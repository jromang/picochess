#!/usr/bin/env python3

# Copyright (C) 2013-2018 Jean-Francois Romang (jromang@posteo.de)
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
import threading
import copy
import gc
import logging
from logging.handlers import RotatingFileHandler
import time
import queue
import configargparse
from platform import machine

from uci.engine import UciShell, UciEngine
from uci.read import read_engine_ini
import chess
import chess.polyglot
import chess.uci

from timecontrol import TimeControl
from utilities import get_location, update_picochess, get_opening_books, shutdown, reboot, checkout_tag
from utilities import Observable, DisplayMsg, version, evt_queue, write_picochess_ini, hms_time, RepeatedTimer
from pgn import Emailer, PgnDisplay
from server import WebServer
from talker.picotalker import PicoTalkerDisplay
from dispatcher import Dispatcher

from dgt.api import Message, Event
from dgt.util import GameResult, TimeMode, Mode, PlayMode
from dgt.hw import DgtHw
from dgt.pi import DgtPi
from dgt.display import DgtDisplay
from dgt.board import DgtBoard
from dgt.translate import DgtTranslate
from dgt.menu import DgtMenu


class AlternativeMover:

    """Keep track of alternative moves."""

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
    """Main function."""
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
        DisplayMsg.show(msg)
        start_clock()
        book_res = searchmoves.book(bookreader, game.copy())
        if book_res:
            Observable.fire(Event.BEST_MOVE(move=book_res.bestmove, ponder=book_res.ponder, inbook=True))
        else:
            while not engine.is_waiting():
                time.sleep(0.05)
                logging.warning('engine is still not waiting')
            uci_dict = timec.uci()
            uci_dict['searchmoves'] = searchmoves.all(game)
            engine.position(copy.deepcopy(game))
            engine.go(uci_dict)

    def analyse(game: chess.Board, msg: Message):
        """Start a new ponder search on the current game."""
        DisplayMsg.show(msg)
        engine.position(copy.deepcopy(game))
        engine.ponder()

    def observe(game: chess.Board, msg: Message):
        """Start a new ponder search on the current game."""
        analyse(game, msg)
        start_clock()

    def brain(game: chess.Board, timec: TimeControl):
        """Start a new permanent brain search on the game with pondering move made."""
        assert not done_computer_fen, 'brain() called with displayed move - fen: %s' % done_computer_fen
        if pb_move:
            game_copy = copy.deepcopy(game)
            game_copy.push(pb_move)
            logging.info('start permanent brain with pondering move [%s] fen: %s', pb_move, game_copy.fen())
            engine.position(game_copy)
            engine.brain(timec.uci())
        else:
            logging.info('ignore permanent brain cause no pondering move available')

    def stop_search_and_clock(ponder_hit=False):
        """Depending on the interaction mode stop search and clock."""
        if interaction_mode in (Mode.NORMAL, Mode.BRAIN):
            stop_clock()
            if engine.is_waiting():
                logging.info('engine already waiting')
            else:
                if ponder_hit:
                    pass  # we send the engine.hit() lateron!
                else:
                    stop_search()
        elif interaction_mode in (Mode.REMOTE, Mode.OBSERVE):
            stop_clock()
            stop_search()
        elif interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
            stop_search()

    def stop_search():
        """Stop current search."""
        engine.stop()
        while not engine.is_waiting():
            time.sleep(0.05)
            logging.warning('engine is still not waiting')

    def stop_clock():
        """Stop the clock."""
        if interaction_mode in (Mode.NORMAL, Mode.BRAIN, Mode.OBSERVE, Mode.REMOTE):
            time_control.stop_internal()
            DisplayMsg.show(Message.CLOCK_STOP(devs={'ser', 'i2c', 'web'}))
            time.sleep(0.4)  # @todo give some time to clock to really do it. Find a better solution!
        else:
            logging.warning('wrong function call [stop]! mode: %s', interaction_mode)

    def start_clock():
        """Start the clock."""
        if interaction_mode in (Mode.NORMAL, Mode.BRAIN, Mode.OBSERVE, Mode.REMOTE):
            time_control.start_internal(game.turn)
            tc_init = time_control.get_parameters()
            DisplayMsg.show(Message.CLOCK_START(turn=game.turn, tc_init=tc_init, devs={'ser', 'i2c', 'web'}))
            time.sleep(0.4)  # @todo give some time to clock to really do it. Find a better solution!
        else:
            logging.warning('wrong function call [start]! mode: %s', interaction_mode)

    def check_game_state(game: chess.Board, play_mode: PlayMode):
        """
        Check if the game has ended or not ; it also sends Message to Displays if the game has ended.

        :param game:
        :param play_mode:
        :return: False is the game continues, Game_Ends() Message if it has ended
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
            return False
        else:
            return Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy())

    def user_move(move: chess.Move, sliding: bool):
        """Handle an user move."""
        nonlocal game
        nonlocal done_move
        nonlocal done_computer_fen
        nonlocal time_control

        logging.info('user move [%s] sliding: %s', move, sliding)
        if move not in game.legal_moves:
            logging.warning('illegal move [%s]', move)
        else:
            if interaction_mode == Mode.BRAIN:
                ponder_hit = (move == pb_move)
                logging.info('pondering move: [%s] res: Ponder%s', pb_move, 'Hit' if ponder_hit else 'Miss')
            else:
                ponder_hit = False
            if sliding and ponder_hit:
                logging.warning('sliding detected, turn ponderhit off')
                ponder_hit = False
            stop_search_and_clock(ponder_hit=ponder_hit)
            if interaction_mode in (Mode.NORMAL, Mode.BRAIN, Mode.OBSERVE, Mode.REMOTE) and not sliding:
                time_control.add_time(game.turn)

            done_computer_fen = None
            done_move = chess.Move.null()
            fen = game.fen()
            turn = game.turn
            game.push(move)
            searchmoves.reset()
            if interaction_mode in (Mode.NORMAL, Mode.BRAIN):
                msg = Message.USER_MOVE_DONE(move=move, fen=fen, turn=turn, game=game.copy())
                game_end = check_game_state(game, play_mode)
                if game_end:
                    DisplayMsg.show(msg)
                    DisplayMsg.show(game_end)
                else:
                    if interaction_mode == Mode.NORMAL or not ponder_hit:
                        if not check_game_state(game, play_mode):
                            logging.info('starting think()')
                            think(game, time_control, msg)
                    else:
                        logging.info('think() not started cause ponderhit')
                        DisplayMsg.show(msg)
                        start_clock()
                        engine.hit()  # finally tell the engine
            elif interaction_mode == Mode.REMOTE:
                msg = Message.USER_MOVE_DONE(move=move, fen=fen, turn=turn, game=game.copy())
                game_end = check_game_state(game, play_mode)
                if game_end:
                    DisplayMsg.show(msg)
                    DisplayMsg.show(game_end)
                else:
                    observe(game, msg)
            elif interaction_mode == Mode.OBSERVE:
                msg = Message.REVIEW_MOVE_DONE(move=move, fen=fen, turn=turn, game=game.copy())
                game_end = check_game_state(game, play_mode)
                if game_end:
                    DisplayMsg.show(msg)
                    DisplayMsg.show(game_end)
                else:
                    observe(game, msg)
            else:  # interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
                msg = Message.REVIEW_MOVE_DONE(move=move, fen=fen, turn=turn, game=game.copy())
                game_end = check_game_state(game, play_mode)
                if game_end:
                    DisplayMsg.show(msg)
                    DisplayMsg.show(game_end)
                else:
                    analyse(game, msg)

    def is_not_user_turn(turn):
        """Return if it is users turn (only valid in normal, brain or remote mode)."""
        assert interaction_mode in (Mode.NORMAL, Mode.BRAIN, Mode.REMOTE), 'wrong mode: %s' % interaction_mode
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
        nonlocal pb_move
        nonlocal error_fen

        handled_fen = True
        # Check for same position
        if fen == game.board_fen():
            logging.debug('Already in this fen: %s', fen)

        # Check if we have to undo a previous move (sliding)
        elif fen in last_legal_fens:
            logging.info('sliding move detected')
            if interaction_mode in (Mode.NORMAL, Mode.BRAIN):
                if is_not_user_turn(game.turn):
                    stop_search()
                    game.pop()
                    logging.info('user move in computer turn, reverting to: %s', game.fen())
                elif done_computer_fen:
                    done_computer_fen = None
                    done_move = chess.Move.null()
                    game.pop()
                    logging.info('user move while computer move is displayed, reverting to: %s', game.fen())
                else:
                    handled_fen = False
                    logging.error('last_legal_fens not cleared: %s', game.fen())
            elif interaction_mode == Mode.REMOTE:
                if is_not_user_turn(game.turn):
                    game.pop()
                    logging.info('user move in remote turn, reverting to: %s', game.fen())
                elif done_computer_fen:
                    done_computer_fen = None
                    done_move = chess.Move.null()
                    game.pop()
                    logging.info('user move while remote move is displayed, reverting to: %s', game.fen())
                else:
                    handled_fen = False
                    logging.error('last_legal_fens not cleared: %s', game.fen())
            else:
                game.pop()
                logging.info('wrong color move -> sliding, reverting to: %s', game.fen())
            legal_moves = list(game.legal_moves)
            move = legal_moves[last_legal_fens.index(fen)]  # type: chess.Move
            user_move(move, sliding=True)
            if interaction_mode in (Mode.NORMAL, Mode.BRAIN, Mode.REMOTE):
                legal_fens = []
            else:
                legal_fens = compute_legal_fens(game.copy())

        # legal move
        elif fen in legal_fens:
            logging.info('standard move detected')
            # time_control.add_inc(game.turn)  # deactivated and moved to user_move() cause tc still running :-(
            legal_moves = list(game.legal_moves)
            move = legal_moves[legal_fens.index(fen)]  # type: chess.Move
            user_move(move, sliding=False)
            last_legal_fens = legal_fens
            if interaction_mode in (Mode.NORMAL, Mode.BRAIN, Mode.REMOTE):
                legal_fens = []
            else:
                legal_fens = compute_legal_fens(game.copy())

        # Player had done the computer or remote move on the board
        elif fen == done_computer_fen:
            logging.info('done move detected')
            assert interaction_mode in (Mode.NORMAL, Mode.BRAIN, Mode.REMOTE), 'wrong mode: %s' % interaction_mode
            DisplayMsg.show(Message.COMPUTER_MOVE_DONE())
            game.push(done_move)
            done_computer_fen = None
            done_move = chess.Move.null()
            game_end = check_game_state(game, play_mode)
            if game_end:
                legal_fens = []
                DisplayMsg.show(game_end)
            else:
                searchmoves.reset()
                time_control.add_time(not game.turn)
                start_clock()
                if interaction_mode == Mode.BRAIN:
                    brain(game, time_control)

                legal_fens = compute_legal_fens(game.copy())
            last_legal_fens = []

        # Check if this is a previous legal position and allow user to restart from this position
        else:
            handled_fen = False
            game_copy = copy.deepcopy(game)
            while game_copy.move_stack:
                game_copy.pop()
                if game_copy.board_fen() == fen:
                    handled_fen = True
                    logging.info('current game fen      : %s', game.fen())
                    logging.info('undoing game until fen: %s', fen)
                    stop_search_and_clock()
                    while len(game_copy.move_stack) < len(game.move_stack):
                        game.pop()

                    # its a complete new pos, delete safed values
                    done_computer_fen = None
                    done_move = pb_move = chess.Move.null()
                    searchmoves.reset()

                    set_wait_state(Message.TAKE_BACK(game=game.copy()))  # new: force stop no matter if picochess turn
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
        if not done_computer_fen:
            nonlocal play_mode, legal_fens, last_legal_fens
            legal_fens = compute_legal_fens(game.copy())
            last_legal_fens = []
        if interaction_mode in (Mode.NORMAL, Mode.BRAIN):  # @todo handle Mode.REMOTE too
            if done_computer_fen:
                logging.debug('best move displayed, dont search and also keep play mode: %s', play_mode)
                start_search = False
            else:
                old_mode = play_mode
                play_mode = PlayMode.USER_WHITE if game.turn == chess.WHITE else PlayMode.USER_BLACK
                if old_mode != play_mode:
                    logging.debug('new play mode: %s', play_mode)  # @todo below: for the moment send it to display too
                    text = play_mode.value  # type: str
                    DisplayMsg.show(Message.PLAY_MODE(play_mode=play_mode, play_mode_text=dgttranslate.text(text)))
        if start_search:
            assert engine.is_waiting(), 'engine not waiting! thinking status: %s' % engine.is_thinking()
            # Go back to analysing or observing
            if interaction_mode == Mode.BRAIN and not done_computer_fen:
                brain(game, time_control)
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
                value = int(time_str)
                if value > 99:
                    value = 99
                return value
            except ValueError:
                return 1

        if len(time_list) == 1:
            fixed = _num(time_list[0])
            timec = TimeControl(TimeMode.FIXED, fixed=fixed)
            textc = dgttranslate.text('B00_tc_fixed', timec.get_list_text())
        elif len(time_list) == 2:
            blitz = _num(time_list[0])
            fisch = _num(time_list[1])
            if fisch == 0:
                timec = TimeControl(TimeMode.BLITZ, blitz=blitz)
                textc = dgttranslate.text('B00_tc_blitz', timec.get_list_text())
            else:
                timec = TimeControl(TimeMode.FISCHER, blitz=blitz, fischer=fisch)
                textc = dgttranslate.text('B00_tc_fisch', timec.get_list_text())
        else:
            timec = TimeControl(TimeMode.BLITZ, blitz=5)
            textc = dgttranslate.text('B00_tc_blitz', timec.get_list_text())
        return timec, textc

    def get_engine_level_dict(engine_level):
        """Transfer an engine level to its level_dict plus an index."""
        installed_engines = engine.get_installed_engines()
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

    def engine_mode():
        ponder_mode = analyse_mode = False
        if False:  # switch-case
            pass
        elif interaction_mode in (Mode.NORMAL, Mode.REMOTE):
            pass
        elif interaction_mode == Mode.BRAIN:
            ponder_mode = True
        elif interaction_mode in (Mode.ANALYSIS, Mode.KIBITZ, Mode.OBSERVE, Mode.PONDER):
            analyse_mode = True
        engine.mode(ponder=ponder_mode, analyse=analyse_mode)

    def _dgt_serial_nr():
        DisplayMsg.show(Message.DGT_SERIAL_NR(number='dont_use'))

    # Enable garbage collection - needed for engine swapping as objects orphaned
    gc.enable()

    # Command line argument parsing
    parser = configargparse.ArgParser(default_config_files=[os.path.join(os.path.dirname(__file__), 'picochess.ini')])
    parser.add_argument('-e', '--engine', type=str, help="UCI engine filename/path such as 'engines/armv7l/a-stockf'",
                        default=None)
    parser.add_argument('-el', '--engine-level', type=str, help='UCI engine level', default=None)
    parser.add_argument('-er', '--engine-remote', type=str,
                        help="UCI engine filename/path such as 'engines/armv7l/a-stockf'", default=None)
    parser.add_argument('-ers', '--engine-remote-server', type=str, help='adress of the remote engine server',
                        default=None)
    parser.add_argument('-eru', '--engine-remote-user', type=str, help='username for the remote engine server')
    parser.add_argument('-erp', '--engine-remote-pass', type=str, help='password for the remote engine server')
    parser.add_argument('-erk', '--engine-remote-key', type=str, help='key file for the remote engine server')
    parser.add_argument('-erh', '--engine-remote-home', type=str, help='engine home path for the remote engine server',
                        default='')
    parser.add_argument('-d', '--dgt-port', type=str,
                        help="enable dgt board on the given serial port such as '/dev/ttyUSB0'")
    parser.add_argument('-b', '--book', type=str, help="path of book such as 'books/b-flank.bin'",
                        default='books/h-varied.bin')
    parser.add_argument('-t', '--time', type=str, default='5 0',
                        help="Time settings <FixSec> or <StMin IncSec> like '10'(move) or '5 0'(game) '3 2'(fischer). \
                        All values must be below 100")
    parser.add_argument('-norl', '--disable-revelation-leds', action='store_true', help='disable Revelation leds')
    parser.add_argument('-l', '--log-level', choices=['notset', 'debug', 'info', 'warning', 'error', 'critical'],
                        default='warning', help='logging level')
    parser.add_argument('-lf', '--log-file', type=str, help='log to the given file')
    parser.add_argument('-pf', '--pgn-file', type=str, help='pgn file used to store the games', default='games.pgn')
    parser.add_argument('-pu', '--pgn-user', type=str, help='user name for the pgn file', default=None)
    parser.add_argument('-pe', '--pgn-elo', type=str, help='user elo for the pgn file', default='-')
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
    parser.add_argument('-uv', '--user-voice', type=str, help='voice for user', default=None)
    parser.add_argument('-cv', '--computer-voice', type=str, help='voice for computer', default=None)
    parser.add_argument('-sv', '--speed-voice', type=int, help='voice speech factor from 0(=90%%) to 9(=135%%)',
                        default=2, choices=range(0, 10))
    parser.add_argument('-sp', '--enable-setpieces-voice', action='store_true',
                        help="speak last computer move again when 'set pieces' displayed")
    parser.add_argument('-u', '--enable-update', action='store_true', help='enable picochess updates')
    parser.add_argument('-ur', '--enable-update-reboot', action='store_true', help='reboot system after update')
    parser.add_argument('-nocm', '--disable-confirm-message', action='store_true', help='disable confirmation messages')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s version {}'.format(version),
                        help='show current version', default=None)
    parser.add_argument('-pi', '--dgtpi', action='store_true', help='use the DGTPi hardware')
    parser.add_argument('-pt', '--ponder-interval', type=int, default=3, choices=range(1, 9),
                        help='how long each part of ponder display should be visible (default=3secs)')
    parser.add_argument('-lang', '--language', choices=['en', 'de', 'nl', 'fr', 'es', 'it'], default='en',
                        help='picochess language')
    parser.add_argument('-c', '--enable-console', action='store_true', help='use console interface')
    parser.add_argument('-cl', '--enable-capital-letters', action='store_true', help='clock messages in capital letters')
    parser.add_argument('-noet', '--disable-et', action='store_true', help='some clocks need this to work - deprecated')
    parser.add_argument('-ss', '--slow-slide', type=int, default=0, choices=range(0, 10),
                        help='extra wait time factor for a stable board position (sliding detect)')
    parser.add_argument('-nosn', '--disable-short-notation', action='store_true', help='disable short notation')

    args, unknown = parser.parse_known_args()

    # Enable logging
    if args.log_file:
        handler = RotatingFileHandler('logs' + os.sep + args.log_file, maxBytes=1.4 * 1024 * 1024, backupCount=5)
        logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                            format='%(asctime)s.%(msecs)03d %(levelname)7s %(module)10s - %(funcName)s: %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S", handlers=[handler])
    logging.getLogger('chess.engine').setLevel(logging.INFO)  # don't want to get so many python-chess uci messages

    logging.debug('#' * 20 + ' PicoChess v%s ' + '#' * 20, version)
    # log the startup parameters but hide the password fields
    a_copy = copy.copy(vars(args))
    a_copy['mailgun_key'] = a_copy['smtp_pass'] = a_copy['engine_remote_key'] = a_copy['engine_remote_pass'] = '*****'
    logging.debug('startup parameters: %s', a_copy)
    if unknown:
        logging.warning('invalid parameter given %s', unknown)
    # wire some dgt classes
    dgtboard = DgtBoard(args.dgt_port, args.disable_revelation_leds, args.dgtpi, args.disable_et, args.slow_slide)
    dgttranslate = DgtTranslate(args.beep_config, args.beep_some_level, args.language, version)
    dgtmenu = DgtMenu(args.disable_confirm_message, args.ponder_interval,
                      args.user_voice, args.computer_voice, args.speed_voice, args.enable_capital_letters,
                      args.disable_short_notation, args.log_file, args.engine_remote_server, dgttranslate)
    dgtdispatcher = Dispatcher(dgtmenu)

    time_control, time_text = transfer_time(args.time.split())
    time_text.beep = False
    # The class dgtDisplay fires Event (Observable) & DispatchDgt (Dispatcher)
    DgtDisplay(dgttranslate, dgtmenu, time_control).start()

    # Create PicoTalker for speech output
    PicoTalkerDisplay(args.user_voice, args.computer_voice, args.speed_voice, args.enable_setpieces_voice).start()

    # Launch web server
    if args.web_server_port:
        WebServer(args.web_server_port, dgtboard).start()
        dgtdispatcher.register('web')

    if args.enable_console:
        logging.debug('starting PicoChess in console mode')
        RepeatedTimer(1, _dgt_serial_nr).start()  # simulate the dgtboard watchdog
    else:
        # Connect to DGT board
        logging.debug('starting PicoChess in board mode')
        if args.dgtpi:
            DgtPi(dgtboard).start()
            dgtdispatcher.register('i2c')
        else:
            logging.debug('(ser) starting the board connection')
            dgtboard.run()  # a clock can only be online together with the board, so we must start it infront
        DgtHw(dgtboard).start()
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

    # try the given engine first and if that fails the first/second from "engines.ini" then crush
    engine_file = args.engine if args.engine_remote_server is None else args.engine_remote
    engine_home = 'engines' + os.sep + machine() if args.engine_remote_server is None else args.engine_remote_home.rstrip(os.sep)
    engine_tries = 0
    engine = engine_name = None
    uci_shell = UciShell(hostname=args.engine_remote_server, username=args.engine_remote_user,
                         key_file=args.engine_remote_key, password=args.engine_remote_pass)
    while engine_tries < 2:
        if engine_file is None:
            eng_ini = read_engine_ini(uci_shell.get(), engine_home)
            engine_file = eng_ini[engine_tries]['file']
            engine_tries += 1
        engine_file = os.path.basename(engine_file)
        # Gentlemen, start your engines...
        engine = UciEngine(file=engine_file, uci_shell=uci_shell, home=engine_home)
        try:
            engine_name = engine.get_name()
            break
        except AttributeError:
            logging.error('engine %s not started', engine_file)
            engine_file = None

    if engine_tries == 2:
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
    play_mode = PlayMode.USER_WHITE  # @todo handle Mode.REMOTE too

    last_legal_fens = []
    done_computer_fen = None
    done_move = chess.Move.null()
    game_declared = False  # User declared resignation or draw

    args.engine_level = None if args.engine_level == 'None' else args.engine_level
    engine_opt, level_index = get_engine_level_dict(args.engine_level)
    engine.startup(engine_opt)
    engine.newgame(game.copy())

    # Startup - external
    level_name = args.engine_level
    if level_name:
        level_text = dgttranslate.text('B00_level', level_name)
        level_text.beep = False
    else:
        level_text = None
        level_name = ''
    sys_info = {'version': version, 'engine_name': engine_name, 'user_name': user_name, 'user_elo': args.pgn_elo}
    DisplayMsg.show(Message.STARTUP_INFO(info={'interaction_mode': interaction_mode, 'play_mode': play_mode,
                                               'books': all_books, 'book_index': book_index,
                                               'level_text': level_text, 'level_name': level_name,
                                               'tc_init': time_control.get_parameters(), 'time_text': time_text}))
    DisplayMsg.show(Message.SYSTEM_INFO(info=sys_info))
    DisplayMsg.show(Message.ENGINE_STARTUP(installed_engines=engine.get_installed_engines(), file=engine.get_file(),
                                           level_index=level_index,
                                           has_960=engine.has_chess960(), has_ponder=engine.has_ponder()))

    ip_info_thread = threading.Timer(10, display_ip_info)  # give RaspberyPi 10sec time to startup its network devices
    ip_info_thread.start()

    fen_timer = threading.Timer(3, expired_fen_timer)
    fen_timer_running = False
    error_fen = None

    pb_move = chess.Move.null()  # safes the best ponder move so far (for permanent brain use)

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
                DisplayMsg.show(Message.LEVEL(level_text=event.level_text, level_name=event.level_name,
                                              do_speak=bool(event.options)))
                stop_fen_timer()

            elif isinstance(event, Event.NEW_ENGINE):
                old_file = engine.get_file()
                old_options = {}
                raw_options = engine.get_options()
                for name, value in raw_options.items():  # transfer Option to string by using the "default" value
                    old_options[name] = str(value.default)
                engine_fallback = False
                # Stop the old engine cleanly
                stop_search()
                # Closeout the engine process and threads
                if engine.quit():
                    # Load the new one and send args.
                    engine = UciEngine(file=event.eng['file'], uci_shell=uci_shell)
                    try:
                        engine_name = engine.get_name()
                    except AttributeError:
                        # New engine failed to start, restart old engine
                        logging.error('new engine failed to start, reverting to %s', old_file)
                        engine_fallback = True
                        event.options = old_options
                        engine = UciEngine(file=old_file, uci_shell=uci_shell)
                        try:
                            engine_name = engine.get_name()
                        except AttributeError:
                            # Help - old engine failed to restart. There is no engine
                            logging.error('no engines started')
                            DisplayMsg.show(Message.ENGINE_FAIL())
                            time.sleep(3)
                            sys.exit(-1)
                    engine.startup(event.options)
                    engine.newgame(game.copy())
                    # All done - rock'n'roll
                    if interaction_mode == Mode.BRAIN and not engine.has_ponder():
                        logging.debug('new engine doesnt support brain mode, reverting to %s', old_file)
                        engine_fallback = True
                        if engine.quit():
                            engine = UciEngine(file=old_file, uci_shell=uci_shell)
                            engine.startup(old_options)
                            engine.newgame(game.copy())
                        else:
                            logging.error('engine shutdown failure')
                    engine_mode()
                    if engine_fallback:
                        msg = Message.ENGINE_FAIL()
                    else:
                        searchmoves.reset()
                        msg = Message.ENGINE_READY(eng=event.eng, engine_name=engine_name,
                                                   eng_text=event.eng_text, has_levels=engine.has_levels(),
                                                   has_960=engine.has_chess960(), has_ponder=engine.has_ponder(),
                                                   show_ok=event.show_ok)
                    # Schedule cleanup of old objects
                    gc.collect()
                    set_wait_state(msg, not engine_fallback)
                    if interaction_mode in (Mode.NORMAL, Mode.BRAIN):  # engine isnt started/searching => stop the clock
                        stop_clock()
                else:
                    logging.error('engine shutdown failure')
                    DisplayMsg.show(Message.ENGINE_FAIL())
                # here dont care if engine supports pondering, cause Mode.NORMAL from startup
                if not engine_fallback and not args.engine_remote_server:  # dont write engine(_level) if remote engine
                    write_picochess_ini('engine', event.eng['file'])

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
                engine.newgame(game.copy())
                done_computer_fen = None
                done_move = pb_move = chess.Move.null()
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
                    engine.newgame(game.copy())
                    done_computer_fen = None
                    done_move = pb_move = chess.Move.null()
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
                elif not done_computer_fen:
                    if time_control.internal_running():
                        stop_clock()
                    else:
                        start_clock()
                else:
                    logging.debug('best move displayed, dont start/stop clock')

            elif isinstance(event, Event.ALTERNATIVE_MOVE):
                if done_computer_fen:
                    done_computer_fen = None
                    done_move = chess.Move.null()
                    if interaction_mode in (Mode.NORMAL, Mode.BRAIN):  # @todo handle Mode.REMOTE too
                        if time_control.mode == TimeMode.FIXED:
                            time_control.reset()
                        # set computer to move - in case the user just changed the engine
                        play_mode = PlayMode.USER_WHITE if game.turn == chess.BLACK else PlayMode.USER_BLACK
                        if not check_game_state(game, play_mode):
                            think(game, time_control, Message.ALTERNATIVE_MOVE(game=game.copy(), play_mode=play_mode))
                    else:
                        logging.warning('wrong function call [alternative]! mode: %s', interaction_mode)

            elif isinstance(event, Event.SWITCH_SIDES):
                if interaction_mode in (Mode.NORMAL, Mode.BRAIN):
                    if not engine.is_waiting():
                        stop_search_and_clock()

                    last_legal_fens = []
                    best_move_displayed = done_computer_fen
                    if best_move_displayed:
                        move = done_move
                        done_computer_fen = None
                        done_move = pb_move = chess.Move.null()
                    else:
                        move = chess.Move.null()  # not really needed

                    play_mode = PlayMode.USER_WHITE if play_mode == PlayMode.USER_BLACK else PlayMode.USER_BLACK
                    text = play_mode.value  # type: str
                    msg = Message.PLAY_MODE(play_mode=play_mode, play_mode_text=dgttranslate.text(text))

                    if time_control.mode == TimeMode.FIXED:
                        time_control.reset()

                    legal_fens = []
                    game_end = check_game_state(game, play_mode)
                    if game_end:
                        DisplayMsg.show(msg)
                    else:
                        cond1 = game.turn == chess.WHITE and play_mode == PlayMode.USER_BLACK
                        cond2 = game.turn == chess.BLACK and play_mode == PlayMode.USER_WHITE
                        if cond1 or cond2:
                            time_control.reset_start_time()
                            think(game, time_control, msg)
                        else:
                            DisplayMsg.show(msg)
                            start_clock()
                            legal_fens = compute_legal_fens(game.copy())

                    if best_move_displayed:
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
                    DisplayMsg.show(Message.COMPUTER_MOVE(move=event.move, ponder=chess.Move.null(), game=game.copy(),
                                                          wait=False))
                    game_copy = game.copy()
                    game_copy.push(event.move)
                    done_computer_fen = game_copy.board_fen()
                    done_move = event.move
                    pb_move = chess.Move.null()
                else:
                    logging.warning('wrong function call [remote]! mode: %s turn: %s', interaction_mode, game.turn)

            elif isinstance(event, Event.BEST_MOVE):
                if interaction_mode in (Mode.NORMAL, Mode.BRAIN) and is_not_user_turn(game.turn):
                    # clock must be stopped BEFORE the "book_move" event cause SetNRun resets the clock display
                    stop_clock()
                    # @todo 8/8/R6P/1R6/7k/2B2K1p/8/8 and sliding Ra6 over a5 to a4 - handle this in correct way!!
                    if game.is_game_over():
                        logging.warning('illegal move on game_end - sliding? move: %s fen: %s', event.move, game.fen())
                    else:
                        if event.inbook:
                            DisplayMsg.show(Message.BOOK_MOVE())
                        searchmoves.add(event.move)
                        DisplayMsg.show(Message.COMPUTER_MOVE(move=event.move, ponder=event.ponder, game=game.copy(),
                                                              wait=event.inbook))
                        game_copy = game.copy()
                        game_copy.push(event.move)
                        done_computer_fen = game_copy.board_fen()
                        done_move = event.move
                        brain_book = interaction_mode == Mode.BRAIN and event.inbook
                        pb_move = event.ponder if event.ponder and not brain_book else chess.Move.null()
                else:
                    logging.warning('wrong function call [best]! mode: %s turn: %s', interaction_mode, game.turn)

            elif isinstance(event, Event.NEW_PV):
                if interaction_mode == Mode.BRAIN and engine.is_pondering():
                    logging.debug('in brain mode and pondering ignore pv %s', event.pv[:3])
                else:
                    # illegal moves can occur if a pv from the engine arrives at the same time as an user move
                    if game.is_legal(event.pv[0]):
                        DisplayMsg.show(Message.NEW_PV(pv=event.pv, mode=interaction_mode, game=game.copy()))
                    else:
                        logging.info('illegal move can not be displayed. move: %s fen: %s', event.pv[0], game.fen())
                        logging.info('engine status: t:%s p:%s', engine.is_thinking(), engine.is_pondering())

            elif isinstance(event, Event.NEW_SCORE):
                if interaction_mode == Mode.BRAIN and engine.is_pondering():
                    logging.debug('in brain mode and pondering, ignore score %s', event.score)
                else:
                    DisplayMsg.show(Message.NEW_SCORE(score=event.score, mate=event.mate, mode=interaction_mode,
                                                      turn=game.turn))

            elif isinstance(event, Event.NEW_DEPTH):
                if interaction_mode == Mode.BRAIN and engine.is_pondering():
                    logging.debug('in brain mode and pondering, ignore depth %s', event.depth)
                else:
                    DisplayMsg.show(Message.NEW_DEPTH(depth=event.depth))

            elif isinstance(event, Event.START_SEARCH):
                DisplayMsg.show(Message.SEARCH_STARTED())

            elif isinstance(event, Event.STOP_SEARCH):
                DisplayMsg.show(Message.SEARCH_STOPPED())

            elif isinstance(event, Event.SET_INTERACTION_MODE):
                if event.mode not in (Mode.NORMAL, Mode.REMOTE) and done_computer_fen:  # @todo check why still needed
                    dgtmenu.set_mode(interaction_mode)  # undo the button4 stuff
                    logging.warning('mode cant be changed to a pondering mode as long as a move is displayed')
                    mode_text = dgttranslate.text('Y10_errormode')
                    msg = Message.INTERACTION_MODE(mode=interaction_mode, mode_text=mode_text, show_ok=False)
                    DisplayMsg.show(msg)
                else:
                    stop_search_and_clock()
                    interaction_mode = event.mode
                    engine_mode()
                    msg = Message.INTERACTION_MODE(mode=event.mode, mode_text=event.mode_text, show_ok=event.show_ok)
                    set_wait_state(msg)  # dont clear searchmoves here

            elif isinstance(event, Event.SET_OPENING_BOOK):
                write_picochess_ini('book', event.book['file'])
                logging.debug('changing opening book [%s]', event.book['file'])
                bookreader = chess.polyglot.open_reader(event.book['file'])
                DisplayMsg.show(Message.OPENING_BOOK(book_text=event.book_text, show_ok=event.show_ok))
                stop_fen_timer()

            elif isinstance(event, Event.SET_TIME_CONTROL):
                time_control.stop_internal(log=False)
                tc_init = event.tc_init
                time_control = TimeControl(**tc_init)
                if time_control.mode == TimeMode.BLITZ:
                    write_picochess_ini('time', '{:d} 0'.format(tc_init['blitz']))
                elif time_control.mode == TimeMode.FISCHER:
                    write_picochess_ini('time', '{:d} {:d}'.format(tc_init['blitz'], tc_init['fischer']))
                elif time_control.mode == TimeMode.FIXED:
                    write_picochess_ini('time', '{:d}'.format(tc_init['fixed']))
                text = Message.TIME_CONTROL(time_text=event.time_text, show_ok=event.show_ok, tc_init=tc_init)
                DisplayMsg.show(text)
                stop_fen_timer()

            elif isinstance(event, Event.CLOCK_TIME):
                if dgtdispatcher.is_prio_device(event.dev, event.connect):  # transfer only the most prio clock's time
                    logging.debug('setting tc clock time - prio: %s w:%s b:%s', event.dev,
                                  hms_time(event.time_white), hms_time(event.time_black))
                    time_control.set_clock_times(white_time=event.time_white, black_time=event.time_black)
                    # find out, if we are in bullet time (<=60secs on users clock or lowest time if user side unknown)
                    time_u = event.time_white
                    time_c = event.time_black
                    if interaction_mode in (Mode.NORMAL, Mode.BRAIN):  # @todo handle Mode.REMOTE too
                        if play_mode == PlayMode.USER_BLACK:
                            time_u, time_c = time_c, time_u
                    else:  # here, we use the lowest time
                        if time_c < time_u:
                            time_u, time_c = time_c, time_u
                    low_time = time_u <= 60 and not (time_control.mode == TimeMode.FIXED and time_control.move_time > 2)
                    dgtboard.low_time = low_time
                    DisplayMsg.show(Message.CLOCK_TIME(time_white=event.time_white, time_black=event.time_black,
                                                       low_time=low_time))
                else:
                    logging.debug('ignore clock time - too low prio: %s', event.dev)

            elif isinstance(event, Event.OUT_OF_TIME):
                stop_search_and_clock()
                result = GameResult.OUT_OF_TIME
                DisplayMsg.show(Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy()))

            elif isinstance(event, Event.SHUTDOWN):
                if uci_shell.get():
                    uci_shell.get().__exit__(None, None, None)  # force to call __exit__ (close shell connection)
                result = GameResult.ABORT
                DisplayMsg.show(Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy()))
                DisplayMsg.show(Message.SYSTEM_SHUTDOWN())
                shutdown(args.dgtpi and uci_shell.get() is None, dev=event.dev)  # @todo make independant of remote eng

            elif isinstance(event, Event.REBOOT):
                result = GameResult.ABORT
                DisplayMsg.show(Message.GAME_ENDS(result=result, play_mode=play_mode, game=game.copy()))
                DisplayMsg.show(Message.SYSTEM_REBOOT())
                reboot(args.dgtpi and uci_shell.get() is None, dev=event.dev)  # @todo make independant of remote eng

            elif isinstance(event, Event.EMAIL_LOG):
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

            elif isinstance(event, Event.REMOTE_ROOM):
                DisplayMsg.show(Message.REMOTE_ROOM(inside=event.inside))

            else:  # Default
                logging.warning('event not handled : [%s]', event)

            evt_queue.task_done()


if __name__ == '__main__':
    main()
