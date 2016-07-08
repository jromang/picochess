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

from utilities import *
import time


class DgtLib(object):

    """This class simulates DGT's SO-lib File with similar API."""

    def __init__(self, dgtserial):
        super(DgtLib, self).__init__()
        self.dgtserial = dgtserial

    def wait(self):
        while self.dgtserial.clock_lock:
            time.sleep(0.1)

    def write(self, command):
        return self.dgtserial.write_board_command(command)

    def set_text_3k(self, text, beep, ld, rd):
        self.wait()
        res = self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x0c, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                          DgtClk.DGT_CMD_CLOCK_ASCII,
                          text[0], text[1], text[2], text[3], text[4], text[5], text[6], text[7], beep,
                          DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        return res

    def set_text_xl(self, text, beep, ld, rd):
        self.wait()
        icn = ((rd & 0x07) | (ld << 3) & 0x38)
        res = self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x0b, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                          DgtClk.DGT_CMD_CLOCK_DISPLAY,
                          text[2], text[1], text[0], text[5], text[4], text[3], icn, beep,
                          DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        return res

    def set_and_run(self, lr, lh, lm, ls, rr, rh, rm, rs):
        self.wait()
        side = ClockSide.NONE
        if lr == 1 and rr == 0:
            side = ClockSide.LEFT
        if lr == 0 and rr == 1:
            side = ClockSide.RIGHT
        res = self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x0a, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                          DgtClk.DGT_CMD_CLOCK_SETNRUN,
                          lh, lm, ls, rh, rm, rs, side,
                          DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        return res

    def end_text(self):
        self.wait()
        res = self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x03, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                          DgtClk.DGT_CMD_CLOCK_END,
                          DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        return res
