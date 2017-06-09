#!/usr/bin/env python3

# Copyright (C) 2013-2017 Jean-Francois Romang (jromang@posteo.de)
#                         Shivkumar Shivaji ()
#                         Jürgen Précour (LocutusOfPenguin@posteo.de)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os

import configargparse
import chess
import chess.polyglot
import chess.uci
import threading
import copy
import gc

from uci.engine import UciEngine
from uci.util import read_engine_ini, get_installed_engines

from timecontrol import TimeControl
from utilities import get_location, update_picochess, get_opening_books, shutdown, reboot, checkout_tag
from utilities import Observable, DisplayMsg, version, evt_queue, write_picochess_ini
import logging
import time
import queue
from dgt.api import Message, Event
from dgt.util import GameResult, TimeMode, Mode, PlayMode
from pgn import Emailer, PgnDisplay
from server import WebServer
from talker.picotalker import PicoTalkerDisplay

from dgt.hw import DgtHw
from dgt.pi import DgtPi
from dgt.display import DgtDisplay
from dgt.board import DgtBoard
from dgt.translate import DgtTranslate
from dgt.menu import DgtMenu
from dispatcher import Dispatcher

from logging.handlers import RotatingFileHandler


class AlternativeMover:
    def __init__(self):
        self.excludemoves = set()

    def all(self, game: chess.Board):
        """Get all remaining legal moves from game position."""
        searchmoves = set(game.legal_moves) - self.excludemoves
        if not searchmoves:
            self.reset()
            return set(game.legal_moves)
        return searchmoves

    def book(self, bookreader, game_copy: chess.Board):
        """Get a BookMove or None from game position."""
        try:
            choice = bookreader.weighted_choice(game_copy, self.excludemoves)
        except IndexError:
            return None

        book_move = choice.move()
        self.add(book_move)
        game_copy.push(book_move)
        try:
            choice = bookreader.weighted_choice(game_copy)
            book_ponder = choice.move()
        except IndexError:
            book_ponder = None
        return chess.uci.BestMove(book_move, book_ponder)

    def add(self, move):
        """Add move to the excluded move list."""
        self.excludemoves.add(move)

    def reset(self):
        """Reset the exclude move list."""
        self.excludemoves = set()


