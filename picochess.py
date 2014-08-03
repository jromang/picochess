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
import dgt
import logging
import time
import uci


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

#def catch_move(e):
#    if e.type == 'bestmove':
#        print('BM:'+e.move)

#engine.subscribe(catch_move)
#engine.send('go depth 10')
#time.sleep(10)

#Connect to DGT board
if args.dgt_port:
    logging.debug("Starting picochess with DGT board on [%s]", args.dgt_port)
else:
    logging.warning("No DGT board port provided")

board = dgt.DGTBoard(args.dgt_port, send_board=True)


def dgt_observer(attrs):
        if attrs.type == dgt.FEN:
            logging.debug("FEN: {0}".format(attrs.message))
        elif attrs.type == dgt.BOARD:
            logging.debug("Board: ")
            logging.debug(attrs.message)
            # self.send_message_to_clock(['c','h','a','n','g','e'], False, False)
            # time.sleep(1)
            # self.send_message_to_clock(['b','o','a','r','d','c'], False, False)

board.subscribe(dgt_observer)
board.poll()