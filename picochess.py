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

import argparse
import chess
import chess.polyglot
import dgtv2
import logging
import uci
from utilities import *


#Command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dgt-port", type=str, help="enable dgt board on the given serial port such as /dev/ttyUSB0")
parser.add_argument("-e", "--engine", type=str, help="stockfish executable path", default="/usr/bin/stockfish")
parser.add_argument("-hs", "--hash-size", type=int, help="hashtable size in MB (default:64)", default=64)
parser.add_argument("-t", "--threads", type=int, help="number of engine threads (default:1)", default=1)
parser.add_argument("-l", "--log-level", choices=['notset', 'debug', 'info', 'warning', 'error', 'critical'], default='warning', help="logging level")
parser.add_argument("-lf", "--log-file", type=str, help="log to the given file")
parser.add_argument("-r", "--remote", type=str, help="remote server running the engine")
parser.add_argument("-u", "--user", type=str, help="remote user on server running the engine")
parser.add_argument("-p", "--password", type=str, help="password for the remote user")
parser.add_argument("-k", "--key-file", type=str, help="key file used to connect to the remote server")
parser.add_argument("-pgn", "--pgn-file", type=str, help="pgn file used to store the games")
args = parser.parse_args()

#Enable logging
logging.basicConfig(filename=args.log_file, level=getattr(logging, args.log_level.upper()),
                    format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

#Load UCI engine
engine = uci.Engine(args.engine, hostname=args.remote, username=args.user, key_file=args.key_file, password=args.password)
logging.debug('Loaded engine [%s]', engine.name)
logging.debug('Supported options [%s]', engine.options)
if 'Hash' in engine.options:
    engine.set_option("Hash", args.hash_size)
if 'Threads' in engine.options:
    engine.set_option("Threads", args.threads)
engine.send('go depth 20')

#Connect to DGT board
board = None
if args.dgt_port:
    logging.debug("Starting picochess with DGT board on [%s]", args.dgt_port)
    board = dgtv2.DGTBoard(args.dgt_port)
    board.start()
else:
    logging.warning("No DGT board port provided")

#Game data
def compute_legal_fens(g):
    fens = []
    for move in g.generate_legal_moves():
        g.push(move)
        fens.append(g.fen().split(' ')[0])
        g.pop()
    return fens

game = chess.Bitboard()
legal_fens = compute_legal_fens(game)

#Opening book
book = chess.polyglot.open_reader(get_opening_books()[8][1])  # Default opening book

#Interacation mode
interaction_mode = Mode.PLAY

#Event loop
while True:
    event = event_queue.get()
    logging.debug('Received event in event loop : %s', event)

    for case in switch(event):

        if case(Event.FEN):  # User sets a new position, convert it to a move if it is legal
            if event.parameter in legal_fens:
                legal_moves = list(game.generate_legal_moves())
                Observable.fire(Event.USER_MOVE, legal_moves[legal_fens.index(event.parameter)])
            break

        if case(Event.USER_MOVE):  # User sends a new move
            move = event.parameter
            logging.debug('User move [%s]', move)
            if not move in game.generate_legal_moves():
                logging.warning('Illegal move [%s]', move)
            break

        if case(Event.LEVEL):  # User sets a new level
            level = event.parameter
            logging.debug("Setting engine to level %i", level)
            engine.set_level(level)
            break

        if case(Event.NEW_GAME):  # User starts a new game
            logging.debug("Starting a new game")
            game = chess.Bitboard()
            legal_fens = compute_legal_fens(game)
            break

        if case(Event.OPENING_BOOK):
            logging.debug("Changing opening book [%s]", get_opening_books()[event.parameter][1])
            book = chess.polyglot.open_reader(get_opening_books()[event.parameter][1])
            break

        if case(Event.BEST_MOVE):
            Display.show(Message.COMPUTER_MOVE, event.parameter)
            break

        if case(Event.SET_MODE):
            Display.show(Message.INTERACTION_MODE, event.parameter)  # Usefull for pgn display device
            interaction_mode = event.parameter
            break

        if case():  # Default
            logging.warning("Event not handled : [%s]", event)