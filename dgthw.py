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
from dgtinterface import *
from dgtserial import *
from dgtlib import *
from utilities import *
from threading import Lock


class DgtHw(DgtInterface):
    def __init__(self, device, enable_board_leds, beep_level):
        super(DgtHw, self).__init__(enable_board_leds, beep_level)
        self.dgtserial = DgtSerial(device)
        self.dgtserial.run()

        self.lock = Lock()
        self.lib = DgtLib(self.dgtserial)
        self.startup_clock()
        self.dgtserial.startup_board()

    def startup_clock(self):
        # Get clock version
        command = [DgtCmd.DGT_CLOCK_MESSAGE, 0x03, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                   DgtClk.DGT_CMD_CLOCK_VERSION, DgtClk.DGT_CMD_CLOCK_END_MESSAGE]
        self.dgtserial.write_board_command(command)
        # self.lib.write(command)

    def _display_on_dgt_xl(self, text, beep=False):
        if not self.clock_found:  # This can only happen on the XL function
            logging.debug('Clock (still) not found. Ignore [%s]', text)
            self.startup_clock()
            return
        while len(text) < 6:
            text += ' '
        if len(text) > 6:
            logging.warning('DGT XL clock message too long [%s]', text)
        logging.debug(text)
        with self.lock:
            res = self.lib.set_text_xl(text, 0x03 if beep else 0x00, 0, 0)
            if res < 0:
                logging.warning('Finally failed %i', res)

    def _display_on_dgt_3000(self, text, beep=False):
        while len(text) < 8:
            text += ' '
        if len(text) > 8:
            logging.warning('DGT 3000 clock message too long [%s]', text)
        logging.debug(text)
        text = bytes(text, 'utf-8')
        with self.lock:
            res = self.lib.set_text_3k(text, 0x03 if beep else 0x00, 0, 0)
            if res < 0:
                logging.warning('Finally failed %i', res)

    def display_text_on_clock(self, text, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        if self.enable_dgt_3000:
            self._display_on_dgt_3000(text, beep)
        else:
            self._display_on_dgt_xl(text, beep)

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        if self.enable_dgt_3000:
            bit_board = Board(fen)
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
                self.lib.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x01, dgt_square, dgt_square])

    def clear_light_revelation_board(self):
        if self.enable_board_leds:
            self.lib.write([DgtCmd.DGT_SET_LEDS, 0x04, 0x00, 0, 63])

    def stop_clock(self):
        l_hms = self.time_left
        r_hms = self.time_right
        with self.lock:
            res = self.lib.set_and_run(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
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
            res = self.lib.set_and_run(lr, l_hms[0], l_hms[1], l_hms[2], rr, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = True

    def end_clock(self, force=False):
        if self.clock_running or force:
            self.lib.end_text()
        else:
            logging.debug('DGT clock isnt running - no need for endClock')
