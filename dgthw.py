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

from chess import Board
from dgtiface import *
from dgtlib import *
from utilities import *
from threading import Lock


class DgtHw(DgtIface):
    def __init__(self, dgtserial, dgttranslate, enable_revelation_leds):
        super(DgtHw, self).__init__(dgtserial, dgttranslate, enable_revelation_leds)

        self.lib_lock = Lock()
        self.lib = DgtLib(self.dgtserial)
        self.dgtserial.run()

    def _display_on_dgt_xl(self, text, beep=False):
        if not self.clock_found:  # This can only happen on the XL function
            logging.debug('DGT clock (still) not found. Ignore [%s]', text)
            self.dgtserial.startup_serial_clock()
            return
        text = text.ljust(6)
        if len(text) > 6:
            logging.warning('DGT XL clock message too long [%s]', text)
        logging.debug(text)
        with self.lib_lock:
            res = self.lib.set_text_xl(text, 0x03 if beep else 0x00, 0, 0)
            if res < 0:
                logging.warning('Finally failed %i', res)

    def _display_on_dgt_3000(self, text, beep=False):
        text = text.ljust(8)
        if len(text) > 8:
            logging.warning('DGT 3000 clock message too long [%s]', text)
        logging.debug(text)
        text = bytes(text, 'utf-8')
        with self.lib_lock:
            res = self.lib.set_text_3k(text, 0x03 if beep else 0x00, 0, 0)
            if res < 0:
                logging.warning('Finally failed %i', res)

    def display_text_on_clock(self, text, beep=False):
        if self.enable_dgt_3000:
            self._display_on_dgt_3000(text, beep)
        else:
            self._display_on_dgt_xl(text, beep)

    def display_move_on_clock(self, move, fen, side, beep=False):
        if self.enable_dgt_3000:
            bit_board = Board(fen)
            move_text = bit_board.san(move)
            if side == 0x02:
                move_text = move_text.rjust(8)
            text = self.dgttranslate.move(move_text)
            self._display_on_dgt_3000(text, beep)
        else:
            move_text = move.uci()
            if side == 0x02:
                move_text = move_text.rjust(6)
            self._display_on_dgt_xl(move_text, beep)

    def display_time_on_clock(self, force=False):
        if self.clock_running or force:
            self.lib.end_text()
        else:
            logging.debug('DGT clock isnt running - no need for endClock')

    def light_squares_revelation_board(self, squares):
        if self.enable_revelation_leds:
            for sq in squares:
                dgt_square = (8 - int(sq[1])) * 8 + ord(sq[0]) - ord('a')
                logging.debug("REV2 light on square %s", sq)
                self.lib.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x01, dgt_square, dgt_square])

    def clear_light_revelation_board(self):
        if self.enable_revelation_leds:
            self.lib.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x00, 0, 63])

    def stop_clock(self):
        self.resume_clock(0x04)

    def resume_clock(self, side):
        l_hms = self.time_left
        r_hms = self.time_right
        if l_hms is None or r_hms is None:
            logging.debug('time values not set - abort function')
            return

        lr = rr = 0
        if side == 0x01:
            lr = 1
        if side == 0x02:
            rr = 1
        with self.lib_lock:
            res = self.lib.set_and_run(lr, l_hms[0], l_hms[1], l_hms[2], rr, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = (side != 0x04)

    def start_clock(self, time_left, time_right, side):
        self.time_left = hours_minutes_seconds(time_left)
        self.time_right = hours_minutes_seconds(time_right)
        self.resume_clock(side)
