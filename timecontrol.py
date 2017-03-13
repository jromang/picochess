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
import time
import threading
from utilities import Observable, hours_minutes_seconds
import logging
from dgtapi import Event
from dgtutil import TimeMode
import copy
from math import floor


class TimeControl(object):
    """control the picochess internal clock."""
    def __init__(self, mode=TimeMode.FIXED, fixed=0, blitz=0, fischer=0, clock_time=None):
        super(TimeControl, self).__init__()
        self.mode = mode
        self.seconds_per_move = fixed
        self.minutes_per_game = blitz
        self.fischer_increment = fischer
        self.clock_time = clock_time

        self.timer = None
        self.run_color = None
        self.active_color = None
        self.start_time = None

        if not clock_time:
            self.reset()

    def __eq__(self, other):
        return self.mode == other.mode and self.seconds_per_move == other.seconds_per_move and \
               self.minutes_per_game == other.minutes_per_game and self.fischer_increment == other.fischer_increment

    def get_init_parameters(self):
        """Return the state of this class for generating a new instance."""
        return {'mode': self.mode, 'fixed': self.seconds_per_move, 'blitz': self.minutes_per_game,
                'fischer': self.fischer_increment, 'clock_time': self.clock_time}

    def reset(self):
        """Reset the clock's times for both players."""
        if self.mode == TimeMode.BLITZ:
            self.clock_time = {chess.WHITE: float(self.minutes_per_game * 60),
                               chess.BLACK: float(self.minutes_per_game * 60)}
        elif self.mode == TimeMode.FISCHER:
            self.clock_time = {chess.WHITE: float(self.minutes_per_game * 60 + self.fischer_increment),
                               chess.BLACK: float(self.minutes_per_game * 60 + self.fischer_increment)}
        elif self.mode == TimeMode.FIXED:
            self.clock_time = {chess.WHITE: float(self.seconds_per_move),
                               chess.BLACK: float(self.seconds_per_move)}
        self.active_color = None

    def _log_time(self):
        time_w, time_b = self.current_clock_time(flip_board=False)
        return hours_minutes_seconds(time_w), hours_minutes_seconds(time_b)

    def current_clock_time(self, flip_board=False):
        """Return the startup time for setting the clock at beginning."""
        c_time = copy.copy(self.clock_time)
        if flip_board:
            c_time[chess.WHITE], c_time[chess.BLACK] = c_time[chess.BLACK], c_time[chess.WHITE]
        return int(c_time[chess.WHITE]), int(c_time[chess.BLACK])

    def reset_start_time(self):
        """Set the start time to the current time."""
        self.start_time = time.time()

    def _out_of_time(self, time_start):
        """Fire an OUT_OF_TIME event."""
        self.run_color = None
        if self.mode == TimeMode.FIXED:
            logging.debug('timeout - but in "MoveTime" mode, dont fire event')
        elif self.active_color is not None:
            txt = 'current clock time (before subtracting) is {} and color is {}, out of time event started from {}'
            logging.debug(txt.format(self.clock_time[self.active_color], self.active_color, time_start))
            Observable.fire(Event.OUT_OF_TIME(color=self.active_color))

    def add_inc(self, color):
        """Add the increment value to the color given."""
        if self.mode == TimeMode.FISCHER:
            # log times - issue #184
            w_hms, b_hms = self._log_time()
            logging.info('before internal time w:{} - b:{}'.format(w_hms, b_hms))

            self.clock_time[color] += self.fischer_increment

            # log times - issue #184
            w_hms, b_hms = self._log_time()
            logging.info('after internal time w:{} - b:{}'.format(w_hms, b_hms))

    def start(self, color, log=True):
        """Start the internal clock."""
        if not self.is_ticking():
            if self.mode in (TimeMode.BLITZ, TimeMode.FISCHER):
                self.active_color = color
                self.start_time = time.time()

            if log:
                w_hms, b_hms = self._log_time()
                logging.info('start internal time w:{} - b:{}'.format(w_hms, b_hms))

            # Only start thread if not already started for same color, and the player has not already lost on time
            if self.clock_time[color] > 0 and self.active_color is not None and self.run_color != self.active_color:
                self.timer = threading.Timer(copy.copy(self.clock_time[color]), self._out_of_time,
                                             [copy.copy(self.clock_time[color])])
                self.timer.start()
                self.run_color = self.active_color

    def stop(self, log=True):
        """Stop the internal clock."""
        if self.is_ticking() and self.mode in (TimeMode.BLITZ, TimeMode.FISCHER):
            if log:
                w_hms, b_hms = self._log_time()
                logging.info('old internal time w:{} b:{}'.format(w_hms, b_hms))

            self.timer.cancel()
            self.timer.join()
            used_time = floor((time.time() - self.start_time)*10)/10
            if log:
                logging.info('used time: {} secs'.format(used_time))
            self.clock_time[self.active_color] -= used_time

            if log:
                w_hms, b_hms = self._log_time()
                logging.info('new internal time w:{} b:{}'.format(w_hms, b_hms))
            self.run_color = self.active_color = None

    def is_ticking(self):
        """Return if the internal clock is running."""
        return self.active_color is not None

    def uci(self):
        """Return remaining time for both players in an UCI dict."""
        uci_dict = {}
        if self.mode in (TimeMode.BLITZ, TimeMode.FISCHER):
            uci_dict['wtime'] = str(int(self.clock_time[chess.WHITE] * 1000))
            uci_dict['btime'] = str(int(self.clock_time[chess.BLACK] * 1000))

            if self.mode == TimeMode.FISCHER:
                uci_dict['winc'] = str(self.fischer_increment * 1000)
                uci_dict['binc'] = str(self.fischer_increment * 1000)
        elif self.mode == TimeMode.FIXED:
            uci_dict['movetime'] = str(self.seconds_per_move * 1000)

        return uci_dict
