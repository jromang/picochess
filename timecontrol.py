# Copyright (C) 2013-2018 Jean-Francois Romang (jromang@posteo.de)
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

import time
import threading
import logging
import copy
from math import floor

from utilities import Observable, hms_time
import chess
from dgt.api import Event
from dgt.util import TimeMode


class TimeControl(object):

    """Control the picochess internal clock."""

    def __init__(self, mode=TimeMode.FIXED, fixed=0, blitz=0, fischer=0, internal_time=None):
        super(TimeControl, self).__init__()
        self.mode = mode
        self.move_time = fixed
        self.game_time = blitz
        self.fisch_inc = fischer
        self.internal_time = internal_time

        self.clock_time = {chess.WHITE: 0, chess.BLACK: 0}  # saves the sended clock time for white/black
        self.timer = None
        self.run_color = None
        self.active_color = None
        self.start_time = None

        if internal_time:  # preset the clock (received) time already
            self.clock_time[chess.WHITE] = int(internal_time[chess.WHITE])
            self.clock_time[chess.BLACK] = int(internal_time[chess.BLACK])
        else:
            self.reset()

    def __eq__(self, other):
        chk_mode = self.mode == other.mode
        chk_secs = self.move_time == other.move_time
        chk_mins = self.game_time == other.game_time
        chk_finc = self.fisch_inc == other.fisch_inc
        return chk_mode and chk_secs and chk_mins and chk_finc

    def __hash__(self):
        value = str(self.mode) + str(self.move_time) + str(self.game_time) + str(self.fisch_inc)
        return hash(value)

    def get_parameters(self):
        """Return the state of this class for generating a new instance."""
        return {'mode': self.mode, 'fixed': self.move_time, 'blitz': self.game_time,
                'fischer': self.fisch_inc, 'internal_time': self.internal_time}

    def get_list_text(self):
        """Get the clock list text for the current time setting."""
        if self.mode == TimeMode.FIXED:
            return '{:2d}'.format(self.move_time)
        if self.mode == TimeMode.BLITZ:
            return '{:2d}'.format(self.game_time)
        if self.mode == TimeMode.FISCHER:
            return '{:2d} {:2d}'.format(self.game_time, self.fisch_inc)
        return 'errtm'

    def reset(self):
        """Reset the clock's times for both players."""
        if self.mode == TimeMode.BLITZ:
            self.clock_time[chess.WHITE] = self.clock_time[chess.BLACK] = self.game_time * 60

        elif self.mode == TimeMode.FISCHER:
            self.clock_time[chess.WHITE] = self.clock_time[chess.BLACK] = self.game_time * 60 + self.fisch_inc

        elif self.mode == TimeMode.FIXED:
            self.clock_time[chess.WHITE] = self.clock_time[chess.BLACK] = self.move_time

        self.internal_time = {chess.WHITE: float(self.clock_time[chess.WHITE]),
                              chess.BLACK: float(self.clock_time[chess.BLACK])}
        self.active_color = None

    def _log_time(self):
        time_w, time_b = self.get_internal_time(flip_board=False)
        return hms_time(time_w), hms_time(time_b)

    def get_internal_time(self, flip_board=False):
        """Return the startup time for setting the clock at beginning."""
        i_time = copy.copy(self.internal_time)
        if flip_board:
            i_time[chess.WHITE], i_time[chess.BLACK] = i_time[chess.BLACK], i_time[chess.WHITE]
        return int(i_time[chess.WHITE]), int(i_time[chess.BLACK])

    def set_clock_times(self, white_time: int, black_time: int):
        """Set the times send from the clock."""
        logging.info('set clock times w:%s b:%s', hms_time(white_time), hms_time(black_time))
        self.clock_time[chess.WHITE] = white_time
        self.clock_time[chess.BLACK] = black_time

    def reset_start_time(self):
        """Set the start time to the current time."""
        self.start_time = time.time()

    def _out_of_time(self, time_start):
        """Fire an OUT_OF_TIME event."""
        self.run_color = None
        if self.mode == TimeMode.FIXED:
            logging.debug('timeout - but in "MoveTime" mode, dont fire event')
        elif self.active_color is not None:
            display_color = 'WHITE' if self.active_color == chess.WHITE else 'BLACK'
            txt = 'current clock time (before subtracting) is %f and color is %s, out of time event started from %f'
            logging.debug(txt, self.internal_time[self.active_color], display_color, time_start)
            Observable.fire(Event.OUT_OF_TIME(color=self.active_color))

    def add_time(self, color):
        """Add the increment value to the color given."""
        assert self.internal_running() is False, 'internal clock still running for: %s' % self.run_color
        if self.mode == TimeMode.FISCHER:
            # log times - issue #184
            w_hms, b_hms = self._log_time()
            logging.info('before internal time w:%s - b:%s', w_hms, b_hms)

            self.internal_time[color] += self.fisch_inc
            self.clock_time[color] += self.fisch_inc

            # log times - issue #184
            w_hms, b_hms = self._log_time()
            logging.info('after internal time w:%s - b:%s', w_hms, b_hms)

        if self.mode == TimeMode.FIXED:
            self.reset()

    def start_internal(self, color, log=True):
        """Start the internal clock."""
        if not self.internal_running():
            if self.mode in (TimeMode.BLITZ, TimeMode.FISCHER):
                self.active_color = color
                self.reset_start_time()

            if log:
                w_hms, b_hms = self._log_time()
                logging.info('start internal time w:%s - b:%s [ign]', w_hms, b_hms)
                logging.info('received clock time w:%s - b:%s [use]',
                             hms_time(self.clock_time[chess.WHITE]), hms_time(self.clock_time[chess.BLACK]))

            self.internal_time[chess.WHITE] = self.clock_time[chess.WHITE]
            self.internal_time[chess.BLACK] = self.clock_time[chess.BLACK]

            # Only start thread if not already started for same color, and the player has not already lost on time
            if self.internal_time[color] > 0 and self.active_color is not None and self.run_color != self.active_color:
                self.timer = threading.Timer(copy.copy(self.internal_time[color]), self._out_of_time,
                                             [copy.copy(self.internal_time[color])])
                self.timer.start()
                logging.debug('internal timer started - color: %s run: %s active: %s',
                              color, self.run_color, self.active_color)
                self.run_color = self.active_color

    def stop_internal(self, log=True):
        """Stop the internal clock."""
        if self.internal_running() and self.mode in (TimeMode.BLITZ, TimeMode.FISCHER):
            if log:
                w_hms, b_hms = self._log_time()
                logging.info('old internal time w:%s b:%s', w_hms, b_hms)

            if self.timer:
                self.timer.cancel()
                self.timer.join()
            else:
                logging.warning('time=%s', self.internal_time)
            used_time = floor((time.time() - self.start_time) * 10) / 10
            if log:
                logging.info('used time: %s secs', used_time)
            self.internal_time[self.active_color] -= used_time
            if self.internal_time[self.active_color] < 0:
                self.internal_time[self.active_color] = 0

            if log:
                w_hms, b_hms = self._log_time()
                logging.info('new internal time w:%s b:%s', w_hms, b_hms)
            self.run_color = self.active_color = None

    def internal_running(self):
        """Return if the internal clock is running."""
        return self.active_color is not None

    def uci(self):
        """Return remaining time for both players in an UCI dict."""
        uci_dict = {}
        if self.mode in (TimeMode.BLITZ, TimeMode.FISCHER):
            uci_dict['wtime'] = str(int(self.internal_time[chess.WHITE] * 1000))
            uci_dict['btime'] = str(int(self.internal_time[chess.BLACK] * 1000))

            if self.mode == TimeMode.FISCHER:
                uci_dict['winc'] = str(self.fisch_inc * 1000)
                uci_dict['binc'] = str(self.fisch_inc * 1000)
        elif self.mode == TimeMode.FIXED:
            uci_dict['movetime'] = str(self.move_time * 1000)

        return uci_dict
