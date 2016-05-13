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

import chess
from dgtiface import *
from utilities import RepeatedTimer


class DgtVr(DgtIface):
    def __init__(self, dgtserial, dgttranslate, enable_revelation_leds):
        super(DgtVr, self).__init__(dgtserial, dgttranslate, enable_revelation_leds)
        # virtual lib
        self.rt = None
        self.time_side = None
        # setup virtual clock
        DisplayMsg.show(Message.DGT_CLOCK_VERSION(main_version=0, sub_version=0, attached="virtual"))

    # (START) dgtserial class simulation
    def runclock(self):
        if self.time_side == 1:
            h, m, s = self.time_left
            time_left = 3600*h + 60*m + s - 1
            if time_left <= 0:
                print('Clock flag: left')
                self.rt.stop()
            self.time_left = hours_minutes_seconds(time_left)
        else:
            h, m, s = self.time_right
            time_right = 3600*h + 60*m + s - 1
            if time_right <= 0:
                print('Clock flag: right')
                self.rt.stop()
            self.time_right = hours_minutes_seconds(time_right)
        if self.timer_running:
            print('Clock duration not run out')
        else:
            print('Clock time: {} - {}'.format(self.time_left, self.time_right))
        DisplayMsg.show(Message.DGT_CLOCK_TIME(time_left=self.time_left, time_right=self.time_right))
    # (END) dgtserial simulation class

    def display_move_on_clock(self, move, fen, side, beep=False):
        if self.enable_dgt_3000:
            bit_board = chess.Board(fen)
            text = bit_board.san(move)
        else:
            text = str(move)
        if side == 0x02:
            text = text.rjust(8 if self.enable_dgt_3000 else 6)
        logging.debug(text)
        print('Clock move: {} Beep: {}'. format(text, beep))

    def display_text_on_clock(self, text, beep=False):
        logging.debug(text)
        print('Clock text: {} Beep: {}'. format(text, beep))

    def stop_clock(self):
        if self.rt:
            print('Clock time stopped at {} - {}'. format(self.time_left, self.time_right))
            self.rt.stop()
        else:
            print('Clock not ready')
        self.clock_running = False

    def resume_clock(self, side):
        pass

    def start_clock(self, time_left, time_right, side):
        self.time_left = hours_minutes_seconds(time_left)
        self.time_right = hours_minutes_seconds(time_right)
        self.time_side = side

        print('Clock time started at {} - {}'. format(self.time_left, self.time_right))
        if self.rt:
            self.rt.stop()
        self.rt = RepeatedTimer(1, self.runclock)
        self.rt.start()
        self.clock_running = (side != 0x04)

    def light_squares_revelation_board(self, squares):
        pass

    def clear_light_revelation_board(self):
        pass

    def end_clock(self, force=False):
        if self.clock_running or force:
            pass
        else:
            logging.debug('Clock isnt running - no need for endClock')