def main():

    def display_ip_info():
        """Fire an IP_INFO message with the IP adr."""
        location, ext_ip, int_ip = get_location()
        info = {'location': location, 'ext_ip': ext_ip, 'int_ip': int_ip, 'version': version}
        DisplayMsg.show(Message.IP_INFO(info=info))

    def expired_fen_timer():
        """Handle times up for an unhandled fen string send from board."""
        nonlocal fen_timer_running
        fen_timer_running = False
        if error_fen:
            logging.info('wrong fen %s for 3secs', error_fen)
            DisplayMsg.show(Message.WRONG_FEN())
            DisplayMsg.show(Message.EXIT_MENU())

    def stop_fen_timer():
        """Stop the fen timer cause another fen string been send."""
        nonlocal fen_timer_running
        nonlocal fen_timer
        if fen_timer_running:
            fen_timer.cancel()
            fen_timer.join()
            fen_timer_running = False

    def start_fen_timer():
        """Start the fen timer in case an unhandled fen string been received from board."""
        nonlocal fen_timer_running
        nonlocal fen_timer
        fen_timer = threading.Timer(3, expired_fen_timer)
        fen_timer.start()
        fen_timer_running = True

    def compute_legal_fens(game_copy: chess.Board):
        """
        Compute a list of legal FENs for the given game.

        :param game_copy: The game
        :return: A list of legal FENs
        """
        fens = []
        for move in game_copy.legal_moves:
            game_copy.push(move)
            fens.append(game_copy.board_fen())
            game_copy.pop()
        return fens

    def think(game: chess.Board, timec: TimeControl, msg: Message):
        """
        Start a new search on the current game.
        If a move is found in the opening book, fire an event in a few seconds.
        """
        start_clock()
        DisplayMsg.show(msg)
        book_res = searchmoves.book(bookreader, game.copy())
        if book_res:
            Observable.fire(Event.BEST_MOVE(move=book_res.bestmove, ponder=book_res.ponder, inbook=True))
        else:
            while not engine.is_waiting():
                time.sleep(0.1)
                logging.warning('engine is still not waiting')
            engine.position(copy.deepcopy(game))
            uci_dict = timec.uci()
            uci_dict['searchmoves'] = searchmoves.all(game)
            engine.go(uci_dict)

    def analyse(game: chess.Board, msg: Message):
        """Start a new ponder search on the current game."""
        engine.position(copy.deepcopy(game))
        engine.ponder()
        DisplayMsg.show(msg)

    def observe(game: chess.Board, msg: Message):
        """Start a new ponder search on the current game."""
        start_clock()
        analyse(game, msg)

    def stop_search_and_clock():
        """depending on the interaction mode stop search and clock."""
        if interaction_mode == Mode.NORMAL:
            stop_clock()
            if not engine.is_waiting():
                stop_search()
        elif interaction_mode in (Mode.REMOTE, Mode.OBSERVE):
            stop_clock()
            stop_search()
        elif interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
            stop_search()

    def stop_search():
        """Stop current search."""
        engine.stop()

    def stop_clock():
        """Stop the clock."""
        if interaction_mode in (Mode.NORMAL, Mode.OBSERVE, Mode.REMOTE):
            time_control.stop()
            DisplayMsg.show(Message.CLOCK_STOP(devs={'ser', 'i2c', 'web'}))
            time.sleep(0.4)  # @todo give some time to clock to really do it. Find a better solution!
        else:
            logging.warning('wrong function call! mode: %s', interaction_mode)

    def start_clock():
        """Start the clock."""
        if interaction_mode in (Mode.NORMAL, Mode.OBSERVE, Mode.REMOTE):
            time_control.start(game.turn)
            tc_init = time_control.get_parameters()
            DisplayMsg.show(Message.CLOCK_START(turn=game.turn, tc_init=tc_init, devs={'ser', 'i2c', 'web'}))
            time.sleep(0.4)  # @todo give some time to clock to really do it. Find a better solution!
        else:
            logging.warning('wrong function call! mode: %s', interaction_mode)

    def check_game_state(game: chess.Board, play_mode: PlayMode):
        """
        Check if the game has ended or not ; it also sends Message to Displays if the game has ended.

        :param game:
        :param play_mode:
        :return: True is the game continues, False if it has ended
        """
        result = None
        if game.is_stalemate():
            result = GameResult.STALEMATE
        if game.is_insufficient_material():
            result = GameResult.INSUFFICIENT_MATERIAL
        if game.is_seventyfive_moves():
            result = GameResult.SEVENTYFIVE_MOVES
        if game.is_fivefold_repetition():
            result = GameResult.FIVEFOLD_REPETITION
        if game.is_checkmate():
            result = GameResult.MATE

        if result is None:
            return True
        else:
            DisplayMsg.show(Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy()))
            return False

    def user_move(move: chess.Move):
        """Handle an user move."""
        nonlocal game
        nonlocal done_move
        nonlocal done_computer_fen

        logging.debug('user move [%s]', move)
        if move not in game.legal_moves:
            logging.warning('illegal move [%s]', move)
        else:
            stop_search_and_clock()

            done_computer_fen = None
            done_move = chess.Move.null()
            fen = game.fen()
            turn = game.turn
            game.push(move)
            searchmoves.reset()
            if interaction_mode == Mode.NORMAL:
                msg = Message.USER_MOVE_DONE(move=move, fen=fen, turn=turn, game=game.copy())
                if check_game_state(game, play_mode):
                    think(game, time_control, msg)
                else:
                    DisplayMsg.show(msg)
            elif interaction_mode == Mode.REMOTE:
                msg = Message.USER_MOVE_DONE(move=move, fen=fen, turn=turn, game=game.copy())
                if check_game_state(game, play_mode):
                    observe(game, msg)
                else:
                    DisplayMsg.show(msg)
            elif interaction_mode == Mode.OBSERVE:
                msg = Message.REVIEW_MOVE_DONE(move=move, fen=fen, turn=turn, game=game.copy())
                if check_game_state(game, play_mode):
                    observe(game, msg)
                else:
                    DisplayMsg.show(msg)
            else:  # interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ):
                msg = Message.REVIEW_MOVE_DONE(move=move, fen=fen, turn=turn, game=game.copy())
                if check_game_state(game, play_mode):
                    analyse(game, msg)
                else:
                    DisplayMsg.show(msg)

    def is_not_user_turn(turn):
        """Return if it is users turn (only valid in normal or remote mode)."""
        condition1 = (play_mode == PlayMode.USER_WHITE and turn == chess.BLACK)
        condition2 = (play_mode == PlayMode.USER_BLACK and turn == chess.WHITE)
        return condition1 or condition2

    def process_fen(fen: str):
        """Process given fen like doMove, undoMove, takebackPosition, handleSliding."""
        nonlocal last_legal_fens
        nonlocal searchmoves
        nonlocal legal_fens
        nonlocal game
        nonlocal done_move
        nonlocal done_computer_fen
        nonlocal error_fen

        handled_fen = True
        # Check for same position
        if fen == game.board_fen():
            logging.debug('Already in this fen: ' + fen)

        # Check if we have to undo a previous move (sliding)
        elif fen in last_legal_fens:
            if interaction_mode == Mode.NORMAL:
                if is_not_user_turn(game.turn):
                    stop_search()
                    game.pop()
                    logging.debug('user move in computer turn, reverting to: ' + game.board_fen())
                elif done_computer_fen:
                    done_computer_fen = None
                    done_move = chess.Move.null()
                    game.pop()
                    logging.debug('user move while computer move is displayed, reverting to: ' + game.board_fen())
                else:
                    handled_fen = False
                    logging.error('last_legal_fens not cleared: ' + game.board_fen())
            elif interaction_mode == Mode.REMOTE:
                if is_not_user_turn(game.turn):
                    game.pop()
                    logging.debug('user move in remote turn, reverting to: ' + game.board_fen())
                elif done_computer_fen:
                    done_computer_fen = None
                    done_move = chess.Move.null()
                    game.pop()
                    logging.debug('user move while remote move is displayed, reverting to: ' + game.board_fen())
                else:
                    handled_fen = False
                    logging.error('last_legal_fens not cleared: ' + game.board_fen())
            else:
                game.pop()
                logging.debug('wrong color move -> sliding, reverting to: ' + game.board_fen())
            legal_moves = list(game.legal_moves)
            move = legal_moves[last_legal_fens.index(fen)]  # type: chess.Move
            user_move(move)
            if interaction_mode in (Mode.NORMAL, Mode.REMOTE):
                legal_fens = []
            else:
                legal_fens = compute_legal_fens(game.copy())

        # legal move
        elif fen in legal_fens:
            time_control.add_inc(game.turn)
            legal_moves = list(game.legal_moves)
            move = legal_moves[legal_fens.index(fen)]  # type: chess.Move
            user_move(move)
            last_legal_fens = legal_fens
            if interaction_mode in (Mode.NORMAL, Mode.REMOTE):
                legal_fens = []
            else:
                legal_fens = compute_legal_fens(game.copy())

        # Player had done the computer or remote move on the board
        elif fen == done_computer_fen:
            assert interaction_mode in (Mode.NORMAL, Mode.REMOTE), 'wrong mode: %s' % interaction_mode
            game.push(done_move)
            done_computer_fen = None
            done_move = chess.Move.null()
            if check_game_state(game, play_mode):
                searchmoves.reset()
                time_control.add_inc(not game.turn)
                if time_control.mode != TimeMode.FIXED:
                    start_clock()
                DisplayMsg.show(Message.COMPUTER_MOVE_DONE())
                legal_fens = compute_legal_fens(game.copy())
            else:
                legal_fens = []
            last_legal_fens = []

        # Check if this is a previous legal position and allow user to restart from this position
        else:
            handled_fen = False
            game_history = copy.deepcopy(game)
            while game_history.move_stack:
                game_history.pop()
                if game_history.board_fen() == fen:
                    handled_fen = True
                    logging.debug('current game fen      : %s', game.fen())
                    logging.debug('undoing game until fen: %s', fen)
                    stop_search_and_clock()
                    while len(game_history.move_stack) < len(game.move_stack):
                        game.pop()
                    done_computer_fen = None
                    done_move = chess.Move.null()
                    last_legal_fens = []
                    msg = Message.TAKE_BACK(game=game.copy())
                    msg_send = False
                    if interaction_mode in (Mode.NORMAL, Mode.REMOTE) and is_not_user_turn(game_history.turn):
                        legal_fens = []
                        if interaction_mode == Mode.NORMAL:
                            searchmoves.reset()
                            if check_game_state(game, play_mode):
                                msg_send = True
                                think(game, time_control, msg)
                    else:
                        legal_fens = compute_legal_fens(game.copy())

                    if interaction_mode == Mode.NORMAL:
                        pass
                    elif interaction_mode in (Mode.OBSERVE, Mode.REMOTE):
                        msg_send = True
                        analyse(game, msg)
                    elif interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
                        msg_send = True
                        analyse(game, msg)
                    if not msg_send:
                        DisplayMsg.show(msg)
                    break
        # doing issue #152
        logging.debug('fen: %s result: %s', fen, handled_fen)
        stop_fen_timer()
        if handled_fen:
            error_fen = None
        else:
            error_fen = fen
            start_fen_timer()

    def set_wait_state(msg: Message, start_search=True):
        """Enter engine waiting (normal mode) and maybe (by parameter) start pondering."""
        if interaction_mode == Mode.NORMAL:
            nonlocal play_mode
            play_mode = PlayMode.USER_WHITE if game.turn == chess.WHITE else PlayMode.USER_BLACK
        if start_search:
            # Go back to analysing or observing
            if interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
                analyse(game, msg)
                return
            if interaction_mode in (Mode.OBSERVE, Mode.REMOTE):
                # observe(game)  # dont want to autostart the clock => we are in newgame situation
                analyse(game, msg)
                return
        DisplayMsg.show(msg)
        stop_fen_timer()

    def transfer_time(time_list: list):
        """Transfer the time list to a TimeControl Object and a Text Object."""
        def _num(time_str):
            try:
                return int(time_str)
            except ValueError:
                return 1

        if len(time_list) == 1:
            fixed = _num(time_list[0])
            timec = TimeControl(TimeMode.FIXED, fixed=fixed)
            textc = dgttranslate.text('B00_tc_fixed', '{:2d}'.format(fixed))
        elif len(time_list) == 2:
            blitz = _num(time_list[0])
            fisch = _num(time_list[1])
            if fisch == 0:
                timec = TimeControl(TimeMode.BLITZ, blitz=blitz)
                textc = dgttranslate.text('B00_tc_blitz', '{:2d}'.format(blitz))
            else:
                timec = TimeControl(TimeMode.FISCHER, blitz=blitz, fischer=fisch)
                textc = dgttranslate.text('B00_tc_fisch', '{:2d} {:2d}'.format(blitz, fisch))
        else:
            timec = TimeControl(TimeMode.BLITZ, blitz=5)
            textc = dgttranslate.text('B00_tc_blitz', ' 5')
        return timec, textc

    def get_engine_level_dict(engine_level):
        """Transfer an engine level to its level_dict plus an index."""
        installed_engines = get_installed_engines(engine.get_shell(), engine.get_file())
        for index in range(0, len(installed_engines)):
            eng = installed_engines[index]
            if eng['file'] == engine.get_file():
                level_list = sorted(eng['level_dict'])
                try:
                    level_index = level_list.index(engine_level)
                    return eng['level_dict'][level_list[level_index]], level_index
                except ValueError:
                    break
        return {}, None

    # Enable garbage collection - needed for engine swapping as objects orphaned
    gc.enable()

    # Command line argument parsing
    parser = configargparse.ArgParser(default_config_files=[os.path.join(os.path.dirname(__file__), 'picochess.ini')])
    parser.add_argument('-e', '--engine', type=str, help="UCI engine executable path such as 'engines/armv7l/a-stockf'",
                        default=None)
    parser.add_argument('-el', '--engine-level', type=str, help='UCI engine level', default=None)
    parser.add_argument('-ers', '--engine-remote-server', type=str, help='adress of the remote engine server')
    parser.add_argument('-eru', '--engine-remote-user', type=str, help='username for the remote engine server')
    parser.add_argument('-erp', '--engine-remote-pass', type=str, help='password for the remote engine server')
    parser.add_argument('-erk', '--engine-remote-key', type=str, help='key file for the remote engine server')
    parser.add_argument('-erh', '--engine-remote-home', type=str, help='engine home path for the remote engine server',
                        default='/opt/picochess')
    parser.add_argument('-d', '--dgt-port', type=str,
                        help='enable dgt board on the given serial port such as /dev/ttyUSB0')
    parser.add_argument('-b', '--book', type=str, help="path of book such as 'books/b-flank.bin'",
                        default='books/h-varied.bin')
    parser.add_argument('-t', '--time', type=str, default='5 0',
                        help="Time settings <FixSec> or <StMin IncSec> like '10'(move) or '5 0'(game) '3 2'(fischer)")
    parser.add_argument('-norl', '--disable-revelation-leds', action='store_true', help='disable Revelation leds')
    parser.add_argument('-l', '--log-level', choices=['notset', 'debug', 'info', 'warning', 'error', 'critical'],
                        default='warning', help='logging level')
    parser.add_argument('-lf', '--log-file', type=str, help='log to the given file')
    parser.add_argument('-pf', '--pgn-file', type=str, help='pgn file used to store the games', default='games.pgn')
    parser.add_argument('-pu', '--pgn-user', type=str, help='user name for the pgn file', default=None)
    parser.add_argument('-w', '--web-server', dest='web_server_port', nargs='?', const=80, type=int, metavar='PORT',
                        help='launch web server')
    parser.add_argument('-m', '--email', type=str, help='email used to send pgn/log files', default=None)
    parser.add_argument('-ms', '--smtp-server', type=str, help='adress of email server', default=None)
    parser.add_argument('-mu', '--smtp-user', type=str, help='username for email server', default=None)
    parser.add_argument('-mp', '--smtp-pass', type=str, help='password for email server', default=None)
    parser.add_argument('-me', '--smtp-encryption', action='store_true',
                        help='use ssl encryption connection to email server')
    parser.add_argument('-mf', '--smtp-from', type=str, help='From email', default='no-reply@picochess.org')
    parser.add_argument('-mk', '--mailgun-key', type=str, help='key used to send emails via Mailgun Webservice',
                        default=None)
    parser.add_argument('-bc', '--beep-config', choices=['none', 'some', 'all'], help='sets standard beep config',
                        default='some')
    parser.add_argument('-bs', '--beep-some-level', type=int, default=0x03,
                        help='sets (some-)beep level from 0(=no beeps) to 15(=all beeps)')
    parser.add_argument('-uv', '--user-voice', type=str, help='voice for user', default='en:mute')
    parser.add_argument('-cv', '--computer-voice', type=str, help='voice for computer', default='en:mute')
    parser.add_argument('-sv', '--speed-voice', type=int, help='voice speech factor from 0(=90%%) to 9(=135%%)',
                        default=2, choices=range(0, 10))
    parser.add_argument('-u', '--enable-update', action='store_true', help='enable picochess updates')
    parser.add_argument('-ur', '--enable-update-reboot', action='store_true', help='reboot system after update')
    parser.add_argument('-nocm', '--disable-confirm-message', action='store_true', help='disable confirmation messages')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s version {}'.format(version),
                        help='show current version', default=None)
    parser.add_argument('-pi', '--dgtpi', action='store_true', help='use the dgtpi hardware')
    parser.add_argument('-pt', '--ponder-interval', type=int, default=3, choices=range(1, 9),
                        help='how long each part of ponder display should be visible (default=3secs)')
    parser.add_argument('-lang', '--language', choices=['en', 'de', 'nl', 'fr', 'es', 'it'], default='en',
                        help='picochess language')
    parser.add_argument('-c', '--console', action='store_true', help='use console interface')
    parser.add_argument('-cl', '--capital-letters', action='store_true', help='clock messages in capital letters')

    args, unknown = parser.parse_known_args()

    engine_file = args.engine
    if engine_file is None:
        eng_ini = read_engine_ini()
        engine_file = eng_ini[0]['file']  # read the first engine filename and use it as standard

    # Enable logging
    if args.log_file:
        handler = RotatingFileHandler('logs' + os.sep + args.log_file, maxBytes=1.4*1024*1024, backupCount=6)
        logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                            format='%(asctime)s.%(msecs)03d %(levelname)7s %(module)10s - %(funcName)s: %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S", handlers=[handler])
    logging.getLogger('chess.uci').setLevel(logging.INFO)  # don't want to get so many python-chess uci messages

    logging.debug('#'*20 + ' PicoChess v%s ' + '#'*20, version)
    # log the startup parameters but hide the password fields
    a_copy = copy.copy(vars(args))
    a_copy['mailgun_key'] = a_copy['smtp_pass'] = a_copy['engine_remote_key'] = a_copy['engine_remote_pass'] = '*****'
    logging.debug('startup parameters: %s', a_copy)
    if unknown:
        logging.warning('invalid parameter given %s', unknown)
    # wire some dgt classes
    dgtboard = DgtBoard(args.dgt_port, args.disable_revelation_leds, args.dgtpi, args.capital_letters)
    dgttranslate = DgtTranslate(args.beep_config, args.beep_some_level, args.language, version)
    dgtmenu = DgtMenu(args.disable_confirm_message, args.ponder_interval, args.speed_voice, dgttranslate)
    dgtdispatcher = Dispatcher(dgtmenu)

    time_control, time_text = transfer_time(args.time.split())
    time_text.beep = False
    # The class dgtDisplay fires Event (Observable) & DispatchDgt (Dispatcher)
    DgtDisplay(dgttranslate, dgtmenu, time_control).start()

    # Create PicoTalker for speech output
    PicoTalkerDisplay(args.user_voice, args.computer_voice, args.speed_voice).start()

    # Launch web server
    if args.web_server_port:
        WebServer(args.web_server_port, dgttranslate, dgtboard).start()
        dgtdispatcher.register('web')

    if args.console:
        logging.debug('starting PicoChess in console mode')
    else:
        # Connect to DGT board
        logging.debug('starting PicoChess in board mode')
        if args.dgtpi:
            DgtPi(dgttranslate, dgtboard).start()
            dgtdispatcher.register('i2c')
        else:
            logging.debug('(ser) starting the board connection')
            dgtboard.run()  # a clock can only be online together with the board, so we must start it infront
        DgtHw(dgttranslate, dgtboard).start()
        dgtdispatcher.register('ser')
    # The class Dispatcher sends DgtApi messages at the correct (delayed) time out
    dgtdispatcher.start()
    # Save to PGN
    emailer = Emailer(email=args.email, mailgun_key=args.mailgun_key)
    emailer.set_smtp(sserver=args.smtp_server, suser=args.smtp_user, spass=args.smtp_pass,
                     sencryption=args.smtp_encryption, sfrom=args.smtp_from)

    PgnDisplay('games' + os.sep + args.pgn_file, emailer).start()
    if args.pgn_user:
        user_name = args.pgn_user
    else:
        if args.email:
            user_name = args.email.split('@')[0]
        else:
            user_name = 'Player'

    # Update
    if args.enable_update:
        update_picochess(args.dgtpi, args.enable_update_reboot, dgttranslate)

    # Gentlemen, start your engines...
    engine = UciEngine(file=engine_file, hostname=args.engine_remote_server, username=args.engine_remote_user,
                       key_file=args.engine_remote_key, password=args.engine_remote_pass, home=args.engine_remote_home)
    try:
        engine_name = engine.get().name
    except AttributeError:
        logging.error('no engines started')
        time.sleep(3)
        DisplayMsg.show(Message.ENGINE_FAIL())
        time.sleep(2)
        sys.exit(-1)

    # Startup - internal
    game = chess.Board()  # Create the current game
    legal_fens = compute_legal_fens(game.copy())  # Compute the legal FENs
    all_books = get_opening_books()
    try:
        book_index = [book['file'] for book in all_books].index(args.book)
    except ValueError:
        logging.warning('selected book not present, defaulting to %s', all_books[7]['file'])
        book_index = 7
    bookreader = chess.polyglot.open_reader(all_books[book_index]['file'])
    searchmoves = AlternativeMover()
    interaction_mode = Mode.NORMAL
    play_mode = PlayMode.USER_WHITE  # @todo make it valid in Mode.REMOTE too!

    last_legal_fens = []
    done_computer_fen = None
    done_move = chess.Move.null()
    game_declared = False  # User declared resignation or draw

    args.engine_level = None if args.engine_level == 'None' else args.engine_level
    engine_opt, level_index = get_engine_level_dict(args.engine_level)
    engine.startup(engine_opt)

    # Startup - external
    if args.engine_level:
        level_text = dgttranslate.text('B00_level', args.engine_level)
        level_text.beep = False
    else:
        level_text = None
    DisplayMsg.show(Message.STARTUP_INFO(info={'interaction_mode': interaction_mode, 'play_mode': play_mode,
                                               'books': all_books, 'book_index': book_index, 'level_text': level_text,
                                               'time_control': time_control, 'time_text': time_text}))
    DisplayMsg.show(Message.ENGINE_STARTUP(shell=engine.get_shell(), file=engine.get_file(), level_index=level_index,
                                           has_levels=engine.has_levels(), has_960=engine.has_chess960()))
    DisplayMsg.show(Message.SYSTEM_INFO(info={'version': version, 'engine_name': engine_name, 'user_name': user_name}))

    ip_info_thread = threading.Timer(10, display_ip_info)  # give RaspberyPi 10sec time to startup its network devices
    ip_info_thread.start()

    fen_timer = threading.Timer(3, expired_fen_timer)
    fen_timer_running = False
    error_fen = None

    # Event loop
    logging.info('evt_queue ready')
    while True:
        try:
            event = evt_queue.get()
        except queue.Empty:
            pass
        else:
            logging.debug('received event from evt_queue: %s', event)
            if False:  # switch-case
                pass
            elif isinstance(event, Event.FEN):
                process_fen(event.fen)

            elif isinstance(event, Event.KEYBOARD_MOVE):
                move = event.move
                logging.debug('keyboard move [%s]', move)
                if move not in game.legal_moves:
                    logging.warning('illegal move. fen: [%s]', game.fen())
                else:
                    game_copy = game.copy()
                    game_copy.push(move)
                    fen = game_copy.board_fen()
                    DisplayMsg.show(Message.DGT_FEN(fen=fen, raw=False))

            elif isinstance(event, Event.LEVEL):
                if event.options:
                    engine.startup(event.options, False)
                DisplayMsg.show(Message.LEVEL(level_text=event.level_text, do_speak=bool(event.options)))
                stop_fen_timer()

            elif isinstance(event, Event.NEW_ENGINE):
                write_picochess_ini('engine', event.eng['file'])
                old_file = engine.get_file()
                engine_shutdown = True
                # Stop the old engine cleanly
                engine.stop()
                # Closeout the engine process and threads
                # The all return non-zero error codes, 0=success
                if engine.quit():  # Ask nicely
                    if engine.terminate():  # If you won't go nicely....
                        if engine.kill():  # Right that does it!
                            logging.error('engine shutdown failure')
                            DisplayMsg.show(Message.ENGINE_FAIL())
                            engine_shutdown = False
                if engine_shutdown:
                    # Load the new one and send args.
                    # Local engines only
                    engine_fallback = False
                    engine = UciEngine(event.eng['file'])
                    try:
                        engine_name = engine.get().name
                    except AttributeError:
                        # New engine failed to start, restart old engine
                        logging.error('new engine failed to start, reverting to %s', old_file)
                        engine_fallback = True
                        event.options = {}  # Reset options. This will load the last(=strongest?) level
                        engine = UciEngine(old_file)
                        try:
                            engine_name = engine.get().name
                        except AttributeError:
                            # Help - old engine failed to restart. There is no engine
                            logging.error('no engines started')
                            DisplayMsg.show(Message.ENGINE_FAIL())
                            time.sleep(3)
                            sys.exit(-1)
                    # Schedule cleanup of old objects
                    gc.collect()
                    engine.startup(event.options)
                    # All done - rock'n'roll
                    if not engine_fallback:
                        msg = Message.ENGINE_READY(eng=event.eng, engine_name=engine_name,
                                                   eng_text=event.eng_text,
                                                   has_levels=engine.has_levels(),
                                                   has_960=engine.has_chess960(), show_ok=event.show_ok)
                    else:
                        msg = Message.ENGINE_FAIL()
                    set_wait_state(msg, not engine_fallback)

            elif isinstance(event, Event.SETUP_POSITION):
                logging.debug('setting up custom fen: %s', event.fen)
                uci960 = event.uci960

                if game.move_stack:
                    if not (game.is_game_over() or game_declared):
                        result = GameResult.ABORT
                        DisplayMsg.show(Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy()))
                game = chess.Board(event.fen, uci960)
                # see new_game
                stop_search_and_clock()
                if engine.has_chess960():
                    engine.option('UCI_Chess960', uci960)
                    engine.send()
                legal_fens = compute_legal_fens(game.copy())
                last_legal_fens = []
                done_computer_fen = None
                done_move = chess.Move.null()
                time_control.reset()
                searchmoves.reset()
                game_declared = False
                set_wait_state(Message.START_NEW_GAME(game=game.copy(), newgame=True))

            elif isinstance(event, Event.NEW_GAME):
                newgame = game.move_stack or (game.chess960_pos() != event.pos960)
                if newgame:
                    logging.debug('starting a new game with code: %s', event.pos960)
                    uci960 = event.pos960 != 518

                    if not (game.is_game_over() or game_declared):
                        result = GameResult.ABORT
                        DisplayMsg.show(Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy()))

                    game = chess.Board()
                    if uci960:
                        game.set_chess960_pos(event.pos960)
                    # see setup_position
                    stop_search_and_clock()
                    if engine.has_chess960():
                        engine.option('UCI_Chess960', uci960)
                        engine.send()
                    legal_fens = compute_legal_fens(game.copy())
                    last_legal_fens = []
                    done_computer_fen = None
                    done_move = chess.Move.null()
                    time_control.reset()
                    searchmoves.reset()
                    game_declared = False
                    set_wait_state(Message.START_NEW_GAME(game=game.copy(), newgame=newgame))
                else:
                    logging.debug('no need to start a new game')
                    DisplayMsg.show(Message.START_NEW_GAME(game=game.copy(), newgame=newgame))

            elif isinstance(event, Event.PAUSE_RESUME):
                if engine.is_thinking():
                    stop_clock()
                    engine.stop(show_best=True)
                else:
                    if time_control.is_ticking():
                        stop_clock()
                    else:
                        start_clock()

            elif isinstance(event, Event.ALTERNATIVE_MOVE):
                if done_computer_fen:
                    done_computer_fen = None
                    done_move = chess.Move.null()
                    think(game, time_control, Message.ALTERNATIVE_MOVE(game=game.copy()))

            elif isinstance(event, Event.SWITCH_SIDES):
                if interaction_mode == Mode.NORMAL:
                    user_to_move = False
                    last_legal_fens = []

                    if engine.is_thinking():
                        stop_clock()
                        engine.stop(show_best=False)
                        user_to_move = True
                    if event.engine_finished:
                        move = done_move if done_computer_fen else game.pop()
                        done_computer_fen = None
                        done_move = chess.Move.null()
                        user_to_move = True
                    else:
                        move = chess.Move.null()
                    if user_to_move:
                        last_legal_fens = []
                        play_mode = PlayMode.USER_WHITE if game.turn == chess.WHITE else PlayMode.USER_BLACK
                    else:
                        play_mode = PlayMode.USER_WHITE if game.turn == chess.BLACK else PlayMode.USER_BLACK

                    text = play_mode.value  # type: str
                    msg = Message.PLAY_MODE(play_mode=play_mode, play_mode_text=dgttranslate.text(text))

                    if not user_to_move and check_game_state(game, play_mode):
                        time_control.reset_start_time()
                        think(game, time_control, msg)
                        legal_fens = []
                    else:
                        start_clock()
                        DisplayMsg.show(msg)
                        legal_fens = compute_legal_fens(game.copy())

                    if event.engine_finished:
                        DisplayMsg.show(Message.SWITCH_SIDES(game=game.copy(), move=move))

            elif isinstance(event, Event.DRAWRESIGN):
                if not game_declared:  # in case user leaves kings in place while moving other pieces
                    stop_search_and_clock()
                    DisplayMsg.show(Message.GAME_ENDS(result=event.result, play_mode=play_mode, game=game.copy()))
                    game_declared = True
                    stop_fen_timer()

            elif isinstance(event, Event.REMOTE_MOVE):
                if interaction_mode == Mode.REMOTE and is_not_user_turn(game.turn):
                    stop_search_and_clock()
                    move = chess.Move.from_uci(event.uci_move)
                    DisplayMsg.show(Message.COMPUTER_MOVE(move=move, game=game.copy(), wait=False))
                    game_copy = game.copy()
                    game_copy.push(event.move)
                    done_computer_fen = game.board_fen()
                    done_move = event.move
                else:
                    logging.warning('wrong function call! mode: %s turn: %s', interaction_mode, game.turn)

            elif isinstance(event, Event.BEST_MOVE):
                if interaction_mode == Mode.NORMAL and is_not_user_turn(game.turn):
                    # clock must be stopped BEFORE the "book_move" event cause SetNRun resets the clock display
                    stop_clock()
                    if event.inbook:
                        DisplayMsg.show(Message.BOOK_MOVE())
                    searchmoves.add(event.move)
                    DisplayMsg.show(Message.COMPUTER_MOVE(move=event.move, ponder=event.ponder, game=game.copy(),
                                                          wait=event.inbook))
                    game_copy = game.copy()
                    game_copy.push(event.move)
                    done_computer_fen = game_copy.board_fen()
                    done_move = event.move
                else:
                    logging.warning('wrong function call! mode: %s turn: %s', interaction_mode, game.turn)

            elif isinstance(event, Event.NEW_PV):
                # illegal moves can occur if a pv from the engine arrives at the same time as a user move.
                if game.is_legal(event.pv[0]):
                    DisplayMsg.show(Message.NEW_PV(pv=event.pv, mode=interaction_mode, game=game.copy()))
                else:
                    logging.info('illegal move can not be displayed. move: %s fen: %s', event.pv[0], game.fen())

            elif isinstance(event, Event.NEW_SCORE):
                DisplayMsg.show(Message.NEW_SCORE(score=event.score, mate=event.mate, mode=interaction_mode,
                                                  turn=game.turn))

            elif isinstance(event, Event.NEW_DEPTH):
                DisplayMsg.show(Message.NEW_DEPTH(depth=event.depth))

            elif isinstance(event, Event.START_SEARCH):
                DisplayMsg.show(Message.SEARCH_STARTED(engine_status=event.engine_status))

            elif isinstance(event, Event.STOP_SEARCH):
                DisplayMsg.show(Message.SEARCH_STOPPED(engine_status=event.engine_status))

            elif isinstance(event, Event.SET_INTERACTION_MODE):
                if event.mode not in (Mode.NORMAL, Mode.REMOTE) and done_computer_fen:
                    event.mode = interaction_mode  # @todo display an error message at clock
                    logging.warning('mode cant be changed to a pondering mode as long as a move is displayed')

                if interaction_mode in (Mode.NORMAL, Mode.OBSERVE, Mode.REMOTE):
                    stop_clock()
                interaction_mode = event.mode
                if engine.is_thinking():
                    stop_search()
                if engine.is_pondering():
                    stop_search()
                msg = Message.INTERACTION_MODE(mode=event.mode, mode_text=event.mode_text, show_ok=event.show_ok)
                set_wait_state(msg)

            elif isinstance(event, Event.SET_OPENING_BOOK):
                write_picochess_ini('book', event.book['file'])
                logging.debug('changing opening book [%s]', event.book['file'])
                bookreader = chess.polyglot.open_reader(event.book['file'])
                DisplayMsg.show(Message.OPENING_BOOK(book_text=event.book_text, show_ok=event.show_ok))
                stop_fen_timer()

            elif isinstance(event, Event.SET_TIME_CONTROL):
                time_control.stop(log=False)
                time_control = TimeControl(**event.tc_init)
                tc_init = time_control.get_parameters()
                if time_control.mode == TimeMode.BLITZ:
                    write_picochess_ini('time', '{:d} 0'.format(tc_init['blitz']))
                elif time_control.mode == TimeMode.FISCHER:
                    write_picochess_ini('time', '{:d} {:d}'.format(tc_init['blitz'], tc_init['fischer']))
                elif time_control.mode == TimeMode.FIXED:
                    write_picochess_ini('time', '{:d}'.format(tc_init['fixed']))
                text = Message.TIME_CONTROL(time_text=event.time_text, show_ok=event.show_ok, tc_init=tc_init)
                DisplayMsg.show(text)
                stop_fen_timer()

            elif isinstance(event, Event.OUT_OF_TIME):
                stop_search_and_clock()
                result = GameResult.OUT_OF_TIME
                DisplayMsg.show(Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy()))

            elif isinstance(event, Event.SHUTDOWN):
                result = GameResult.ABORT
                DisplayMsg.show(Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy()))
                DisplayMsg.show(Message.SYSTEM_SHUTDOWN())
                shutdown(args.dgtpi, dev=event.dev)

            elif isinstance(event, Event.REBOOT):
                result = GameResult.ABORT
                DisplayMsg.show(Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy()))
                DisplayMsg.show(Message.SYSTEM_REBOOT())
                reboot(args.dgtpi, dev=event.dev)

            elif isinstance(event, Event.EMAIL_LOG):
                if args.log_file:
                    email_logger = Emailer(email=args.email, mailgun_key=args.mailgun_key)
                    email_logger.set_smtp(sserver=args.smtp_server, suser=args.smtp_user, spass=args.smtp_pass,
                                          sencryption=args.smtp_encryption, sfrom=args.smtp_from)
                    body = 'You probably want to forward this file to a picochess developer ;-)'
                    email_logger.send('Picochess LOG', body, '/opt/picochess/logs/{}'.format(args.log_file))

            elif isinstance(event, Event.SET_VOICE):
                DisplayMsg.show(Message.SET_VOICE(type=event.type, lang=event.lang, speaker=event.speaker,
                                                  speed=event.speed))

            elif isinstance(event, Event.KEYBOARD_BUTTON):
                DisplayMsg.show(Message.DGT_BUTTON(button=event.button, dev=event.dev))

            elif isinstance(event, Event.KEYBOARD_FEN):
                DisplayMsg.show(Message.DGT_FEN(fen=event.fen, raw=False))

            elif isinstance(event, Event.EXIT_MENU):
                DisplayMsg.show(Message.EXIT_MENU())

            elif isinstance(event, Event.UPDATE_PICO):
                DisplayMsg.show(Message.UPDATE_PICO())
                checkout_tag(event.tag)
                DisplayMsg.show(Message.EXIT_MENU())

            else:  # Default
                logging.warning('event not handled : [%s]', event)

            evt_queue.task_done()


if __name__ == '__main__':
    main()
