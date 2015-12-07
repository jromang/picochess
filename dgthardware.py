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
import chess
from dgtinterface import *
from dgtserial import *
from utilities import *


class DGTHardware(DGTInterface):
    def __init__(self, device, enable_board_leds, disable_dgt_clock_beep):
        super(DGTHardware, self).__init__(enable_board_leds, disable_dgt_clock_beep)
        self.dgtserial = DGTSerial(device)
        self.dgtserial.run()

    def write(self, message):
        self.dgtserial.write(message)

    def _display_on_dgt_xl(self, text, beep=False):
        if self.clock_found:
            while len(text) < 6:
                text += ' '
            if len(text) > 6:
                logging.warning('DGT XL clock message too long [%s]', text)
            logging.debug(text)
            self.write(
                [DgtCmd.DGT_CLOCK_MESSAGE, 0x0b, DgtClk.DGT_CMD_CLOCK_START_MESSAGE, DgtClk.DGT_CMD_CLOCK_DISPLAY,
                 text[2], text[1], text[0], text[5], text[4], text[3], 0x00, 0x03 if beep else 0x01,
                 DgtClk.DGT_CMD_CLOCK_END_MESSAGE])

    def _display_on_dgt_3000(self, text, beep=False):
        if self.clock_found:
            while len(text) < 8:
                text += ' '
            if len(text) > 8:
                logging.warning('DGT 3000 clock message too long [%s]', text)
            logging.debug(text)
            text = bytes(text, 'utf-8')
            self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x0c, DgtClk.DGT_CMD_CLOCK_START_MESSAGE, DgtClk.DGT_CMD_CLOCK_ASCII,
                        text[0], text[1], text[2], text[3], text[4], text[5], text[6], text[7], 0x03 if beep else 0x01,
                        DgtClk.DGT_CMD_CLOCK_END_MESSAGE])

    def display_text_on_clock(self, text, dgt_xl_text=None, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        if self.enable_dgt_3000:
            self._display_on_dgt_3000(text, beep)
        else:
            if dgt_xl_text:
                text = dgt_xl_text
            self._display_on_dgt_xl(text, beep)

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        if self.enable_dgt_3000:
            bit_board = chess.Board(fen)
            text = bit_board.san(move)
            self._display_on_dgt_3000(text, beep)
        else:
            text = ' ' + move.uci()
            self._display_on_dgt_xl(text, beep)

    def light_squares_revelation_board(self, squares):
        if self.enable_board_leds:
            for sq in squares:
                dgt_square = (8 - int(sq[1])) * 8 + ord(sq[0]) - ord('a')
                logging.debug("REV2 light on square %s(%i)", sq, dgt_square)
                self.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x01, dgt_square, dgt_square])

    def clear_light_revelation_board(self):
        if self.enable_board_leds:
            self.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x00, 0, 63])

    def stop_clock(self):
        l_hms = self.time_left
        r_hms = self.time_right
        self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x0a, DgtClk.DGT_CMD_CLOCK_START_MESSAGE, DgtClk.DGT_CMD_CLOCK_SETNRUN,
                    l_hms[0], l_hms[1], l_hms[2], r_hms[0], r_hms[1], r_hms[2],
                    0x04 | 0x01, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])

    def start_clock(self, time_left, time_right, side):
        l_hms = hours_minutes_seconds(time_left)
        r_hms = hours_minutes_seconds(time_right)
        self.time_left = l_hms
        self.time_right = r_hms
        self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x0a, DgtClk.DGT_CMD_CLOCK_START_MESSAGE, DgtClk.DGT_CMD_CLOCK_SETNRUN,
                    l_hms[0], l_hms[1], l_hms[2], r_hms[0], r_hms[1], r_hms[2],
                    side, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        self.write([DgtCmd.DGT_CLOCK_MESSAGE, 0x03, DgtClk.DGT_CMD_CLOCK_START_MESSAGE, DgtClk.DGT_CMD_CLOCK_END,
                    DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
