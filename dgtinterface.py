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

from utilities import *
import time
from threading import Timer, Thread


class DGTInterface(DgtDisplay, Thread):
    def __init__(self, enable_board_leds, beep_level):
        super(DGTInterface, self).__init__()

        self.enable_dgt_3000 = False
        self.enable_dgt_pi = True
        self.clock_found = False
        self.enable_board_leds = enable_board_leds
        self.beep_level = int(beep_level) & 0x0f
        self.time_left = [0, 0, 0]
        self.time_right = [0, 0, 0]

        self.timer = None
        self.timer_running = False
        self.clock_running = False

    def display_text_on_clock(self, text, text_xl=None, beep=BeepLevel.CONFIG):
        raise NotImplementedError()

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG):
        raise NotImplementedError()

    def light_squares_revelation_board(self, squares):
        raise NotImplementedError()

    def clear_light_revelation_board(self):
        raise NotImplementedError()

    def stop_clock(self):
        raise NotImplementedError()

    def start_clock(self, time_left, time_right, side):
        raise NotImplementedError()

    def end_clock(self):
        raise NotImplementedError()

    def get_beep_level(self, beeplevel):
        if beeplevel == BeepLevel.YES:
            return True
        if beeplevel == BeepLevel.NO:
            return False
        return bool(self.beep_level & beeplevel.value)

    def stopped_timer(self):
        self.timer_running = False
        if self.clock_running:
            logging.debug('Showing the running clock again')
            self.end_clock()
        else:
            logging.debug('Clock not running - ignored duration')

    def run(self):
        while True:
            # Check if we have something to display
            try:
                message = self.dgt_queue.get()
                logging.debug("Read dgt from queue: %s", message)
                for case in switch(message):
                    if case(DgtApi.DISPLAY_MOVE):
                        message.force = False  # TEST!
                        while self.timer_running and not message.force:
                            time.sleep(0.1)
                        if hasattr(message, 'duration') and message.duration > 0:
                            self.timer = Timer(message.duration, self.stopped_timer)
                            self.timer.start()
                            logging.debug('Showing move for {} secs'.format(message.duration))
                            self.timer_running = True
                        self.display_move_on_clock(message.move, message.fen, message.beep)
                        break
                    if case(DgtApi.DISPLAY_TEXT):
                        message.force = False  # TEST!
                        while self.timer_running and not message.force:
                            time.sleep(0.1)
                        if hasattr(message, 'duration') and message.duration > 0:
                            self.timer = Timer(message.duration, self.stopped_timer)
                            self.timer.start()
                            logging.debug('Showing text for {} secs'.format(message.duration))
                            self.timer_running = True
                        self.display_text_on_clock(message.text, message.xl, message.beep)
                        break
                    if case(DgtApi.LIGHT_CLEAR):
                        self.clear_light_revelation_board()
                        break
                    if case(DgtApi.LIGHT_SQUARES):
                        self.light_squares_revelation_board(message.squares)
                        break
                    if case(DgtApi.CLOCK_STOP):
                        self.clock_running = False
                        self.stop_clock()
                        break
                    if case(DgtApi.CLOCK_START):
                        self.clock_running = True
                        self.start_clock(message.time_left, message.time_right, message.side)
                        break
                    if case(DgtApi.CLOCK_VERSION):
                        self.clock_found = True
                        if message.main_version == 2:
                            self.enable_dgt_3000 = True
                        if message.attached == 'i2c':
                            self.enable_dgt_pi = True
                        self.show(Dgt.DISPLAY_TEXT(text='pico ' + version, xl='pic' + version, beep=BeepLevel.YES, duration=2))
                        break
                    if case(DgtApi.CLOCK_TIME):
                        self.time_left = message.time_left
                        self.time_right = message.time_right
                        break
                    if case():  # Default
                        pass
            except queue.Empty:
                pass
