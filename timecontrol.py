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
import copy


class TimeControl(object):
    def __init__(self, mode=ClockMode.FIXED_TIME, seconds_per_move=0, minutes_per_game=0, fischer_increment=0):
        super(TimeControl, self).__init__()
        self.mode = mode
        self.seconds_per_move = seconds_per_move
        self.minutes_per_game = minutes_per_game
        self.fischer_increment = fischer_increment
        self.timer = None
        self.run_color = None
        self.reset()

    def reset(self):
        """Resets the clock's times for both players"""
        self.clock_time = {chess.WHITE: float(self.minutes_per_game * 60),
                           chess.BLACK: float(self.minutes_per_game * 60)}  # Player remaining time, in seconds
        self.active_color = None

    def out_of_time(self, time_start):
        """Fires an OUT_OF_TIME event"""
        if self.active_color is not None:
            logging.debug(
                'Firing an OUT_OF_TIME event, current clock time (before subtracting) is {0} and color is {1}, out of time event started from {2}'.format(
                    self.clock_time[self.active_color], self.active_color, time_start))
            Observable.fire(Event.OUT_OF_TIME, color=self.active_color)

    def run(self, color):
        if self.mode in (ClockMode.BLITZ, ClockMode.FISCHER):
            self.active_color = color
            self.start_time = time.time()
            # logging.debug("start time is {0}".format(self.start_time))

            if self.mode == ClockMode.FISCHER:
                self.clock_time[color] += self.fischer_increment
            # logging.debug("Time left is {0}".format(self.clock_time[color]))

            # Only start thread if thread is not already started for same color, and the player has not already lost on time
            if self.clock_time[color] > 0 and self.active_color is not None and self.run_color != self.active_color:
                self.timer = threading.Timer(copy.copy(self.clock_time[color]), self.out_of_time,
                                             [copy.copy(self.clock_time[color])])
                self.timer.start()
                self.run_color = self.active_color
                # logging.info("Started out of time event at {0} for {1}".format(copy.copy(self.clock_time[color]), color))

    def stop(self):
        """Stop the clocks"""
        if self.active_color is not None and self.mode in (ClockMode.BLITZ, ClockMode.FISCHER):
            self.timer.cancel()
            # if self.timer.finished:
            #     logging.info("Timer thread finished!")
            #     # logging.info("After cancelling Thread state is {0}".format(self.timer.finished))
            self.timer.join()

            # logging.info("Cancelled out of time event")
            self.clock_time[self.active_color] -= time.time() - self.start_time
            # logging.debug("updated time.clock is {0}".format(self.clock_time[self.active_color]))
            self.active_color = None

    def is_ticking(self):
        return self.active_color is not None

    def uci(self):
        """Returns remaining time for both players in an UCI dict"""
        uci_dict = {}
        if self.mode in (ClockMode.BLITZ, ClockMode.FISCHER):
            uci_dict['wtime'] = str(int(self.clock_time[chess.WHITE] * 1000))
            uci_dict['btime'] = str(int(self.clock_time[chess.BLACK] * 1000))

            if self.mode == ClockMode.FISCHER:
                uci_dict['winc'] = str(self.fischer_increment * 1000)
                uci_dict['binc'] = str(self.fischer_increment * 1000)
        elif self.mode == ClockMode.FIXED_TIME:
            uci_dict['movetime'] = str(self.seconds_per_move * 1000)

        return uci_dict
