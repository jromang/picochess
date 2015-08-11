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


class DGTHardware(DGTInterface, DGTSerial):
    def __init__(self, device, enable_board_leds, enable_dgt_3000, disable_dgt_clock_beep):
        super(DGTHardware, self).__init__(device, enable_board_leds, enable_dgt_3000, disable_dgt_clock_beep)
        self.displayed_text = None  # The current clock display or None if in ClockNRun mode or unknown text
        self.clock_found = True
        # DGTSerial(device, enable_dgt_3000).start()
        DGTSerial(device, enable_dgt_3000).run()

    def _display_on_dgt_xl(self, text, beep=False):
        if self.clock_found and not self.enable_dgt_3000:
            while len(text) < 6:
                text += ' '
            if len(text) > 6:
                logging.warning('DGT XL clock message too long [%s]', text)
            logging.debug(text)
            self.write(
                [Commands.DGT_CLOCK_MESSAGE, 0x0b, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_DISPLAY,
                 text[2], text[1], text[0], text[5], text[4], text[3], 0x00, 0x03 if beep else 0x01,
                 Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def _display_on_dgt_3000(self, text, beep=False):
        if self.enable_dgt_3000:
            while len(text) < 8:
                text += ' '
            if len(text) > 8:
                logging.warning('DGT 3000 clock message too long [%s]', text)
            logging.debug(text)
            text = bytes(text, 'utf-8')
            self.write([Commands.DGT_CLOCK_MESSAGE, 0x0c, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_ASCII,
                        text[0], text[1], text[2], text[3], text[4], text[5], text[6], text[7], 0x03 if beep else 0x01,
                        Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def get_beep_level(self, beeplevel):
        if beeplevel == BeepLevel.YES:
            return True
        if beeplevel == BeepLevel.NO:
            return False
        return not self.disable_dgt_clock_beep

    def display_text_on_clock(self, text, dgt_xl_text=None, beep=BeepLevel.CONFIG, force=True):
        beep = self.get_beep_level(beep)
        if self.enable_dgt_3000:
            if force or self.displayed_text != text:
                self._display_on_dgt_3000(text, beep)
        else:
            if dgt_xl_text:
                text = dgt_xl_text
            if force or self.displayed_text != text:
                self._display_on_dgt_xl(text, beep)
        self.displayed_text = text

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG, force=True):
        beep = self.get_beep_level(beep)
        if self.enable_dgt_3000:
            bit_board = chess.Board(fen)
            text = bit_board.san(move)
            if force or self.displayed_text != text:
                self._display_on_dgt_3000(text, beep)
        else:
            text = ' ' + move.uci()
            if force or self.displayed_text != text:
                self._display_on_dgt_xl(text, beep)
        self.displayed_text = text

    def light_squares_revelation_board(self, squares):
        if self.enable_board_leds:
            for sq in squares:
                dgt_square = (8 - int(sq[1])) * 8 + ord(sq[0]) - ord('a')
                logging.debug("REV2 light on square %s(%i)", sq, dgt_square)
                self.write([Commands.DGT_SET_LEDS, 0x04, 0x01, dgt_square, dgt_square])

    def clear_light_revelation_board(self):
        if self.enable_board_leds:
            self.write([Commands.DGT_SET_LEDS, 0x04, 0x00, 0, 63])

    def stop_clock(self):
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
                    0, 0, 0, 0, 0, 0,
                    0x04 | 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def start_clock(self, time_left, time_right, side):
        l_hms = hours_minutes_seconds(time_left)
        r_hms = hours_minutes_seconds(time_right)
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
                    l_hms[0], l_hms[1], l_hms[2], r_hms[0], r_hms[1], r_hms[2],
                    side, Clock.DGT_CMD_CLOCK_END_MESSAGE])
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x03, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_END,
                    Clock.DGT_CMD_CLOCK_END_MESSAGE])
