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

import threading, functools
from threading import Timer
import chess
from utilities import *

class VirtualHardware(Observable, Display, threading.Thread):
    def __init__(self):
        super(VirtualHardware, self).__init__()
        self.rt = None

    class PeriodicTimer(object):
        def __init__(self, interval, callback):
            self.interval = interval
            self.thread = None

            @functools.wraps(callback)
            def wrapper(*args, **kwargs):
                result = callback(*args, **kwargs)
                if result:
                    self.thread = threading.Timer(self.interval, self.callback)
                    self.thread.start()
            self.callback = wrapper

        def start(self):
            self.thread = threading.Timer(self.interval, self.callback)
            self.thread.start()

        def stop(self):
            self.thread.cancel()

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

    def runclock(self,w_hms, b_hms, side):
        print(w_hms, b_hms, side)

    def run(self):
        while True:
            # Check if we have something to display
            message = self.message_queue.get()
            for case in switch(message):
                if case(Dgt.DISPLAY_MOVE):
                    fen = message.fen
                    move = message.move
                    bit_board = chess.Board(fen)
                    print('DGT clock mov:' + str(message.move) + "/" + bit_board.san(move))
                    break
                if case(Dgt.DISPLAY_TEXT):
                    print('DGT clock txt:' + message.text)
                    break
                if case(Dgt.CLOCK_START):
                    print('DGT clock time started ', (message.w_hms, message.b_hms, message.side))
                    self.rt = self.RepeatedTimer(1, self.runclock, message.w_hms, message.b_hms, message.side)
                    break
                if case(Dgt.CLOCK_STOP):
                    print('DGT clock time stopped')
                    self.rt.stop()
                    break
                if case(Dgt.LIGHT_CLEAR):
                    pass
                    break
                if case(Dgt.LIGHT_SQUARES):
                    pass
                    break
                if case():  # Default
                    pass
