#! /usr/bin/env python3

import argparse
import logging
import os.path

#Command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dgt-port", type=str, help="enable dgt board on the given serial port such as /dev/ttyUSB0")
parser.add_argument("-e", "--engine", type=str, help="stockfish executable path", default="/usr/bin/stockfish")
parser.add_argument("-l", "--log-level", choices=['notset', 'debug', 'info', 'warning', 'error', 'critical'], default='warning', help="logging level")
args = parser.parse_args()

#Enable logging
logging.basicConfig(filename="picochess.log", level=getattr(logging, args.log_level.upper()))

#Startup tests
if args.dgt_port:
    logging.debug("Starting picochess with DGT board on ["+args.dgt_port+"]")
else:
    logging.warning("No DGT board port provided")
    
if not os.path.isfile(args.engine):
    logging.error("Engine not found ["+args.engine+"]")