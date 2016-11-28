#!/usr/bin/env python3

# Copyright (C) 2013-2016 Jean-Francois Romang (jromang@posteo.de)
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
import chess.gaviota
import chess.uci
import threading
import copy
import gc

from engine import UciEngine, read_engine_ini

from timecontrol import TimeControl
from utilities import *
from keyboard import KeyboardInput, TerminalDisplay
from pgn import Emailer, PgnDisplay
from server import WebServer

from dgthw import DgtHw
from dgtpi import DgtPi
from dgtvr import DgtVr
from dgtdisplay import DgtDisplay
# from dgtserial import DgtSerial
from dgtboard import DgtBoard
from dgttranslate import DgtTranslate

from logging.handlers import RotatingFileHandler
from configobj import ConfigObj


class AlternativeMover:
    def __init__(self):
        self.excludemoves = set()

    def all(self, game):
        searchmoves = set(game.legal_moves) - self.excludemoves
        if not searchmoves:
            self.reset()
            return set(game.legal_moves)
        return searchmoves

    def book(self, bookreader, game):
        try:
            bm = bookreader.weighted_choice(game, self.excludemoves)
        except IndexError:
            return None

        book_move = bm.move()
        self.add(book_move)
        g = copy.deepcopy(game)
        g.push(book_move)
        try:
            bp = bookreader.weighted_choice(g)
            book_ponder = bp.move()
        except IndexError:
            book_ponder = None
        return chess.uci.BestMove(book_move, book_ponder)

    def add(self, move):
        self.excludemoves.add(move)

    def reset(self):
        self.excludemoves = set()


