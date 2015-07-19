#!/usr/bin/env python3

# Copyright (C) 2013-2014 Jean-Francois Romang (jromang@posteo.de)
#                         Shivkumar Shivaji ()
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))
import configargparse
import chess
import chess.polyglot
import logging

import uci

import threading
import copy
import time
from timecontrol import TimeControl
from utilities import *
from keyboardinput import KeyboardInput, TerminalDisplay
from pgn import PgnDisplay
from server import WebServer
import chesstalker.chesstalker
from dgthardware import DGTHardware
from dgtdisplay import DGTDisplay
from virtualhardware import VirtualHardware

import spur

def main():
    #Command line argument parsing
    parser = configargparse.ArgParser(default_config_files=[os.path.join(os.path.dirname(__file__), "picochess.ini")])
    parser.add_argument("-e", "--engine", type=str, help="UCI engine executable path", default='stockfish')
    parser.add_argument("-d", "--dgt-port", type=str, help="enable dgt board on the given serial port such as /dev/ttyUSB0")
    parser.add_argument("-leds", "--enable-dgt-board-leds", action='store_true', help="enable dgt board leds")
    parser.add_argument("-hs", "--hash-size", type=int, help="hashtable size in MB (default:64)", default=64)
    parser.add_argument("-t", "--threads", type=int, help="number of engine threads (default:1)", default=1)
    parser.add_argument("-l", "--log-level", choices=['notset', 'debug', 'info', 'warning', 'error', 'critical'], default='warning', help="logging level")
    parser.add_argument("-lf", "--log-file", type=str, help="log to the given file")
    parser.add_argument("-r", "--remote", type=str, help="remote server running the engine")
    parser.add_argument("-u", "--user", type=str, help="remote user on server running the engine")
    parser.add_argument("-p", "--password", type=str, help="password for the remote user")
    parser.add_argument("-sk", "--server-key", type=str, help="key file used to connect to the remote server")
    parser.add_argument("-pgn", "--pgn-file", type=str, help="pgn file used to store the games", default='games.pgn')
    parser.add_argument("-pgn_u", "--pgn-user", type=str, help="user name for the pgn file", default=None)
    parser.add_argument("-ar", "--auto-reboot", action='store_true', help="reboot system after update")
    parser.add_argument("-web", "--web-server", dest="web_server_port", nargs="?", const=80, type=int, metavar="PORT", help="launch web server")
    parser.add_argument("-mail", "--email", type=str, help="email used to send pgn files", default=None)
    parser.add_argument("-mail_s", "--smtp_server", type=str, help="Adress of email server", default=None)
    parser.add_argument("-mail_u", "--smtp_user", type=str, help="Username for email server", default=None)
    parser.add_argument("-mail_p", "--smtp_pass", type=str, help="Password for email server", default=None)
    parser.add_argument("-mail_enc", "--smtp_encryption", action='store_true', help="use ssl encryption connection to smtp-Server")
    parser.add_argument("-mk", "--mailgun-key", type=str, help="key used to send emails via Mailgun Webservice", default=None)
    parser.add_argument("-uci", "--uci-option", type=str, help="pass an UCI option to the engine (name;value)", default=None)
    parser.add_argument("-dgt3000", "--dgt-3000-clock", action='store_true', help="use dgt 3000 clock")
    parser.add_argument("-nobeep", "--disable-dgt-clock-beep", action='store_true', help="disable beeps on the dgt clock")
    parser.add_argument("-uvoice", "--user-voice", type=str, help="voice for user", default=None)
    parser.add_argument("-cvoice", "--computer-voice", type=str, help="voice for computer", default=None)
    args = parser.parse_args()
    engine_thread = None

    # Enable logging
    logging.basicConfig(filename=args.log_file, level=getattr(logging, args.log_level.upper()),
                        format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger("chess.uci").setLevel(logging.INFO) # don't want to get so many python-chess uci messages

    # Update
    update_picochess(args.auto_reboot)

    # Load UCI engine
    engine = uci.Engine(args.engine, hostname=args.remote, username=args.user, key_file=args.server_key, password=args.password)

    engine_name = engine.get().name
    if args.pgn_user:
        user_name = args.pgn_user
    else:
        if args.email:
            user_name = args.email.split('@')[0]
        else:
            user_name = "Player"

    logging.debug('Loaded engine [%s]', engine_name)
    logging.debug('Supported options [%s]', engine.get().options)
    if 'Hash' in engine.get().options:
        engine.option("Hash", args.hash_size)
    if 'Threads' in engine.get().options:  # Stockfish
        engine.option("Threads", args.threads)
    if 'Core Threads' in engine.get().options:  # Hiarcs
        engine.option("Core Threads", args.threads)
    if args.uci_option:
        for uci_option in args.uci_option.strip('"').split(";"):
            uci_parameter = uci_option.strip().split('=')
            engine.option(uci_parameter[0], uci_parameter[1])
    # send the options to the engine
    engine.send()

    # Connect to DGT board
    DGTDisplay(args.enable_dgt_board_leds, args.dgt_3000_clock, not args.disable_dgt_clock_beep).start()

    if args.dgt_port:
        logging.debug("Starting picochess with DGT board on [%s]", args.dgt_port)
        DGTHardware(args.dgt_port, args.dgt_3000_clock).start()
    else:
        logging.warning("No DGT board port provided")
        # Enable keyboard input and terminal display
        KeyboardInput().start()
        TerminalDisplay().start()
        VirtualHardware(args.dgt_3000_clock).start()

    # Save to PGN
    PgnDisplay(args.pgn_file, email=args.email, fromINIMailGun_Key=args.mailgun_key,
                        fromIniSmtp_Server=args.smtp_server, fromINISmtp_User=args.smtp_user,
                        fromINISmtp_Pass=args.smtp_pass, fromINISmtp_Enc=args.smtp_encryption).start() 

    # Create ChessTalker for speech output
    talker = None
    if args.user_voice or args.computer_voice:
        logging.debug("Initializing ChessTalker [%s, %s]", str(args.user_voice), str(args.computer_voice))
        talker = chesstalker.chesstalker.ChessTalker(args.user_voice, args.computer_voice)
        talker.start()
    else:
        logging.debug("ChessTalker disabled")

    # Launch web server
    if args.web_server_port:
        WebServer(args.web_server_port).start()

    def display_system_info():
        Display.show(Message.SYSTEM_INFO, info={"version": version, "location": get_location(),
                                                "books": get_opening_books(), "ip": get_ip(),
                                                "engine_name": engine_name, "user_name": user_name
                                                })

    def compute_legal_fens(g):
        """
        Computes a list of legal FENs for the given game.
        Also stores the initial position in the 'root' attribute.
        :param g: The game
        :return: A list of legal FENs, and the root FEN
        """
        class FenList(list):
            def __init__(self, *args):
                list.__init__(self, *args)
                self.root = ''

        fens = FenList()
        for move in g.legal_moves:
            g.push(move)
            fens.append(g.fen().split(' ')[0])
            g.pop()
        fens.root = g.fen().split(' ')[0]
        return fens

    def think(time):
        """
        Starts a new search on the current game.
        If a move is found in the opening book, fire an event in a few seconds.
        :return:
        """
        def send_book_move(move):
            g=copy.deepcopy(game)
            g.push(move)
            book_ponder = weighted_choice(book, g)
            Observable.fire(Event.BEST_MOVE, move=move, ponder=book_ponder)
            Observable.fire(Event.SCORE, score='book', mate=None)

        book_move = weighted_choice(book, game)
        Display.show(Message.RUN_CLOCK, turn=game.turn, time_control=time)
        time.run(game.turn)
        if book_move:
            Display.show(Message.BOOK_MOVE, move=book_move.uci())
            send_book_move(book_move)
        else:
            engine.position(game)
            nonlocal engine_status
            engine_status = EngineStatus.THINK
            Display.show(Message.SEARCH_STARTED, engine_status=engine_status)
            # res = engine.go(time.uci())
            # engine_status = EngineStatus.WAIT
            # Display.show(Message.SEARCH_STOPPED, engine_status=engine_status, result=res)
            nonlocal engine_thread
            engine_thread = threading.Timer(0, engine.go, [time.uci()])
            engine_thread.start()

    def analyse():
        """
        Starts a new ponder search on the current game.
        :return:
        """
        engine.position(game)
        nonlocal engine_status
        engine_status = EngineStatus.PONDER
        Display.show(Message.SEARCH_STARTED, engine_status=engine_status)
        # engine.ponder()
        nonlocal engine_thread
        engine_thread = threading.Timer(0, engine.ponder)
        engine_thread.start()

    def observe(time):
        """
        Starts a new ponder search on the current game.
        :return:
        """
        Display.show(Message.RUN_CLOCK, turn=game.turn, time_control=time)
        time.run(game.turn)
        analyse()

    def stop_search():
        """
        Stop current search.
        :return:
        """
        nonlocal engine_thread
        if engine_thread:
            engine_thread.cancel()
        engine.stop()
        nonlocal engine_status
        # @todo pv_game_mode is actually wrong, only valid in game mode => but result isnt used
        Display.show(Message.SEARCH_STOPPED, engine_status=engine_status, result=pv_game_mode)
        engine_status = EngineStatus.WAIT

    def stop_clock():
        nonlocal time_control
        time_control.stop()
        Display.show(Message.STOP_CLOCK)
    
    def stop_search_and_clock():
        stop_clock()
        stop_search()

    def check_game_state(game, play_mode):
        """
        Check if the game has ended or not ; it also sends Message to Displays if the game has ended.
        :param game:
        :return: True is the game continues, False if it has ended
        """
        result = None
        if game.is_stalemate():
            result=GameResult.STALEMATE
        if game.is_insufficient_material():
            result=GameResult.INSUFFICIENT_MATERIAL
        if game.is_seventyfive_moves():
            result=GameResult.SEVENTYFIVE_MOVES
        if game.is_fivefold_repetition():
            result=GameResult.FIVEFOLD_REPETITION
        if game.is_game_over():
            result=GameResult.MATE

        if result is None:
            return True
        else:
            custom_fen = game.custom_fen if hasattr(game, 'custom_fen') else None
            Display.show(Message.GAME_ENDS, result=result, moves=list(game.move_stack), color=game.turn, play_mode=play_mode, custom_fen=custom_fen)
            return False

    def process_fen(fen, legal_fens):
        if fen in legal_fens:
            # Check if we have to undo a previous move (sliding)
            if interaction_mode == Mode.GAME:
                if (play_mode == PlayMode.PLAY_WHITE and game.turn == chess.BLACK) or \
                        (play_mode == PlayMode.PLAY_BLACK and game.turn == chess.WHITE):
                    stop_search()
                    if game.move_stack:
                        game.pop()
            legal_moves = list(game.legal_moves)
            Observable.fire(Event.USER_MOVE, move=legal_moves[legal_fens.index(fen)])
        elif fen == game.fen().split(' ')[0]:  # Player had done the computer move on the board
            if check_game_state(game, play_mode) and interaction_mode == Mode.GAME:
                Display.show(Message.COMPUTER_MOVE_DONE_ON_BOARD)
                if time_control.mode != ClockMode.FIXED_TIME:
                    Display.show(Message.RUN_CLOCK, turn=game.turn, time_control=time_control)
                    time_control.run(game.turn)
        else:  # Check if this a a previous legal position and allow user to restart from this position
            game_history = copy.deepcopy(game)
            while game_history.move_stack:
                game_history.pop()
                if game_history.fen().split(' ')[0] == fen:
                    logging.debug("Undoing game until FEN :" + fen)
                    stop_search()
                    while len(game_history.move_stack) < len(game.move_stack):
                        game.pop()
                    if interaction_mode == Mode.ANALYSIS or interaction_mode == Mode.KIBITZ:
                        analyse()
                    if interaction_mode == Mode.OBSERVE or interaction_mode == Mode.REMOTE:
                        observe(time_control)
                    Display.show(Message.USER_TAKE_BACK)
                    legal_fens = compute_legal_fens(game)
                    break
        return legal_fens

    def set_wait_state():
        if interaction_mode == Mode.GAME:
            nonlocal play_mode
            play_mode = PlayMode.PLAY_WHITE if game.turn == chess.WHITE else PlayMode.PLAY_BLACK

    # Startup - internal
    game = chess.Board()  # Create the current game
    legal_fens = compute_legal_fens(game)  # Compute the legal FENs
    book = chess.polyglot.open_reader(get_opening_books()[8][1])  # Default opening book (gm1950)
    interaction_mode = Mode.GAME   # Interaction mode
    play_mode = PlayMode.PLAY_WHITE
    engine_status = EngineStatus.WAIT
    time_control = TimeControl(ClockMode.BLITZ, minutes_per_game=5)

    system_info_thread = threading.Timer(0, display_system_info)
    system_info_thread.start()

    # Startup - external
    Display.show(Message.UCI_OPTION_LIST, options=engine.get().options)
    Display.show(Message.STARTUP_INFO, info={"interaction_mode": interaction_mode, "play_mode": play_mode,
                                             "book": book, "time_control_string": "mov 5", "engine_status": engine_status
    })

    pv_game_mode = None

    # Event loop
    while True:
        try:
            event = event_queue.get()
        except queue.Empty:
            pass
        else:
            logging.debug('Received event in event loop : %s', event)
            for case in switch(event):
                if case(Event.FEN):  # User sets a new position, convert it to a move if it is legal
                    legal_fens = process_fen(event.fen, legal_fens)
                    break

                if case(Event.KEYBOARD_MOVE):
                    move = event.move
                    logging.debug('Keyboard move [%s]', move)
                    if move not in game.legal_moves:
                        logging.warning('Illegal move [%s]', move)
                    else:
                        g = copy.deepcopy(game)
                        g.push(move)
                        legal_fens = process_fen(g.fen().split(' ')[0], legal_fens)
                    break

                if case(Event.USER_MOVE):  # User sends a new move
                    move = event.move
                    logging.debug('User move [%s]', move)
                    if move not in game.legal_moves:
                        logging.warning('Illegal move [%s]', move)
                    # Check if we are in play mode and it is player's turn
                    elif interaction_mode == Mode.GAME:
                        if (play_mode == PlayMode.PLAY_WHITE and game.turn == chess.WHITE) or \
                                (play_mode == PlayMode.PLAY_BLACK and game.turn == chess.BLACK):
                            time_control.stop()
                            Display.show(Message.STOP_CLOCK)
                            game.push(move)
                            if check_game_state(game, play_mode):
                                Display.show(Message.USER_MOVE, move=move, game=copy.deepcopy(game))
                                think(time_control)
                    elif interaction_mode == Mode.OBSERVE or interaction_mode == Mode.REMOTE:
                        stop_search_and_clock()
                        fen = game.fen()
                        game.push(move)
                        if check_game_state(game, play_mode):
                            Display.show(Message.REVIEW_MODE_MOVE, move=move, fen=fen, game=copy.deepcopy(game),
                                         mode=interaction_mode)
                            observe(time_control)
                            time.sleep(0.3)
                            Display.show(Message.RUN_CLOCK, turn=game.turn, time_control=time_control)
                            legal_fens = compute_legal_fens(game)

                    elif (interaction_mode == Mode.ANALYSIS) or (interaction_mode == Mode.KIBITZ):
                        stop_search()
                        fen = game.fen()
                        game.push(move)
                        if check_game_state(game, play_mode):
                            Display.show(Message.REVIEW_MODE_MOVE, move=move, fen=fen, game=copy.deepcopy(game),
                                         mode=interaction_mode)
                            analyse()
                            legal_fens = compute_legal_fens(game)
                    break

                if case(Event.LEVEL):  # User sets a new level
                    level = event.level
                    logging.debug("Setting engine to level %i", level)
                    if engine.level(level):
                        engine.send()
                        Display.show(Message.LEVEL, level=level)
                    break

                if case(Event.SETUP_POSITION):  # User sets up a position
                    logging.debug("Setting up custom fen: {0}".format(event.fen))

                    if game.move_stack:
                        if not game.is_game_over():
                            custom_fen = game.custom_fen if hasattr(game, 'custom_fen') else None
                            Display.show(Message.GAME_ENDS, result=GameResult.ABORT, moves=list(game.move_stack),
                                         color=game.turn, play_mode=play_mode, custom_fen=custom_fen)

                    game = chess.Board(event.fen)
                    game.custom_fen = event.fen

                    legal_fens = compute_legal_fens(game)
                    stop_search_and_clock()
                    time_control.reset()

                    interaction_mode = Mode.GAME
                    set_wait_state()
                    Display.show(Message.START_NEW_GAME)
                    break

                if case(Event.STOP_SEARCH):
                    move = pv_game_mode.bestmove
                    ponder = pv_game_mode.ponder
                    stop_search_and_clock()
                    time_control.stop()
                    Display.show(Message.STOP_CLOCK)
                    fen_old = game.fen()
                    game.push(move)
                    Display.show(Message.COMPUTER_MOVE, move=move, ponder=ponder, fen=fen_old, fen_new=game.fen(),
                                 game=copy.deepcopy(game), time_control=time_control)
                    # if check_game_state(game, interaction_mode):
                    legal_fens = compute_legal_fens(game)
                    break

                if case(Event.NEW_GAME):  # User starts a new game
                    if game.move_stack:
                        logging.debug("Starting a new game")
                        if not game.is_game_over():
                            custom_fen = game.custom_fen if hasattr(game, 'custom_fen') else None
                            Display.show(Message.GAME_ENDS, result=GameResult.ABORT, moves=list(game.move_stack),
                                         color=game.turn, play_mode=play_mode, custom_fen=custom_fen)
                        game = chess.Board()

                    legal_fens = compute_legal_fens(game)
                    stop_search_and_clock()
                    time_control.reset()

                    set_wait_state()
                    Display.show(Message.START_NEW_GAME)
                    break

                if case(Event.OPENING_BOOK):
                    logging.debug("Changing opening book [%s]", event.book[1])
                    book = chess.polyglot.open_reader(event.book[1])
                    Display.show(Message.OPENING_BOOK, book=event.book)
                    break

                if case(Event.BEST_MOVE):
                    move = event.move
                    ponder = event.ponder
                    # The next three lines now here, cause of threads @ think()
                    res = chess.uci.BestMove(move, ponder)
                    Display.show(Message.SEARCH_STOPPED, engine_status=engine_status, result=res)
                    engine_status = EngineStatus.WAIT
                    # Check if we are in play mode and it is computer's turn
                    if interaction_mode == Mode.GAME:
                        if (play_mode == PlayMode.PLAY_WHITE and game.turn == chess.BLACK) or \
                                (play_mode == PlayMode.PLAY_BLACK and game.turn == chess.WHITE):
                            time_control.stop()
                            Display.show(Message.STOP_CLOCK)
                            fen_old = game.fen()
                            game.push(move)
                            Display.show(Message.COMPUTER_MOVE, move=move, ponder=ponder, fen=fen_old, fen_new=game.fen(),
                                         game=copy.deepcopy(game), time_control=time_control)
                            # if check_game_state(game, interaction_mode):
                            legal_fens = compute_legal_fens(game)
                    break

                if case(Event.NEW_PV):
                    if interaction_mode == Mode.GAME:
                        move = event.pv[0] if len(event.pv) > 0 else None
                        ponder = event.pv[1] if len(event.pv) > 1 else None
                        pv_game_mode = chess.uci.BestMove(move, ponder)
                    else:
                        Display.show(Message.NEW_PV, pv=event.pv, interaction_mode=interaction_mode, fen=game.fen())
                    break

                if case(Event.SCORE):
                    try:
                        score = int(event.score)
                        if game.turn == chess.BLACK:
                            score *= -1

                    except ValueError:
                        score = event.score
                        logging.debug('Could not convert score ' + score)

                    except TypeError:
                        score = 'm {0}'.format(event.mate)

                    Display.show(Message.SCORE, score=score, mate=event.mate, interaction_mode=interaction_mode)
                    break

                if case(Event.SET_MODE):
                    interaction_mode = event.mode
                    if engine_status == EngineStatus.THINK:
                        stop_search()  # dont need to stop, if pondering
                    if interaction_mode == Mode.OBSERVE or interaction_mode == Mode.REMOTE:
                        stop_clock()  # only stop, if the clock is really running
                    set_wait_state()
                    Display.show(Message.INTERACTION_MODE, mode=event.mode)
                    break

                if case(Event.CHANGE_PLAYMODE):
                    play_mode = PlayMode.PLAY_WHITE if play_mode == PlayMode.PLAY_BLACK else PlayMode.PLAY_BLACK
                    Display.show(Message.PLAY_MODE, play_mode=play_mode)
                    if check_game_state(game, play_mode):
                        think(time_control)
                    break

                if case(Event.SET_TIME_CONTROL):
                    time_control = event.time_control
                    Display.show(Message.TIME_CONTROL, time_control_string=event.time_control_string)
                    break

                if case(Event.OUT_OF_TIME):
                    stop_search_and_clock()
                    custom_fen = game.custom_fen if hasattr(game, 'custom_fen') else None
                    Display.show(Message.GAME_ENDS, result=GameResult.TIME_CONTROL, moves=list(game.move_stack),
                                 color=event.color, play_mode=play_mode, custom_fen=custom_fen)
                    break

                if case(Event.UCI_OPTION_SET):
                    engine.option(event.name, event.value)
                    break

                if case(Event.SHUTDOWN):
                    if talker:
                        talker.say_event(event)
                    shutdown()
                    break

                if case(Event.DGT_BUTTON):
                    Display.show(Message.BUTTON_PRESSED, button=event.button)
                    break

                if case(Event.DGT_FEN):
                    Display.show(Message.DGT_FEN, fen=event.fen)
                    break

                if case():  # Default
                    logging.warning("Event not handled : [%s]", event)

            event_queue.task_done()

if __name__ == '__main__':
    main()
