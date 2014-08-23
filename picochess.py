#! /usr/bin/env python3

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
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+os.sep+'libs')
import configargparse
import chess
import chess.polyglot
import dgt
import logging
import uci
import threading
from timecontrol import TimeControl
from utilities import *
from keyboardinput import KeyboardInput, TerminalDisplay
from pgn import PgnDisplay
from server import WebServer


def main():
    #Command line argument parsing
    parser = configargparse.ArgParser(default_config_files=[os.path.dirname(os.path.realpath(__file__)) + os.sep + 'picochess.ini'])
    parser.add_argument("-e", "--engine", type=str, help="UCI engine executable path", required=True)
    parser.add_argument("-d", "--dgt-port", type=str, help="enable dgt board on the given serial port such as /dev/ttyUSB0")
    parser.add_argument("-hs", "--hash-size", type=int, help="hashtable size in MB (default:64)", default=64)
    parser.add_argument("-t", "--threads", type=int, help="number of engine threads (default:1)", default=1)
    parser.add_argument("-l", "--log-level", choices=['notset', 'debug', 'info', 'warning', 'error', 'critical'], default='warning', help="logging level")
    parser.add_argument("-lf", "--log-file", type=str, help="log to the given file")
    parser.add_argument("-r", "--remote", type=str, help="remote server running the engine")
    parser.add_argument("-u", "--user", type=str, help="remote user on server running the engine")
    parser.add_argument("-p", "--password", type=str, help="password for the remote user")
    parser.add_argument("-k", "--key-file", type=str, help="key file used to connect to the remote server")
    parser.add_argument("-pgn", "--pgn-file", type=str, help="pgn file used to store the games")
    parser.add_argument("-ar", "--auto-reboot", action='store_true', help="reboot system after update")
    parser.add_argument("-web", "--web-server", action='store_true', help="launch web server")
    parser.add_argument("-mail", "--email", type=str, help="email used to send pgn files")
    args = parser.parse_args()

    # Enable logging
    logging.basicConfig(filename=args.log_file, level=getattr(logging, args.log_level.upper()),
                        format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    # Update
    update_picochess(args.auto_reboot)

    # Load UCI engine
    engine = uci.Engine(args.engine, hostname=args.remote, username=args.user, key_file=args.key_file, password=args.password)
    logging.debug('Loaded engine [%s]', engine.name)
    logging.debug('Supported options [%s]', engine.options)
    if 'Hash' in engine.options:
        engine.set_option("Hash", args.hash_size)
    if 'Threads' in engine.options:  # Stockfish
        engine.set_option("Threads", args.threads)
    if 'Core Threads' in engine.options:  # Hiarcs
        engine.set_option("Core Threads", args.threads)

    # Connect to DGT board
    if args.dgt_port:
        logging.debug("Starting picochess with DGT board on [%s]", args.dgt_port)
        dgt.DGTBoard(args.dgt_port).start()
    else:
        logging.warning("No DGT board port provided")
        # Enable keyboard input and terminal display
        KeyboardInput().start()
        TerminalDisplay().start()

    # Save to PGN
    PgnDisplay("test.pgn").start()

    # Launch web server
    if(args.web_server):
        WebServer().start()

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
        for move in g.generate_legal_moves():
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
            Observable.fire(Event.BEST_MOVE, move=move.uci())

        global book_thread
        book_move = weighted_choice(book, game)
        Display.show(Message.RUN_CLOCK, turn=game.turn, time_control=time)
        time.run(game.turn)
        if book_move:
            Display.show(Message.BOOK_MOVE, move=book_move.uci())
            book_thread = threading.Timer(2, send_book_move, [book_move])
            book_thread.start()
        else:
            book_thread = None
            engine.set_position(game)
            engine.go(time.uci())
            Display.show(Message.SEARCH_STARTED)

    def stop_thinking():
        """
        Stop current search or book thread.
        :return:
        """
        if book_thread:
            book_thread.cancel()
        else:
            engine.stop(True)

    def check_game_state(game):
        """
        Check if the game has ended or not ; it also sends Message to Displays if the game has ended.
        :param game:
        :return: True is the game continues, False if it has ended
        """
        if game.is_stalemate():
            Display.show(Message.GAME_ENDS, result=GameResult.STALEMATE, moves=list(game.move_stack), color=game.turn)
            return False
        if game.is_insufficient_material():
            Display.show(Message.GAME_ENDS, result=GameResult.INSUFFICIENT_MATERIAL, moves=list(game.move_stack), color=game.turn)
            return False
        if game.is_game_over():
            Display.show(Message.GAME_ENDS, result=GameResult.MATE, moves=list(game.move_stack), color=game.turn)
            return False
        return True

    game = chess.Bitboard()  # Create the current game
    legal_fens = compute_legal_fens(game)  # Compute the legal FENs
    book = chess.polyglot.open_reader(get_opening_books()[8][1])  # Default opening book
    interaction_mode = Mode.PLAY_WHITE   # Interaction mode
    book_thread = None  # The thread that will fire book moves
    time_control = TimeControl(ClockMode.BLITZ, minutes_per_game=1)

    #Send the engine's UCI options to all Displays
    Display.show(Message.UCI_OPTION_LIST, options=engine.options)

    #Event loop
    while True:
        event = event_queue.get()
        logging.debug('Received event in event loop : %s', event)

        for case in switch(event):

            if case(Event.FEN):  # User sets a new position, convert it to a move if it is legal
                if event.fen in legal_fens:
                    # Check if we have to undo a previous move (sliding)
                    if (interaction_mode == Mode.PLAY_WHITE and game.turn == chess.BLACK) or (interaction_mode == Mode.PLAY_BLACK and game.turn == chess.WHITE):
                        stop_thinking()
                        game.pop()
                    legal_moves = list(game.generate_legal_moves())
                    Observable.fire(Event.USER_MOVE, move=legal_moves[legal_fens.index(event.fen)])
                elif event.fen == game.fen().split(' ')[0]:  # Player had done the computer move on the board
                    Display.show(Message.COMPUTER_MOVE_DONE_ON_BOARD)
                    if time_control.mode != ClockMode.FIXED_TIME:
                        Display.show(Message.RUN_CLOCK, turn=game.turn, time_control=time_control)
                        time_control.run(game.turn)
                elif event.fen == legal_fens.root:  # Allow user to take his move back while the engine is searching
                    stop_thinking()
                    game.pop()
                    Display.show(Message.USER_TAKE_BACK)
                break

            if case(Event.USER_MOVE):  # User sends a new move
                move = event.move
                logging.debug('User move [%s]', move)
                if not move in game.generate_legal_moves():
                    logging.warning('Illegal move [%s]', move)
                # Check if we are in play mode and it is player's turn
                elif (interaction_mode == Mode.PLAY_WHITE and game.turn == chess.WHITE) or (interaction_mode == Mode.PLAY_BLACK and game.turn == chess.BLACK):
                    time_control.stop()
                    game.push(move)
                    if check_game_state(game):
                        Display.show(Message.USER_MOVE, move=move, game=game)
                        think(time_control)
                break

            if case(Event.LEVEL):  # User sets a new level
                level = event.level
                logging.debug("Setting engine to level %i", level)
                engine.set_level(level)
                break

            if case(Event.NEW_GAME):  # User starts a new game
                if game.move_stack:
                    logging.debug("Starting a new game")
                    game = chess.Bitboard()
                    legal_fens = compute_legal_fens(game)
                    time_control.reset()
                    Display.show(Message.START_NEW_GAME)
                if interaction_mode == Mode.PLAY_BLACK:
                    think(time_control)
                break

            if case(Event.OPENING_BOOK):
                logging.debug("Changing opening book [%s]", get_opening_books()[event.book_index][1])
                book = chess.polyglot.open_reader(get_opening_books()[event.book_index][1])
                break

            if case(Event.BEST_MOVE):
                move = chess.Move.from_uci(event.move)
                # Check if we are in play mode and it is computer's turn
                if (interaction_mode == Mode.PLAY_WHITE and game.turn == chess.BLACK) or (interaction_mode == Mode.PLAY_BLACK and game.turn == chess.WHITE):
                    time_control.stop()
                    game.push(move)
                    Display.show(Message.COMPUTER_MOVE, move=move.uci(), game=game, time_control=time_control)
                    if check_game_state(game):
                        legal_fens = compute_legal_fens(game)
                break

            if case(Event.SET_MODE):
                Display.show(Message.INTERACTION_MODE, mode=event.mode)  # Usefull for pgn display device
                interaction_mode = event.mode
                break

            if case(Event.SET_TIME_CONTROL):
                time_control = event.time_control
                break

            if case(Event.OUT_OF_TIME):
                stop_thinking()
                Display.show(Message.GAME_ENDS, result=GameResult.TIME_CONTROL, moves=list(game.move_stack), color=event.color)
                break

            if case(Event.UCI_OPTION_SET):
                engine.set_option(event.name, event.value)
                break

            if case():  # Default
                logging.warning("Event not handled : [%s]", event)


if __name__ == '__main__':
    main()
