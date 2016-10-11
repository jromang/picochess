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
import time
import threading
from utilities import *
import copy
from math import floor


class TimeControl(object):
    def __init__(self, mode=TimeMode.FIXED, seconds_per_move=0, minutes_per_game=0, fischer_increment=0):
        super(TimeControl, self).__init__()
        self.mode = mode
        self.seconds_per_move = seconds_per_move
        self.minutes_per_game = minutes_per_game
        self.fischer_increment = fischer_increment
        self.timer = None
        self.run_color = None
        self.clock_time = None
        self.active_color = None
        self.start_time = None
        self.reset()

    def __eq__(self, other):
        return self.mode == other.mode and self.seconds_per_move == other.seconds_per_move and \
               self.minutes_per_game == other.minutes_per_game and self.fischer_increment == other.fischer_increment

    def reset(self):
        """Resets the clock's times for both players"""
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

    def current_clock_time(self, flip_board=False):
        """Returns the startup time for setting the clock at beginning."""
        ct = copy.copy(self.clock_time)
        if flip_board:
            ct[chess.WHITE], ct[chess.BLACK] = ct[chess.BLACK], ct[chess.WHITE]
        return int(ct[chess.WHITE]), int(ct[chess.BLACK])

    def reset_start_time(self):
        self.start_time = time.time()

    def _out_of_time(self, time_start):
        """Fires an OUT_OF_TIME event."""
        if self.mode == TimeMode.FIXED:
            logging.debug('timeout - but in "MoveTime" mode, dont fire event')
        elif self.active_color is not None:
            txt = 'current clock time (before subtracting) is {} and color is {}, out of time event started from {}'
            logging.debug(txt.format(self.clock_time[self.active_color], self.active_color, time_start))
            Observable.fire(Event.OUT_OF_TIME(color=self.active_color))

    def add_inc(self, color):
        if self.mode == TimeMode.FISCHER:
            # log times - issue #184
            time_w, time_b = self.current_clock_time(flip_board=False)
            w_hms = hours_minutes_seconds(time_w)
            b_hms = hours_minutes_seconds(time_b)
            logging.info('before internal time w:{} - b:{}'.format(w_hms, b_hms))

            self.clock_time[color] += self.fischer_increment

            # log times - issue #184
            time_w, time_b = self.current_clock_time(flip_board=False)
            w_hms = hours_minutes_seconds(time_w)
            b_hms = hours_minutes_seconds(time_b)
            logging.info('after internal time w:{} - b:{}'.format(w_hms, b_hms))

    def start(self, color):
        """Starts the internal clock."""
        if self.active_color is None:
            if self.mode in (TimeMode.BLITZ, TimeMode.FISCHER):
                self.active_color = color
                self.start_time = time.time()

            # log times
            time_w, time_b = self.current_clock_time(flip_board=False)
            w_hms = hours_minutes_seconds(time_w)
            b_hms = hours_minutes_seconds(time_b)
            logging.info('start internal time w:{} - b:{}'.format(w_hms, b_hms))

            # Only start thread if not already started for same color, and the player has not already lost on time
            if self.clock_time[color] > 0 and self.active_color is not None and self.run_color != self.active_color:
                self.timer = threading.Timer(copy.copy(self.clock_time[color]), self._out_of_time,
                                             [copy.copy(self.clock_time[color])])
                self.timer.start()
                self.run_color = self.active_color

    def stop(self):
        """Stop the internal clock."""
        if self.active_color is not None:
            if self.mode in (TimeMode.BLITZ, TimeMode.FISCHER):
                # log times
                time_w, time_b = self.current_clock_time(flip_board=False)
                w_hms = hours_minutes_seconds(time_w)
                b_hms = hours_minutes_seconds(time_b)
                logging.info('old internal time w:{} b:{}'.format(w_hms, b_hms))

                self.timer.cancel()
                self.timer.join()
                used_time = floor((time.time() - self.start_time)*10)/10
                logging.info('used time: {} secs'.format(used_time))
                self.clock_time[self.active_color] -= used_time

                # log times
                time_w, time_b = self.current_clock_time(flip_board=False)
                w_hms = hours_minutes_seconds(time_w)
                b_hms = hours_minutes_seconds(time_b)
                logging.info('new internal time w:{} b:{}'.format(w_hms, b_hms))
                self.active_color = None

    def is_ticking(self):
        """Is the internal clock running?"""
        return self.active_color is not None

    def uci(self):
        """Returns remaining time for both players in an UCI dict."""
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
