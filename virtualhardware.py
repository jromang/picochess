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
    def __init__(self, enable_dgt_3000):
        super(VirtualHardware, self).__init__()
        self.rt = None
        self.time_left = None
        self.time_right = None
        self.time_side = None
        self.enable_dgt_3000 = enable_dgt_3000
        self.displayed_text = None # The current clock display or None if in ClockNRun mode or unknown text

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
        self.displayed_text = None # reset saved text to unknown
        Display.show(Dgt.DISPLAY_TEXT, text='{} : {}'.format(l_hms, r_hms), xl=None, beep=BeepLevel.NO)

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG):
        if self.enable_dgt_3000:
            bit_board = chess.Board(fen)
            move_string = bit_board.san(move)
        else:
            move_string = str(move)
        logging.debug(move_string)
        print('DGT clock mov:' + move_string)

    def display_text_on_clock(self, text, dgt_xl_text=None, beep=BeepLevel.CONFIG, force=True):
        if self.enable_dgt_3000:
            if force or self.displayed_text != text:
                logging.debug(text)
                print('DGT clock txt:' + text)
        else:
            if dgt_xl_text:
                text = dgt_xl_text
            if force or self.displayed_text != text:
                logging.debug(text)
                print('DGT clock txt:' + text)
        self.displayed_text = text

    def stop_clock(self):
        if self.rt:
            print('DGT clock time stopped at ', (self.time_left, self.time_right))
            self.rt.stop()
        else:
            print('clock not ready')

    def start_clock(self, time_left, time_right, side):
        self.time_left = time_left
        self.time_right = time_right
        self.time_side = side

        print('DGT clock time started at ', (self.time_left, self.time_right))
        if self.rt:
            self.rt.stop()
        self.rt = self.RepeatedTimer(1, self.runclock)

    def run(self):
        while True:
            # Check if we have something to display
            message = self.message_queue.get()
            for case in switch(message):
                if case(Dgt.DISPLAY_MOVE):
                    self.display_move_on_clock(message.move, message.fen, message.beep)
                    break
                if case(Dgt.DISPLAY_TEXT):
                    self.display_text_on_clock(message.text, message.xl, message.beep)
                    break
                if case(Dgt.CLOCK_START):
                    self.start_clock(message.time_left, message.time_right, message.side)
                    break
                if case(Dgt.CLOCK_STOP):
                    self.stop_clock()
                    break
                if case():  # Default
                    pass
