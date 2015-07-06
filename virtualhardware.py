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

import threading
from threading import Timer
import chess
from utilities import *

class VirtualHardware(Observable, Display, threading.Thread):
    def __init__(self, dgt_3000_clock):
        super(VirtualHardware, self).__init__()
        self.rt = None
        self.time_left = None
        self.time_right = None
        self.time_side = None
        self.dgt3000_clock = dgt_3000_clock

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
            self.time_left -= 1
        else:
            self.time_right -= 1
        if self.time_left <= 0:
            print('Time flag fallen on left side')
            self.time_left = 0
        if self.time_right <= 0:
            print('Time flag fallen on right side')
            self.time_right = 0
        l_hms = hours_minutes_seconds(self.time_left)
        r_hms = hours_minutes_seconds(self.time_right)
        Display.show(Dgt.DISPLAY_TEXT, text='{} : {}'.format(l_hms, r_hms))

    def run(self):
        while True:
            # Check if we have something to display
            message = self.message_queue.get()
            for case in switch(message):
                if case(Dgt.DISPLAY_MOVE):
                    move = message.move
                    if self.dgt3000_clock:
                        fen = message.fen
                        bit_board = chess.Board(fen)
                        move_string = bit_board.san(move)
                    else:
                        move_string = str(move)
                    print('DGT clock mov:' + move_string)
                    break
                if case(Dgt.DISPLAY_TEXT):
                    print('DGT clock txt:' + message.text)
                    break
                if case(Dgt.CLOCK_START):
                    self.time_left = message.time_left
                    self.time_right = message.time_right
                    self.time_side = message.side

                    print('DGT clock time started at ', (self.time_left, self.time_right))
                    if self.rt:
                        self.rt.stop()
                    self.rt = self.RepeatedTimer(1, self.runclock)
                    break
                if case(Dgt.CLOCK_STOP):
                    print('DGT clock time stopped at ', (self.time_left, self.time_right))
                    self.rt.stop()
                    break
                if case():  # Default
                    pass
