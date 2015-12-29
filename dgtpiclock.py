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

import logging
import ctypes
import sys
import os
import time
from threading import Timer, Lock
from utilities import *


class DGTpiclock(Display):
    def __init__(self):
        super(DGTpiclock, self).__init__()
        self.i2c_queue = queue.Queue()
        self.timer = None
        self.timer_running = False
        self.clock_running = False
        self.lock = Lock()

        # load the dgt3000 SO-file
        self.lib = ctypes.cdll.LoadLibrary("/home/pi/20151223/dgt3000.so")

    def write(self, message, beep, duration, force):
        if force:
            logging.debug('force given')
            self.i2c_queue = queue.Queue()
            if self.timer:
                self.timer.stop()
                self.timer_running = False
        self.i2c_queue.put((message, beep, duration))

    def send_command(self, command):
        self.lock.acquire()
        message, beep, duration = command
        if duration > 0:
            self.timer = Timer(duration, self.stopped_timer)
            self.timer.start()
            self.timer_running = True
        res = self.lib.dgt3000Display(message, 0x03 if beep else 0x01, 0, 0)
        if res < 0:
            logging.warning('dgt lib returned error: %i', res)
            self.lib.dgt3000Configure()
        self.lock.release()

    def write_stop_to_clock(self, l_hms, r_hms):
        self.lock.acquire()
        res = self.lib.dgt3000SetNRun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
        if res < 0:
            logging.warning('dgt lib returned error: %i', res)
            self.lib.dgt3000Configure()
        self.lock.release()

    def stopped_timer(self):
        self.timer_running = False
        if self.clock_running:
            self.lock.acquire()
            res = self.lib.dgt3000EndDisplay()
            if res < 0:
                logging.warning('dgt lib returned error: %i', res)
                self.lib.dgt3000Configure()
            self.lock.release()

    def write_start_to_clock(self, l_hms, r_hms, side):
        self.lock.acquire()
        if side == 0x01:
            lr = 1
            rr = 0
        else:
            lr = 0
            rr = 1
        self.clock_running = True
        res = self.lib.dgt3000SetNRun(lr, l_hms[0], l_hms[1], l_hms[2], rr, r_hms[0], r_hms[1], r_hms[2])
        if res < 0:
            logging.warning('dgt lib returned error: %i', res)
            self.lib.dgt3000Configure()
        self.lock.release()

    def startup_clock(self):
        if self.lib.dgt3000Init() < 0:
            sys.exit(-1)
        if self.lib.dgt3000Configure() < 0:
            sys.exit(-1)
        Display.show(Message.DGT_CLOCK_VERSION, main_version=2, sub_version=2)

    def process_incoming_clock_forever(self):
        but = ctypes.c_byte(0)
        buttime = ctypes.c_byte(0)
        clktime = ctypes.create_string_buffer(6)
        counter = 0
        while True:
            self.lock.acquire()
            # get button events
            if self.lib.dgt3000GetButton(ctypes.pointer(but), ctypes.pointer(buttime)) == 1:
                ack3 = but.value
                if ack3 == 0x01:
                    logging.info("Button 0 pressed")
                    Display.show(Message.DGT_BUTTON, button=0)
                if ack3 == 0x02:
                    logging.info("Button 1 pressed")
                    Display.show(Message.DGT_BUTTON, button=1)
                if ack3 == 0x04:
                    logging.info("Button 2 pressed")
                    Display.show(Message.DGT_BUTTON, button=2)
                if ack3 == 0x08:
                    logging.info("Button 3 pressed")
                    Display.show(Message.DGT_BUTTON, button=3)
                if ack3 == 0x10:
                    logging.info("Button 4 pressed")
                    Display.show(Message.DGT_BUTTON, button=4)
                if ack3 == 0x20:
                    logging.info("Button on/off pressed")
                    # do more fancy tasks - like save pgn...
                    os.system('shutdown')
                if ack3 == 0x40:
                    logging.info("Lever pressed > right side down")
                if ack3 == -0x40:
                    logging.info("Lever pressed > left side down")

            # get time events
            self.lib.dgt3000GetTime(clktime)
            self.lock.release()
            times = list(clktime.raw)
            counter = (counter + 1) % 5
            if counter == 1:
                Display.show(Message.DGT_CLOCK_TIME, time_left=times[:3], time_right=times[3:])
            if counter == 3:  # issue 150 - force to write something to the board => check for alive connection!
                # self.write_to_board([DgtCmd.DGT_RETURN_SERIALNR])  # the code doesnt really matter ;-)
                Display.show(Message.DGT_SERIALNR)
            time.sleep(0.2)

    def process_outgoing_clock_forever(self):
        while True:
            if not self.timer_running:
                # Check if we have something to send
                try:
                    command = self.i2c_queue.get()
                    self.send_command(command)
                except queue.Empty:
                    pass

    def run(self):
        self.startup_clock()
        incoming_clock_thread = Timer(0, self.process_incoming_clock_forever)
        incoming_clock_thread.start()
        outgoing_clock_thread = Timer(0, self.process_outgoing_clock_forever)
        outgoing_clock_thread.start()