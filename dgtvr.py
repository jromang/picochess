# Copyright (C) 2013-2017 Jean-Francois Romang (jromang@posteo.de)
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
from dgtiface import DgtIface
from utilities import *
import time


class DgtVr(DgtIface):
    def __init__(self, dgttranslate, msg_lock, dgtboard):
        super(DgtVr, self).__init__(dgttranslate, msg_lock, dgtboard)
        # virtual lib
        self.rt = None
        self.time_side = ClockSide.NONE
        # setup virtual clock
        self.enable_dgt_pi = dgtboard.is_pi
        main = 2 if dgtboard.is_pi else 0
        DisplayMsg.show(Message.DGT_CLOCK_VERSION(main=main, sub=0, dev='web', text=None))

    # (START) dgtserial class simulation
    def _runclock(self):
        if self.time_side == ClockSide.LEFT:
            h, m, s = self.time_left
            time_left = 3600*h + 60*m + s - 1
            if time_left <= 0:
                print('\033[1;31;40m<{}> [vir] clock flag: left\033[1;37;40m'. format(time.time()))
                self.rt.stop()
            self.time_left = hours_minutes_seconds(time_left)
        if self.time_side == ClockSide.RIGHT:
            h, m, s = self.time_right
            time_right = 3600*h + 60*m + s - 1
            if time_right <= 0:
                print('\033[1;31;40m<{}> [vir] clock flag: right\033[1;37;40m'. format(time.time()))
                self.rt.stop()
            self.time_right = hours_minutes_seconds(time_right)
        if self.maxtimer_running:
            print('\033[1;32;40m<{}> [vir] clock maxtime not run out\033[1;37;40m'. format(time.time()))
        else:
            print('\033[1;34;40m<{}> [vir] clock time: {} - {}\033[1;37;40m'.format(time.time(), self.time_left, self.time_right))
        DisplayMsg.show(Message.DGT_CLOCK_TIME(time_left=self.time_left, time_right=self.time_right, dev='web'))
    # (END) dgtserial simulation class

    def display_move_on_clock(self, message):
        if self.enable_dgt_3000 or self.enable_dgt_pi:
            bit_board, text = self.get_san(message, not self.enable_dgt_pi)
            if self.enable_dgt_pi:
                text = '{:3d}.{:s}'.format(bit_board.fullmove_number, text)
            else:
                text = '{:2d}.{:s}'.format(bit_board.fullmove_number % 100, text)
        else:
            text = str(message.move)
            if message.side == ClockSide.RIGHT:
                text = text.rjust(6)

        logging.debug(text)
        print('\033[1;34;40m<{}> [vir] clock move: {} Beep: {}\033[1;37;40m'. format(time.time(), text, message.beep))

    def display_text_on_clock(self, message):
        if self.enable_dgt_pi:
            text = message.l
        else:
            text = message.m if self.enable_dgt_3000 else message.s
        if text is None:
            text = message.m

        logging.debug(text)
        print('\033[1;34;40m<{}> [vir] clock text: {} Beep: {}\033[1;37;40m'. format(time.time(), text, message.beep))

    def display_time_on_clock(self, force=False):
        if self.clock_running or force:
            print('\033[1;32;40m<{}> [vir] clock showing time again - running state: {}\033[1;37;40m'. format(time.time(), self.clock_running))
        else:
            logging.debug('[vir] clock isnt running - no need for endText')

    def stop_clock(self, devs: set):
        if self.rt:
            print('\033[1;32;40m<{}> [vir] clock time stopped at {} - {}\033[1;37;40m'. format(time.time(), self.time_left, self.time_right))
            self.rt.stop()
        else:
            print('\033[1;36;40m<{}> [vir] clock not ready\033[1;37;40m'. format(time.time()))
        self._resume_clock(ClockSide.NONE)

    def _resume_clock(self, side: ClockSide):
        self.clock_running = (side != ClockSide.NONE)

    def start_clock(self, time_left: int, time_right: int, side: ClockSide, devs: set):
        self.time_left = hours_minutes_seconds(time_left)
        self.time_right = hours_minutes_seconds(time_right)
        self.time_side = side

        print('\033[1;32;40m<{}> [vir] clock time started at {} - {} on {}\033[1;37;40m'. format(time.time(), self.time_left, self.time_right, side))
        if self.rt:
            self.rt.stop()
        if side != ClockSide.NONE:
            self.rt = RepeatedTimer(1, self._runclock)
            self.rt.start()
        self._resume_clock(side)

    def light_squares_revelation_board(self, squares):
        pass

    def clear_light_revelation_board(self):
        pass

