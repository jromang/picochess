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

import chess
import time
import threading
import logging
from utilities import *


class TimeControl:
    def __init__(self, mode=ClockMode.FIXED_TIME, seconds_per_move=0, minutes_per_game=0, fischer_increment=0):
        super().__init__()
        self.mode = mode
        self.seconds_per_move = seconds_per_move
        self.minutes_per_game = minutes_per_game
        self.fischer_increment = fischer_increment
        self.timer = None
        self.reset()

    def reset(self):
        self.clock_time = {chess.WHITE: float(self.minutes_per_game * 60), chess.BLACK: float(self.minutes_per_game * 60)}  # Player remaining time, in seconds
        self.active_color = None

    def out_of_time(self):
        Observable.fire(Event.OUT_OF_TIME, color=self.active_color)

    def run(self, color):
        if self.mode in (ClockMode.BLITZ, ClockMode.FISCHER):
            self.active_color = color
            self.start_time = time.clock()
            self.timer = threading.Timer(self.clock_time[color], self.out_of_time)
            self.timer.start()

    def stop(self):
        if self.active_color is not None and self.mode in (ClockMode.BLITZ, ClockMode.FISCHER):
            self.clock_time[self.active_color] -= time.clock() - self.start_time
            self.timer.cancel()
            self.timer.join()
            self.active_color = None

    def uci(self):
        uci_string = ''
        if self.mode in (ClockMode.BLITZ, ClockMode.FISCHER):
            uci_string = 'wtime ' + str(int(self.clock_time[chess.WHITE] * 1000)) + ' btime ' + str(int(self.clock_time[chess.BLACK] * 1000))
            if self.mode == ClockMode.FISCHER:
                uci_string += ' winc ' + str(self.fischer_increment * 1000) + ' binc ' + str(self.fischer_increment * 1000)
        elif self.mode == ClockMode.FIXED_TIME:
            uci_string = 'movetime ' + str(self.seconds_per_move * 1000)
        return uci_string
