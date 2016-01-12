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

import logging
from chess import Board
from ctypes import *
from dgtinterface import *
from dgti2c import *
from utilities import *
from threading import Lock, Timer


class DGThelp(object):
    def __init__(self, device):
        super(DGThelp, self).__init__()
        self.dgti2c = DGTi2c(device)
        self.dgti2c.run()

        self.clock_lock = False  # from dgtserial.py
        self.startup_clock()

    def write(self, message):
        self.send_command(message)

    def send_command(self, message):
        mes = message[3] if message[0].value == DgtCmd.DGT_CLOCK_MESSAGE.value else message[0]
        if mes.value == DgtClk.DGT_CMD_CLOCK_ASCII.value:
            logging.debug(message[4:10])
        self.dgti2c.write_to_board(message)
        if message[0] == DgtCmd.DGT_CLOCK_MESSAGE:
            logging.debug('DGT clock locked')
            self.clock_lock = True

    def startup_clock(self):
        self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x03, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                    DgtClk.DGT_CMD_CLOCK_VERSION, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])  # Get clock version

    def display(self, text, beep, ld, rd):
        self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x0c, DgtClk.DGT_CMD_CLOCK_START_MESSAGE, DgtClk.DGT_CMD_CLOCK_ASCII,
                    text[0], text[1], text[2], text[3], text[4], text[5], text[6], text[7], 0x03 if beep else 0x01,
                    DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x03, DgtClk.DGT_CMD_CLOCK_START_MESSAGE, DgtClk.DGT_CMD_CLOCK_END,
                    DgtClk.DGT_CMD_CLOCK_END_MESSAGE])

    def setnrun(self, lr, lh, lm, ls, rr, rh, rm, rs):
        side = 0x04
        if lr == 1 and rr == 0:
            side = 0x01
        if lr == 0 and rr == 1:
            side = 0x02
        self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x0a, DgtClk.DGT_CMD_CLOCK_START_MESSAGE, DgtClk.DGT_CMD_CLOCK_SETNRUN,
                    lh, lm, ls, rh, rm, rs,
                    side, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x03, DgtClk.DGT_CMD_CLOCK_START_MESSAGE, DgtClk.DGT_CMD_CLOCK_END,
                    DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