def main():

    def display_system_info():
        location, ip = get_location()
        DisplayMsg.show(Message.SYSTEM_INFO(info={'version': version, 'location': location, 'ip': ip,
                                                  'engine_name': engine_name, 'user_name': user_name
                                                  }))

    def compute_legal_fens(g):
        """
        Compute a list of legal FENs for the given game.
        :param g: The game
        :return: A list of legal FENs
        """
        fens = []
        for move in g.legal_moves:
            g.push(move)
            fens.append(g.board_fen())
            g.pop()
        return fens

    def probe_tablebase(game):
        if not gaviota:
            return None
        score = gaviota.probe_dtm(game)
        if score is not None:
            Observable.fire(Event.NEW_SCORE(score='gaviota', mate=score))
        return score

    def think(game, tc):
        """
        Start a new search on the current game.
        If a move is found in the opening book, fire an event in a few seconds.
        :return:
        """
        start_clock()
        book_move = searchmoves.book(bookreader, game)
        if book_move:
            Observable.fire(Event.BEST_MOVE(result=book_move, inbook=True))
        else:
            probe_tablebase(game)
            while not engine.is_waiting():
                time.sleep(0.1)
                logging.warning('engine is still not waiting')
            engine.position(copy.deepcopy(game))
            uci_dict = tc.uci()
            uci_dict['searchmoves'] = searchmoves.all(game)
            engine.go(uci_dict)

    def analyse(game):
        """
        Start a new ponder search on the current game.
        :return:
        """
        probe_tablebase(game)
        engine.position(copy.deepcopy(game))
        engine.ponder()

    def observe(game):
        """
        Starts a new ponder search on the current game.
        :return:
        """
        start_clock()
        analyse(game)

    def stop_search_and_clock():
        if interaction_mode == Mode.NORMAL:
            stop_clock()
        elif interaction_mode in (Mode.REMOTE, Mode.OBSERVE):
            stop_clock()
            stop_search()
        elif interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
            stop_search()

    def stop_search():
        """
        Stop current search.
        :return:
        """
        engine.stop()

    def stop_clock():
        if interaction_mode in (Mode.NORMAL, Mode.OBSERVE, Mode.REMOTE):
            time_control.stop()
            DisplayMsg.show(Message.CLOCK_STOP())
        else:
            logging.warning('wrong mode: {}'.format(interaction_mode))

    def start_clock():
        if interaction_mode in (Mode.NORMAL, Mode.OBSERVE, Mode.REMOTE):
            time_control.start(game.turn)
            DisplayMsg.show(Message.CLOCK_START(turn=game.turn, time_control=time_control))
        else:
            logging.warning('wrong mode: {}'.format(interaction_mode))

    def check_game_state(game, play_mode):
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

    def user_move(move):
        logging.debug('user move [%s]', move)
        if move not in game.legal_moves:
            logging.warning('Illegal move [%s]', move)
        else:
            handle_move(move=move)

    def process_fen(fen):
        nonlocal last_computer_fen
        nonlocal last_legal_fens
        nonlocal searchmoves
        nonlocal legal_fens

        # Check for same position
        if (fen == game.board_fen() and not last_computer_fen) or fen == last_computer_fen:
            logging.debug('Already in this fen: ' + fen)

        # Check if we have to undo a previous move (sliding)
        elif fen in last_legal_fens:
            if interaction_mode == Mode.NORMAL:
                if (play_mode == PlayMode.USER_WHITE and game.turn == chess.BLACK) or \
                        (play_mode == PlayMode.USER_BLACK and game.turn == chess.WHITE):
                    stop_search()
                    game.pop()
                    logging.debug('User move in computer turn, reverting to: ' + game.board_fen())
                elif last_computer_fen:
                    last_computer_fen = None
                    game.pop()
                    game.pop()
                    logging.debug('User move while computer move is displayed, reverting to: ' + game.board_fen())
                else:
                    logging.error("last_legal_fens not cleared: " + game.board_fen())
            elif interaction_mode == Mode.REMOTE:
                if (play_mode == PlayMode.USER_WHITE and game.turn == chess.BLACK) or \
                        (play_mode == PlayMode.USER_BLACK and game.turn == chess.WHITE):
                    game.pop()
                    logging.debug('User move in remote turn, reverting to: ' + game.board_fen())
                elif last_computer_fen:
                    last_computer_fen = None
                    game.pop()
                    game.pop()
                    logging.debug('User move while remote move is displayed, reverting to: ' + game.board_fen())
                else:
                    logging.error('last_legal_fens not cleared: ' + game.board_fen())
            else:
                game.pop()
                logging.debug('Wrong color move -> sliding, reverting to: ' + game.board_fen())
            legal_moves = list(game.legal_moves)
            user_move(legal_moves[last_legal_fens.index(fen)])
            if interaction_mode == Mode.NORMAL or interaction_mode == Mode.REMOTE:
                legal_fens = []
            else:
                legal_fens = compute_legal_fens(game)

        # legal move
        elif fen in legal_fens:
            time_control.add_inc(game.turn)
            legal_moves = list(game.legal_moves)
            user_move(legal_moves[legal_fens.index(fen)])
            last_legal_fens = legal_fens
            if interaction_mode == Mode.NORMAL or interaction_mode == Mode.REMOTE:
                legal_fens = []
            else:
                legal_fens = compute_legal_fens(game)

        # Player had done the computer or remote move on the board
        elif last_computer_fen and fen == game.board_fen():
            last_computer_fen = None
            if check_game_state(game, play_mode) and interaction_mode in (Mode.NORMAL, Mode.REMOTE):
                # finally reset all alternative moves see: handle_move()
                nonlocal searchmoves
                searchmoves.reset()
                time_control.add_inc(not game.turn)
                if time_control.mode != TimeMode.FIXED:
                    start_clock()
                DisplayMsg.show(Message.COMPUTER_MOVE_DONE_ON_BOARD())
                legal_fens = compute_legal_fens(game)
            else:
                legal_fens = []
            last_legal_fens = []

        # Check if this is a previous legal position and allow user to restart from this position
        else:
            game_history = copy.deepcopy(game)
            if last_computer_fen:
                game_history.pop()
            while game_history.move_stack:
                game_history.pop()
                if game_history.board_fen() == fen:
                    logging.debug("Current game FEN      : {}".format(game.fen()))
                    logging.debug("Undoing game until FEN: {}".format(fen))
                    stop_search_and_clock()
                    while len(game_history.move_stack) < len(game.move_stack):
                        game.pop()
                    last_computer_fen = None
                    last_legal_fens = []
                    if (interaction_mode == Mode.REMOTE or interaction_mode == Mode.NORMAL) and \
                            ((play_mode == PlayMode.USER_WHITE and game_history.turn == chess.BLACK)
                              or (play_mode == PlayMode.USER_BLACK and game_history.turn == chess.WHITE)):
                        legal_fens = []
                        if interaction_mode == Mode.NORMAL:
                            searchmoves.reset()
                            if check_game_state(game, play_mode):
                                think(game, time_control)
                    else:
                        legal_fens = compute_legal_fens(game)

                    if interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
                        analyse(game)
                    elif interaction_mode in (Mode.OBSERVE, Mode.REMOTE):
                        observe(game)
                    start_clock()
                    DisplayMsg.show(Message.USER_TAKE_BACK())
                    break

    def set_wait_state(start_search=True):
        if interaction_mode == Mode.NORMAL:
            nonlocal play_mode
            play_mode = PlayMode.USER_WHITE if game.turn == chess.WHITE else PlayMode.USER_BLACK
        if start_search:
            # Go back to analysing or observing
            if interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
                analyse(game)
            if interaction_mode in (Mode.OBSERVE, Mode.REMOTE):
                observe(game)

    def handle_move(move, ponder=None, inbook=False):
        nonlocal game
        nonlocal last_computer_fen
        nonlocal searchmoves
        fen = game.fen()
        turn = game.turn

        # clock must be stoped BEFORE the "book_move" event cause SetNRun resets the clock display
        stop_search_and_clock()

        # engine or remote move
        if (interaction_mode == Mode.NORMAL or interaction_mode == Mode.REMOTE) and \
                ((play_mode == PlayMode.USER_WHITE and turn == chess.BLACK) or
                     (play_mode == PlayMode.USER_BLACK and turn == chess.WHITE)):
            last_computer_fen = game.board_fen()
            game.push(move)
            if inbook:
                DisplayMsg.show(Message.BOOK_MOVE())
            searchmoves.add(move)
            text = Message.COMPUTER_MOVE(move=move, ponder=ponder, fen=fen, turn=turn, game=game.copy(),
                                         time_control=time_control, wait=inbook)
            DisplayMsg.show(text)
        else:
            last_computer_fen = None
            game.push(move)
            if inbook:
                DisplayMsg.show(Message.BOOK_MOVE())
            searchmoves.reset()
            if interaction_mode == Mode.NORMAL:
                if check_game_state(game, play_mode):
                    think(game, time_control)
                text = Message.USER_MOVE(move=move, fen=fen, turn=turn, game=game.copy())
            elif interaction_mode == Mode.REMOTE:
                if check_game_state(game, play_mode):
                    observe(game)
                text = Message.USER_MOVE(move=move, fen=fen, turn=turn, game=game.copy())
            elif interaction_mode == Mode.OBSERVE:
                if check_game_state(game, play_mode):
                    observe(game)
                text = Message.REVIEW_MOVE(move=move, fen=fen, turn=turn, game=game.copy(), mode=interaction_mode)
            else:  # interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ):
                if check_game_state(game, play_mode):
                    analyse(game)
                text = Message.REVIEW_MOVE(move=move, fen=fen, turn=turn, game=game.copy(), mode=interaction_mode)
            DisplayMsg.show(text)

    def transfer_time(time_list):
        def num(ts):
            try:
                return int(ts)
            except ValueError:
                return 1

        if len(time_list) == 1:
            secs = num(time_list[0])
            time_control = TimeControl(TimeMode.FIXED, seconds_per_move=secs)
            text = dgttranslate.text('B00_tc_fixed', '{:2d}'.format(secs))
        elif len(time_list) == 2:
            mins = num(time_list[0])
            finc = num(time_list[1])
            if finc == 0:
                time_control = TimeControl(TimeMode.BLITZ, minutes_per_game=mins)
                text = dgttranslate.text('B00_tc_blitz', '{:2d}'.format(mins))
            else:
                time_control = TimeControl(TimeMode.FISCHER, minutes_per_game=mins, fischer_increment=finc)
                text = dgttranslate.text('B00_tc_fisch', '{:2d} {:2d}'.format(mins, finc))
        else:
            time_control = TimeControl(TimeMode.BLITZ, minutes_per_game=5)
            text = dgttranslate.text('B00_tc_blitz', ' 5')
        return time_control, text

    def get_engine_level_dict(engine_level):
        from engine import get_installed_engines

        installed_engines = get_installed_engines(engine.get_shell(), engine.get_file())
        for index in range(0, len(installed_engines)):
            eng = installed_engines[index]
            if eng['file'] == engine.get_file():
                level_list = sorted(eng['level_dict'])
                try:
                    level_index = level_list.index(engine_level)
                    return eng['level_dict'][level_list[level_index]]
                except ValueError:
                    break
        return {}

    # Enable garbage collection - needed for engine swapping as objects orphaned
    gc.enable()

    # Command line argument parsing
    parser = configargparse.ArgParser(default_config_files=[os.path.join(os.path.dirname(__file__), 'picochess.ini')])
    parser.add_argument('-e', '--engine', type=str, help='UCI engine executable path', default=None)
    parser.add_argument('-el', '--engine-level', type=str, help='UCI engine level', default=None)
    parser.add_argument('-d', '--dgt-port', type=str,
                        help='enable dgt board on the given serial port such as /dev/ttyUSB0')
    parser.add_argument('-b', '--book', type=str, help='full path of book such as books/b-flank.bin',
                        default='books/h-varied.bin')
    parser.add_argument('-t', '--time', type=str, default='5 0',
                        help="Time settings <FixSec> or <StMin IncSec> like '10'(move) or '5 0'(game) '3 2'(fischer)")
    parser.add_argument('-g', '--enable-gaviota', action='store_true', help='enable gavoita tablebase probing')
    parser.add_argument('-leds', '--enable-revelation-leds', action='store_true', help='enable Revelation leds')
    parser.add_argument('-l', '--log-level', choices=['notset', 'debug', 'info', 'warning', 'error', 'critical'],
                        default='warning', help='logging level')
    parser.add_argument('-lf', '--log-file', type=str, help='log to the given file')
    parser.add_argument('-rs', '--remote-server', type=str, help='remote server running the engine')
    parser.add_argument('-ru', '--remote-user', type=str, help='remote user on server running the engine')
    parser.add_argument('-rp', '--remote-pass', type=str, help='password for the remote user')
    parser.add_argument('-rk', '--remote-key', type=str, help='key file used to connect to the remote server')
    parser.add_argument('-pf', '--pgn-file', type=str, help='pgn file used to store the games', default='games.pgn')
    parser.add_argument('-pu', '--pgn-user', type=str, help='user name for the pgn file', default=None)
    parser.add_argument('-web', '--web-server', dest='web_server_port', nargs='?', const=80, type=int, metavar='PORT',
                        help='launch web server')
    parser.add_argument('-m', '--email', type=str, help='email used to send pgn/log files', default=None)
    parser.add_argument('-ms', '--smtp-server', type=str, help='adress of email server', default=None)
    parser.add_argument('-mu', '--smtp-user', type=str, help='username for email server', default=None)
    parser.add_argument('-mp', '--smtp-pass', type=str, help='password for email server', default=None)
    parser.add_argument('-me', '--smtp-encryption', action='store_true',
                        help='use ssl encryption connection to smtp-Server')
    parser.add_argument('-mf', '--smtp-from', type=str, help='From email', default='no-reply@picochess.org')
    parser.add_argument('-mk', '--mailgun-key', type=str, help='key used to send emails via Mailgun Webservice',
                        default=None)
    parser.add_argument('-bc', '--beep-config', choices=['none', 'some', 'all'], help='sets standard beep config',
                        default='some')
    parser.add_argument('-beep', '--beep-level', type=int, default=0x03,
                        help='sets (some-)beep level from 0(=no beeps) to 15(=all beeps)')
    parser.add_argument('-uvoice', '--user-voice', type=str, help='voice for user', default=None)
    parser.add_argument('-cvoice', '--computer-voice', type=str, help='voice for computer', default=None)
    parser.add_argument('-inet', '--enable-internet', action='store_true', help='DEPRECATED - dont use it anymore!')
    parser.add_argument('-update', '--enable-update', action='store_true', help='enable picochess updates')
    parser.add_argument('-ar', '--auto-reboot', action='store_true', help='reboot system after update')
    parser.add_argument('-nook', '--disable-ok-message', action='store_true', help='disable ok confirmation messages')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s version {}'.format(version),
                        help='show current version', default=None)
    parser.add_argument('-pi', '--dgtpi', action='store_true', help='use the dgtpi hardware')
    parser.add_argument('-lang', '--language', choices=['en', 'de', 'nl', 'fr', 'es', 'it'], default='en',
                        help='picochess language')
    parser.add_argument('-c', '--console', action='store_true', help='use console interface')

    args = parser.parse_args()
    if args.engine is None:
        el = read_engine_ini()
        args.engine = el[0]['file']  # read the first engine filename and use it as standard

    # Enable logging
    if args.log_file:
        handler = RotatingFileHandler('logs' + os.sep + args.log_file, maxBytes=1024*1024, backupCount=9)
        logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                            format='%(asctime)s.%(msecs)03d %(levelname)5s %(module)10s - %(funcName)s: %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S", handlers=[handler])
    logging.getLogger('chess.uci').setLevel(logging.INFO)  # don't want to get so many python-chess uci messages

    logging.debug('#'*20 + ' PicoChess v' + version + ' ' + '#'*20)
    # log the startup parameters but hide the password fields
    p = copy.copy(vars(args))
    p['mailgun_key'] = p['remote_key'] = p['remote_pass'] = p['smtp_pass'] = '*****'
    logging.debug('startup parameters: {}'.format(p))

    # Update
    if args.enable_update:
        update_picochess(args.auto_reboot)

    gaviota = None
    if args.enable_gaviota:
        try:
            gaviota = chess.gaviota.open_tablebases('tablebases/gaviota')
            logging.debug('Tablebases gaviota loaded')
        except OSError:
            logging.error('Tablebases gaviota doesnt exist')
            gaviota = None

    # The class dgtDisplay talks to DgtHw/DgtPi or DgtVr
    dgttranslate = DgtTranslate(args.beep_config, args.beep_level, args.language)
    DgtDisplay(args.disable_ok_message, dgttranslate).start()

    # Launch web server
    if args.web_server_port:
        WebServer(args.web_server_port).start()

    dgtboard = DgtBoard(args.dgt_port, args.enable_revelation_leds, args.dgtpi)

    if args.console:
        # Enable keyboard input and terminal display
        logging.debug('starting picochess in virtual mode')
        KeyboardInput(dgttranslate, args.dgtpi).start()
        TerminalDisplay().start()
        DgtVr(dgttranslate, dgtboard).start()
    else:
        # Connect to DGT board
        logging.debug('starting picochess in board mode')
        if args.dgtpi:
            DgtPi(dgttranslate).start()
        DgtHw(dgttranslate, dgtboard).start()
    # Save to PGN
    emailer = Emailer(
        email=args.email, mailgun_key=args.mailgun_key,
        smtp_server=args.smtp_server, smtp_user=args.smtp_user,
        smtp_pass=args.smtp_pass, smtp_encryption=args.smtp_encryption, smtp_from=args.smtp_from)

    PgnDisplay(args.pgn_file, emailer).start()
    if args.pgn_user:
        user_name = args.pgn_user
    else:
        if args.email:
            user_name = args.email.split('@')[0]
        else:
            user_name = 'Player'

    # Create PicoTalker for speech output
    if args.user_voice or args.computer_voice:
        from talker.picotalker import PicoTalkerDisplay
        logging.debug("initializing PicoTalker [%s, %s]", str(args.user_voice), str(args.computer_voice))
        PicoTalkerDisplay(args.user_voice, args.computer_voice).start()
    else:
        logging.debug('PicoTalker disabled')

    # Gentlemen, start your engines...
    engine = UciEngine(args.engine, hostname=args.remote_server, username=args.remote_user,
                       key_file=args.remote_key, password=args.remote_pass)
    try:
        engine_name = engine.get().name
    except AttributeError:
        logging.error('no engines started')
        DisplayMsg.show(Message.ENGINE_FAIL())
        time.sleep(3)
        sys.exit(-1)

    # Startup - internal
    game = chess.Board()  # Create the current game
    legal_fens = compute_legal_fens(game)  # Compute the legal FENs
    all_books = get_opening_books()
    try:
        book_index = [book['file'] for book in all_books].index(args.book)
    except ValueError:
        logging.warning("selected book not present, defaulting to %s", all_books[7]['file'])
        book_index = 7
    bookreader = chess.polyglot.open_reader(all_books[book_index]['file'])
    searchmoves = AlternativeMover()
    interaction_mode = Mode.NORMAL
    play_mode = PlayMode.USER_WHITE

    last_computer_fen = None
    last_legal_fens = []
    game_declared = False  # User declared resignation or draw

    engine.startup(get_engine_level_dict(args.engine_level))

    # Startup - external
    time_control, time_text = transfer_time(args.time.split())
    time_text.beep = False
    if args.engine_level:
        level_text = dgttranslate.text('B00_level', args.engine_level)
        level_text.beep = False
    else:
        level_text = None
    DisplayMsg.show(Message.STARTUP_INFO(info={'interaction_mode': interaction_mode, 'play_mode': play_mode,
                                               'books': all_books, 'book_index': book_index, 'level_text': level_text,
                                               'time_control': time_control, 'time_text': time_text}))
    DisplayMsg.show(Message.ENGINE_STARTUP(shell=engine.get_shell(), file=engine.get_file(),
                                           has_levels=engine.has_levels(), has_960=engine.has_chess960()))

    system_info_thread = threading.Timer(0, display_system_info)
    system_info_thread.start()

    # Event loop
    logging.info('evt_queue ready')
    while True:
        try:
            event = evt_queue.get()
        except queue.Empty:
            pass
        else:
            logging.debug('received event from evt_queue: %s', event)
            for case in switch(event):
                if case(EventApi.FEN):
                    process_fen(event.fen)
                    break

                if case(EventApi.KEYBOARD_MOVE):
                    move = event.move
                    logging.debug('keyboard move [%s]', move)
                    if move not in game.legal_moves:
                        logging.warning('illegal move [%s]', move)
                    else:
                        g = copy.deepcopy(game)
                        g.push(move)
                        fen = g.fen().split(' ')[0]
                        if event.flip_board:
                            fen = fen[::-1]
                        DisplayMsg.show(Message.KEYBOARD_MOVE(fen=fen))
                    break

                if case(EventApi.LEVEL):
                    if event.options:
                        engine.startup(event.options, False)
                    DisplayMsg.show(Message.LEVEL(level_text=event.level_text))
                    break

                if case(EventApi.NEW_ENGINE):
                    config = ConfigObj('picochess.ini')
                    config['engine'] = event.eng['file']
                    config.write()
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
                            logging.error("new engine failed to start, reverting to %s", old_file)
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
                            DisplayMsg.show(Message.ENGINE_READY(eng=event.eng, engine_name=engine_name,
                                                                 eng_text=event.eng_text,
                                                                 has_levels=engine.has_levels(),
                                                                 has_960=engine.has_chess960(), ok_text=event.ok_text))
                        else:
                            DisplayMsg.show(Message.ENGINE_FAIL())
                        set_wait_state(not engine_fallback)
                    break

                if case(EventApi.SETUP_POSITION):
                    logging.debug("setting up custom fen: {}".format(event.fen))
                    uci960 = event.uci960

                    if game.move_stack:
                        if not (game.is_game_over() or game_declared):
                            DisplayMsg.show(Message.GAME_ENDS(result=GameResult.ABORT, play_mode=play_mode, game=game.copy()))
                    game = chess.Board(event.fen, uci960)
                    # see new_game
                    stop_search_and_clock()
                    if engine.has_chess960():
                        engine.option('UCI_Chess960', uci960)
                        engine.send()
                    legal_fens = compute_legal_fens(game)
                    last_legal_fens = []
                    last_computer_fen = None
                    time_control.reset()
                    searchmoves.reset()
                    DisplayMsg.show(Message.START_NEW_GAME(time_control=time_control, game=game.copy()))
                    game_declared = False
                    set_wait_state()
                    break

                if case(EventApi.NEW_GAME):
                    logging.debug('starting a new game with code: {}'.format(event.pos960))
                    uci960 = event.pos960 != 518

                    if game.move_stack:
                        if not (game.is_game_over() or game_declared):
                            DisplayMsg.show(Message.GAME_ENDS(result=GameResult.ABORT, play_mode=play_mode, game=game.copy()))
                    game = chess.Board()
                    if uci960:
                        game.set_chess960_pos(event.pos960)
                    # see setup_position
                    stop_search_and_clock()
                    if engine.has_chess960():
                        engine.option('UCI_Chess960', uci960)
                        engine.send()
                    legal_fens = compute_legal_fens(game)
                    last_legal_fens = []
                    last_computer_fen = None
                    time_control.reset()
                    searchmoves.reset()
                    DisplayMsg.show(Message.START_NEW_GAME(time_control=time_control, game=game.copy()))
                    game_declared = False
                    set_wait_state()
                    break

                if case(EventApi.PAUSE_RESUME):
                    if engine.is_thinking():
                        stop_clock()
                        engine.stop(show_best=True)
                    else:
                        if time_control.is_ticking():
                            stop_clock()
                        else:
                            start_clock()
                    break

                if case(EventApi.ALTERNATIVE_MOVE):
                    if last_computer_fen:
                        last_computer_fen = None
                        game.pop()
                        DisplayMsg.show(Message.ALTERNATIVE_MOVE())
                        think(game, time_control)
                    break

                if case(EventApi.SWITCH_SIDES):
                    if interaction_mode == Mode.NORMAL:
                        user_to_move = False
                        last_legal_fens = []

                        if engine.is_thinking():
                            stop_clock()
                            engine.stop(show_best=False)
                            user_to_move = True
                        if event.engine_finished:
                            last_computer_fen = None
                            move = game.pop()
                            user_to_move = True
                        else:
                            move = chess.Move.null()
                        if user_to_move:
                            last_legal_fens = []
                            play_mode = PlayMode.USER_WHITE if game.turn == chess.WHITE else PlayMode.USER_BLACK
                        else:
                            play_mode = PlayMode.USER_WHITE if game.turn == chess.BLACK else PlayMode.USER_BLACK

                        if not user_to_move and check_game_state(game, play_mode):
                            time_control.reset_start_time()
                            think(game, time_control)
                            legal_fens = []
                        else:
                            start_clock()
                            legal_fens = compute_legal_fens(game)

                        text = dgttranslate.text(play_mode.value)
                        DisplayMsg.show(Message.PLAY_MODE(play_mode=play_mode, play_mode_text=text))

                        if event.engine_finished:
                            DisplayMsg.show(Message.SWITCH_SIDES(move=move))
                    break

                if case(EventApi.DRAWRESIGN):
                    if not game_declared:  # in case user leaves kings in place while moving other pieces
                        stop_search_and_clock()
                        DisplayMsg.show(Message.GAME_ENDS(result=event.result, play_mode=play_mode, game=game.copy()))
                        game_declared = True
                    break

                if case(EventApi.REMOTE_MOVE):
                    if interaction_mode == Mode.REMOTE:
                        handle_move(move=chess.Move.from_uci(event.move))
                        legal_fens = compute_legal_fens(game)
                    break

                if case(EventApi.BEST_MOVE):
                    handle_move(move=event.result.bestmove, ponder=event.result.ponder, inbook=event.inbook)
                    break

                if case(EventApi.NEW_PV):
                    # illegal moves can occur if a pv from the engine arrives at the same time as a user move.
                    if game.is_legal(event.pv[0]):
                        DisplayMsg.show(Message.NEW_PV(pv=event.pv, mode=interaction_mode, game=game.copy()))
                    else:
                        logging.info('illegal move can not be displayed. move:%s fen=%s', event.pv[0], game.fen())
                    break

                if case(EventApi.NEW_SCORE):
                    DisplayMsg.show(Message.NEW_SCORE(score=event.score, mate=event.mate, mode=interaction_mode, turn=game.turn))
                    break

                if case(EventApi.NEW_DEPTH):
                    DisplayMsg.show(Message.NEW_DEPTH(depth=event.depth))
                    break

                if case(EventApi.SET_INTERACTION_MODE):
                    if interaction_mode in (Mode.NORMAL, Mode.OBSERVE, Mode.REMOTE):
                        stop_clock()
                    interaction_mode = event.mode
                    if engine.is_thinking():
                        stop_search()
                    if engine.is_pondering():
                        stop_search()
                    set_wait_state()
                    DisplayMsg.show(Message.INTERACTION_MODE(mode=event.mode, mode_text=event.mode_text, ok_text=event.ok_text))
                    break

                if case(EventApi.SET_OPENING_BOOK):
                    config = ConfigObj('picochess.ini')
                    config['book'] = event.book['file']
                    config.write()
                    logging.debug("changing opening book [%s]", event.book['file'])
                    bookreader = chess.polyglot.open_reader(event.book['file'])
                    DisplayMsg.show(Message.OPENING_BOOK(book_text=event.book_text, ok_text=event.ok_text))
                    break

                if case(EventApi.SET_TIME_CONTROL):
                    time_control = event.time_control
                    config = ConfigObj('picochess.ini')
                    if time_control.mode == TimeMode.BLITZ:
                        config['time'] = '{:d} 0'.format(time_control.minutes_per_game)
                    elif time_control.mode == TimeMode.FISCHER:
                        config['time'] = '{:d} {:d}'.format(time_control.minutes_per_game, time_control.fischer_increment)
                    elif time_control.mode == TimeMode.FIXED:
                        config['time'] = '{:d}'.format(time_control.seconds_per_move)
                    config.write()
                    DisplayMsg.show(Message.TIME_CONTROL(time_text=event.time_text, ok_text=event.ok_text))
                    break

                if case(EventApi.OUT_OF_TIME):
                    stop_search_and_clock()
                    DisplayMsg.show(Message.GAME_ENDS(result=GameResult.OUT_OF_TIME, play_mode=play_mode, game=game.copy()))
                    break

                if case(EventApi.SHUTDOWN):
                    DisplayMsg.show(Message.GAME_ENDS(result=GameResult.ABORT, play_mode=play_mode, game=game.copy()))
                    shutdown(args.dgtpi)
                    break

                if case(EventApi.REBOOT):
                    DisplayMsg.show(Message.GAME_ENDS(result=GameResult.ABORT, play_mode=play_mode, game=game.copy()))
                    reboot()
                    break

                if case(EventApi.EMAIL_LOG):
                    if args.log_file:
                        email_logger = Emailer(email=args.email, mailgun_key=args.mailgun_key,
                                               smtp_server=args.smtp_server, smtp_user=args.smtp_user,
                                               smtp_pass=args.smtp_pass, smtp_encryption=args.smtp_encryption,
                                               smtp_from=args.smtp_from)
                        body = 'You probably want to forward this file to a picochess developer ;-)'
                        email_logger.send('Picochess LOG', body, '/opt/picochess/logs/{}'.format(args.log_file))
                    break

                if case(EventApi.DGT_BUTTON):
                    DisplayMsg.show(Message.DGT_BUTTON(button=event.button))
                    break

                if case(EventApi.DGT_FEN):
                    DisplayMsg.show(Message.DGT_FEN(fen=event.fen))
                    break

                if case():  # Default
                    logging.warning("event not handled : [%s]", event)

            evt_queue.task_done()


if __name__ == '__main__':
    main()
