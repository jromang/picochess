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
from dgthelp import *
from utilities import *
from threading import Lock, Timer

char_to_DGTXL = {
    '0': 0x01 | 0x02 | 0x20 | 0x08 | 0x04 | 0x10, '1': 0x02 | 0x04, '2': 0x01 | 0x40 | 0x08 | 0x02 | 0x10,
    '3': 0x01 | 0x40 | 0x08 | 0x02 | 0x04, '4': 0x20 | 0x04 | 0x40 | 0x02, '5': 0x01 | 0x40 | 0x08 | 0x20 | 0x04,
    '6': 0x01 | 0x40 | 0x08 | 0x20 | 0x04 | 0x10, '7': 0x02 | 0x04 | 0x01,
    '8': 0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10 | 0x08, '9': 0x01 | 0x40 | 0x08 | 0x02 | 0x04 | 0x20,
    'a': 0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10, 'b': 0x20 | 0x04 | 0x40 | 0x08 | 0x10, 'c': 0x01 | 0x20 | 0x10 | 0x08,
    'd': 0x10 | 0x40 | 0x08 | 0x02 | 0x04, 'e': 0x01 | 0x40 | 0x08 | 0x20 | 0x10, 'f': 0x01 | 0x40 | 0x20 | 0x10,
    'g': 0x01 | 0x20 | 0x10 | 0x08 | 0x04, 'h': 0x20 | 0x10 | 0x04 | 0x40, 'i': 0x02 | 0x04,
    'j': 0x02 | 0x04 | 0x08 | 0x10, 'k': 0x01 | 0x20 | 0x40 | 0x04 | 0x10, 'l': 0x20 | 0x10 | 0x08,
    'm': 0x01 | 0x40 | 0x04 | 0x10, 'n': 0x40 | 0x04 | 0x10, 'o': 0x40 | 0x04 | 0x10 | 0x08,
    'p': 0x01 | 0x40 | 0x20 | 0x10 | 0x02, 'q': 0x01 | 0x40 | 0x20 | 0x04 | 0x02, 'r': 0x40 | 0x10,
    's': 0x01 | 0x40 | 0x08 | 0x20 | 0x04, 't': 0x20 | 0x10 | 0x08 | 0x40, 'u': 0x08 | 0x02 | 0x20 | 0x04 | 0x10,
    'v': 0x08 | 0x02 | 0x20, 'w': 0x40 | 0x08 | 0x20 | 0x02, 'x': 0x20 | 0x10 | 0x04 | 0x40 | 0x02,
    'y': 0x20 | 0x08 | 0x04 | 0x40 | 0x02, 'z': 0x01 | 0x40 | 0x08 | 0x02 | 0x10, ' ': 0x00, '-': 0x40
}


class DGThw(DGTInterface):
    def __init__(self, device, enable_board_leds, beep_level):
        super(DGThw, self).__init__(enable_board_leds, beep_level)
        self.lock = Lock()
        self.lib = DGThelp(device)

    def _display_on_dgt_3000(self, text, beep=False):
        if len(text) > 8:
            logging.warning('DGT 3000 clock message too long [%s]', text)
        logging.debug(text)
        text = bytes(text, 'utf-8')
        with self.lock:
            res = self.lib.display(text, 0x03 if beep else 0x01, 0, 0)
            if res < 0:
                logging.warning('Finally failed %i', res)

    def display_text_on_clock(self, text, dgt_xl_text=None, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        self._display_on_dgt_3000(text, beep)

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        bit_board = Board(fen)
        text = bit_board.san(move)
        self._display_on_dgt_3000(text, beep)

    def light_squares_revelation_board(self, squares):
        if self.enable_board_leds:
            for sq in squares:
                dgt_square = (8 - int(sq[1])) * 8 + ord(sq[0]) - ord('a')
                logging.debug("REV2 light on square %s(%i)", sq, dgt_square)
                self.lib.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x01, dgt_square, dgt_square])

    def clear_light_revelation_board(self):
        if self.enable_board_leds:
            self.lib.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x00, 0, 63])

    def stop_clock(self):
        l_hms = self.time_left
        r_hms = self.time_right
        with self.lock:
            res = self.lib.setnrun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = False

    def start_clock(self, time_left, time_right, side):
        l_hms = hours_minutes_seconds(time_left)
        r_hms = hours_minutes_seconds(time_right)
        self.time_left = l_hms
        self.time_right = r_hms
        if side == 0x01:
            lr = 1
            rr = 0
        else:
            lr = 0
            rr = 1
        with self.lock:
            res = self.lib.setnrun(lr, l_hms[0], l_hms[1], l_hms[2], rr, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = True

    def end_clock(self):
        if self.clock_running:
            self.lib.end_clock()
        else:
            logging.debug('clock isnt running - no need for stop')
