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

from threading import Timer
import chess
from dgtinterface import *


class DGTVr(DGTInterface):
    def __init__(self, enable_board_leds, beep_level):
        super(DGTVr, self).__init__(enable_board_leds, beep_level)
        # virtual lib
        self.rt = None
        self.time_side = None
        # setup virtual clock
        Display.show(Message.DGT_CLOCK_VERSION(main_version=0, sub_version=0, attached="virtual"))

    # (START) dgtserial class simulation
    class RepeatedTimer(object):
        def __init__(self, interval, function, *args, **kwargs):
            self._timer = None
            self.interval = interval
            self.function = function
            self.args = args
            self.kwargs = kwargs
            self.is_running = False
            self.start()

        def _run(self):
            self.is_running = False
            self.start()
            self.function(*self.args, **self.kwargs)

        def start(self):
            if not self.is_running:
                self._timer = Timer(self.interval, self._run)
                self._timer.start()
                self.is_running = True

        def stop(self):
            self._timer.cancel()
            self.is_running = False

    def runclock(self):
        if self.time_side == 1:
            h, m, s = self.time_left
            time_left = 3600*h + 60*m + s -1
            if time_left <= 0:
                print('Clock flag: left')
                self.rt.stop()
            self.time_left = hours_minutes_seconds(time_left)
        else:
            h, m, s = self.time_right
            time_right = 3600*h + 60*m + s -1
            if time_right <= 0:
                print('Clock flag: right')
                self.rt.stop()
            self.time_right = hours_minutes_seconds(time_right)
        if self.timer_running:
            print('Clock duration not run out')
        else:
            print('Clock time: {} - {}'.format(self.time_left, self.time_right))
        Display.show(Message.DGT_CLOCK_TIME(time_left=self.time_left, time_right=self.time_right))
    # (END) dgtserial simulation class

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        if self.enable_dgt_3000:
            bit_board = chess.Board(fen)
            text = bit_board.san(move)
        else:
            text = str(move)
        logging.debug(text)
        print('Clock move: {} Beep: {}'. format(text, beep))

    def display_text_on_clock(self, text, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        logging.debug(text)
        print('Clock text: {} Beep: {}'. format(text, beep))

    def stop_clock(self):
        if self.rt:
            print('Clock time stopped at {} - {}'. format(self.time_left, self.time_right))
            self.rt.stop()
        else:
            print('Clock not ready')
        self.clock_running = False

    def start_clock(self, time_left, time_right, side):
        self.time_left = hours_minutes_seconds(time_left)
        self.time_right = hours_minutes_seconds(time_right)
        self.time_side = side

        print('Clock time started at {} - {}'. format(self.time_left, self.time_right))
        if self.rt:
            self.rt.stop()
        self.rt = self.RepeatedTimer(1, self.runclock)
        self.clock_running = True

    def light_squares_revelation_board(self, squares):
        pass

    def clear_light_revelation_board(self):
        pass

    def end_clock(self):
        if self.clock_running:
            pass
        else:
            logging.debug('Clock isnt running - no need for endClock')
