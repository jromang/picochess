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
    def __init__(self, dgtserial, dgttranslate):
        super(DgtHw, self).__init__(dgtserial, dgttranslate)

        self.lib_lock = Lock()
        self.lib = DgtLib(self.dgtserial)
        self.dgtserial.run()

    def _display_on_dgt_xl(self, text, beep=False, left_dots=ClockDots.NONE, right_dots=ClockDots.NONE):
        if not self.clock_found:  # This can only happen on the XL function
            logging.debug('DGT clock (still) not found. Ignore [%s]', text)
            self.dgtserial.startup_serial_clock()
            return
        text = text.ljust(6)
        if len(text) > 6:
            logging.warning('DGT XL clock message too long [%s]', text)
        logging.debug(text)
        with self.lib_lock:
            res = self.lib.set_text_xl(text, 0x03 if beep else 0x00, left_dots, right_dots)
            if not res:
                logging.warning('Finally failed %i', res)

    def _display_on_dgt_3000(self, text, beep=False, left_dots=ClockDots.NONE, right_dots=ClockDots.NONE):
        text = text.ljust(8)
        if len(text) > 8:
            logging.warning('DGT 3000 clock message too long [%s]', text)
        logging.debug(text)
        text = bytes(text, 'utf-8')
        with self.lib_lock:
            res = self.lib.set_text_3k(text, 0x03 if beep else 0x00, left_dots, right_dots)
            if not res:
                logging.warning('Finally failed %i', res)

    def display_text_on_clock(self, message):
        if 'ser' not in message.devs:
            return
        display_m = self.enable_dgt_3000 and not self.dgtserial.enable_revelation_leds
        text = message.m if display_m else message.s

        if text is None:
            text = message.l if display_m else message.m
        left_dots = message.ld if hasattr(message, 'ld') else ClockDots.NONE
        right_dots = message.rd if hasattr(message, 'rd') else ClockDots.NONE

        if display_m:
            self._display_on_dgt_3000(text, message.beep, left_dots, right_dots)
        else:
            self._display_on_dgt_xl(text, message.beep, left_dots, right_dots)

    def display_move_on_clock(self, message):
        left_dots = message.ld if hasattr(message, 'ld') else ClockDots.NONE
        right_dots = message.rd if hasattr(message, 'rd') else ClockDots.NONE
        display_m = self.enable_dgt_3000 and not self.dgtserial.enable_revelation_leds
        if display_m:
            bit_board = Board(message.fen)
            move_text = bit_board.san(message.move)
            if message.side == ClockSide.RIGHT:
                move_text = move_text.rjust(8)
            text = self.dgttranslate.move(move_text)
            self._display_on_dgt_3000(text, message.beep, left_dots, right_dots)
        else:
            move_text = message.move.uci()
            if message.side == ClockSide.RIGHT:
                move_text = move_text.rjust(6)
            self._display_on_dgt_xl(move_text, message.beep, left_dots, right_dots)

    def display_time_on_clock(self, force=False):
        if self.clock_running or force:
            with self.lib_lock:
                self.lib.end_text()
        else:
            logging.debug('DGT clock isnt running - no need for endClock')

    def light_squares_revelation_board(self, uci_move):
        if self.dgtserial.enable_revelation_leds:
            logging.debug("REV2 lights on move {}".format(uci_move))
            fr = (8 - int(uci_move[1])) * 8 + ord(uci_move[0]) - ord('a')
            to = (8 - int(uci_move[3])) * 8 + ord(uci_move[2]) - ord('a')
            self.lib.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x01, fr, to, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])

    def clear_light_revelation_board(self):
        if self.dgtserial.enable_revelation_leds:
            logging.debug('REV2 lights turned off')
            self.lib.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x00, 0, 63, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])

    def stop_clock(self):
        self.resume_clock(ClockSide.NONE)

    def resume_clock(self, side):
        l_hms = self.time_left
        r_hms = self.time_right
        if l_hms is None or r_hms is None:
            logging.debug('time values not set - abort function')
            return

        lr = rr = 0
        if side == ClockSide.LEFT:
            lr = 1
        if side == ClockSide.RIGHT:
            rr = 1
        with self.lib_lock:
            res = self.lib.set_and_run(lr, l_hms[0], l_hms[1], l_hms[2], rr, r_hms[0], r_hms[1], r_hms[2])
            if not res:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = (side != ClockSide.NONE)
            # this is needed for some(!) clocks
            self.lib.end_text()

    def start_clock(self, time_left, time_right, side):
        self.time_left = hours_minutes_seconds(time_left)
        self.time_right = hours_minutes_seconds(time_right)
        self.resume_clock(side)
