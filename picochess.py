#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dgt-port", type=str, help="enable dgt board on the given serial port such as /dev/ttyUSB0")
parser.parse_args()
