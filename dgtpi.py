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
from dgti2c import *
from utilities import *


class DGTPi(DGTInterface):
    def __init__(self, device, enable_board_leds, beep_level):
        super(DGTPi, self).__init__(enable_board_leds, beep_level)
        self.dgti2c = DGTi2c(device)
        self.dgti2c.run()

        self.lock = Lock()
        # load the dgt3000 SO-file
        self.lib = ctypes.cdll.LoadLibrary("/home/pi/20151229/dgt3000.so")

    def _display_on_dgt_3000(self, text, beep=False):
        if len(text) > 11:
            logging.warning('DGT 3000 clock message too long [%s]', text)
        logging.debug(text)
        text = bytes(text, 'utf-8')

        self.lock.acquire()
        res = self.lib.dgt3000Display(text, 0x03 if beep else 0x01, 0, 0)
        if res < 0:
            logging.warning('Display returned error %i', res)
            res = self.lib.dgt3000Configure()
            if res < 0:
                logging.warning('Configure also failed %i', res)
            else:
                res = self.lib.dgt3000Display(text, 0x03 if beep else 0x00, 0, 0)
        if res < 0:
            logging.warning('Finally failed %i', res)
        self.lock.release()

    def display_text_on_clock(self, text, dgt_xl_text=None, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        self._display_on_dgt_3000(text, beep)

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        bit_board = chess.Board(fen)
        text = bit_board.san(move)
        self._display_on_dgt_3000(text, beep)

    def light_squares_revelation_board(self, squares):
        pass

    def clear_light_revelation_board(self):
        pass

    def stop_clock(self):
        l_hms = hours_minutes_seconds(self.time_left)
        r_hms = hours_minutes_seconds(self.time_right)
        self.lock.acquire()
        res = self.lib.dgt3000SetNRun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
        if res < 0:
            logging.warning('SetNRun returned error %i', res)
            res = self.lib.dgt3000Configure()
            if res < 0:
                logging.warning('Configure also failed %i', res)
            else:
                res = self.lib.dgt3000SetNRun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
        if res < 0:
            logging.warning('Finally failed %i', res)
        else:
            self.clock_running = False
        self.lock.release()

    def start_clock(self, time_left, time_right, side):
        l_hms = hours_minutes_seconds(time_left)
        r_hms = hours_minutes_seconds(time_right)
        self.time_left = l_hms
        self.time_right = r_hms

        self.lock.acquire()
        res = self.lib.dgt3000SetNRun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
        if res < 0:
            logging.warning('SetNRun returned error %i', res)
            res = self.lib.dgt3000Configure()
            if res < 0:
                logging.warning('Configure also failed %i', res)
            else:
                res = self.lib.dgt3000SetNRun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
        if res < 0:
            logging.warning('Finally failed %i', res)
        else:
            self.clock_running = False
        self.lock.release()

    # def serialnr_board(self):
    #     self.dgti2c.write_to_board([DgtCmd.DGT_RETURN_SERIALNR])
