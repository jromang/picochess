#! /usr/bin/env python3

import argparse
import logging
import uci

#Command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dgt-port", type=str, help="enable dgt board on the given serial port such as /dev/ttyUSB0")
parser.add_argument("-e", "--engine", type=str, help="stockfish executable path", default="/usr/bin/stockfish")
parser.add_argument("-l", "--log-level", choices=['notset', 'debug', 'info', 'warning', 'error', 'critical'], default='warning', help="logging level")
parser.add_argument("-lf", "--log-file", type=str, help="log to the given file")
args = parser.parse_args()

#Enable logging
logging.basicConfig(filename=args.log_file, level=getattr(logging, args.log_level.upper()),
                    format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

#Startup tests
if args.dgt_port:
    logging.debug("Starting picochess with DGT board on [%s]", args.dgt_port)
else:
    logging.warning("No DGT board port provided")

#Load UCI engine
engine=uci.Stockfish(args.engine)