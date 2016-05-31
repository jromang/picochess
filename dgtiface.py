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

from utilities import *
import time
import chess
from threading import Timer, Thread


class DgtIface(DisplayDgt, Thread):
    def __init__(self, dgtserial, dgttranslate, enable_revelation_leds):
        super(DgtIface, self).__init__()

        self.dgtserial = dgtserial
        self.dgttranslate = dgttranslate

        self.enable_dgt_3000 = False
        self.enable_dgt_pi = False
        self.clock_found = False
        self.enable_revelation_leds = enable_revelation_leds
        self.time_left = None
        self.time_right = None

        self.timer = None
        self.timer_running = False
        self.clock_running = False
        self.duration_factor = 1  # This is for testing the duration - remove it lateron!

    def display_text_on_clock(self, text, beep=False):
        raise NotImplementedError()

    def display_move_on_clock(self, move, fen, side, beep=False):
        raise NotImplementedError()

    def display_time_on_clock(self, force=False):
        raise NotImplementedError()

    def light_squares_revelation_board(self, squares):
        raise NotImplementedError()

    def clear_light_revelation_board(self):
        raise NotImplementedError()

    def stop_clock(self):
        raise NotImplementedError()

    def resume_clock(self, side):
        raise NotImplementedError()

    def start_clock(self, time_left, time_right, side):
        raise NotImplementedError()

    def stopped_timer(self):
        self.timer_running = False
        if self.clock_running:
            logging.debug('showing the running clock again')
            self.display_time_on_clock(force=False)
        else:
            logging.debug('clock not running - ignored duration')

    def run(self):
        logging.info('dgt_queue ready')
        while True:
            # Check if we have something to display
            try:
                message = self.dgt_queue.get()
                logging.debug("received command from dgt_queue: %s", message)
                for case in switch(message):
                    if case(DgtApi.DISPLAY_MOVE):
                        message.wait = True  # TEST!
                        while self.timer_running and message.wait:
                            time.sleep(0.1)
                        if hasattr(message, 'duration') and message.duration > 0:
                            self.timer = Timer(message.duration * self.duration_factor, self.stopped_timer)
                            self.timer.start()
                            logging.debug('showing move for {} secs'.format(message.duration * self.duration_factor))
                            self.timer_running = True
                        self.display_move_on_clock(message.move, message.fen, message.side, message.beep)
                        break
                    if case(DgtApi.DISPLAY_TEXT):
                        message.wait = True  # TEST!
                        while self.timer_running and message.wait:
                            time.sleep(0.1)
                        if self.enable_dgt_pi:
                            text = message.l
                        else:
                            text = message.m if self.enable_dgt_3000 else message.s
                        if text is None:
                            text = message.m
                        if hasattr(message, 'duration') and message.duration > 0:
                            self.timer = Timer(message.duration * self.duration_factor, self.stopped_timer)
                            self.timer.start()
                            logging.debug('showing text for {} secs'.format(message.duration * self.duration_factor))
                            self.timer_running = True
                        self.display_text_on_clock(text, message.beep)
                        break
                    if case(DgtApi.DISPLAY_TIME):
                        while self.timer_running and message.wait:
                            time.sleep(0.1)
                        self.display_time_on_clock(message.force)
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
                        Observable.fire(Event.DGT_CLOCK_CALLBACK(callback=message.callback))
                        break
                    if case(DgtApi.CLOCK_START):
                        while self.timer_running and message.wait:
                            time.sleep(0.1)
                        self.clock_running = (message.side != 0x04)
                        # log times
                        l_hms = hours_minutes_seconds(message.time_left)
                        r_hms = hours_minutes_seconds(message.time_right)
                        logging.debug('last time received from clock l:{} r:{}'.format(self.time_left, self.time_right))
                        logging.debug('sending time to clock l:{} r:{}'.format(l_hms, r_hms))

                        self.start_clock(message.time_left, message.time_right, message.side)
                        Observable.fire(Event.DGT_CLOCK_CALLBACK(callback=message.callback))
                        break
                    if case(DgtApi.CLOCK_VERSION):
                        self.clock_found = True
                        if message.main_version == 2:
                            self.enable_dgt_3000 = True
                        if message.attached == 'i2c':
                            self.enable_dgt_pi = True
                        self.show(Dgt.DISPLAY_TEXT(l='picoChs ' + version, m='pico ' + version, s='pic' + version, beep=True, duration=2))
                        break
                    if case(DgtApi.CLOCK_TIME):
                        self.time_left = message.time_left
                        self.time_right = message.time_right
                        break
                    if case():  # Default
                        pass
            except queue.Empty:
                pass
