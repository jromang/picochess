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
from chess import Board
from ctypes import *
from dgtinterface import *
from dgti2c import *
from utilities import *
from threading import Lock, Timer


class DGTPi(DGTInterface):
    def __init__(self, device, enable_board_leds, beep_level):
        super(DGTPi, self).__init__(enable_board_leds, beep_level)
        self.dgti2c = DGTi2c(device)
        self.dgti2c.run()

        self.lock = Lock()
        # load the dgt3000 SO-file
        self.lib = cdll.LoadLibrary("/home/pi/20151229/dgt3000.so")

        self.startup_clock()
        incoming_clock_thread = Timer(0, self.process_incoming_clock_forever)
        incoming_clock_thread.start()

    def startup_clock(self):
        while self.lib.dgt3000Init() < 0:
            logging.warning('Init failed')
            time.sleep(0.5)  # dont flood the log
        if self.lib.dgt3000Configure() < 0:
            logging.warning('Configure failed')
        Display.show(Message.DGT_CLOCK_VERSION, main_version=2, sub_version=2)

    def process_incoming_clock_forever(self):
        but = c_byte(0)
        buttime = c_byte(0)
        clktime = create_string_buffer(6)
        counter = 0
        while True:
            with self.lock:
                # get button events
                if self.lib.dgt3000GetButton(pointer(but), pointer(buttime)) == 1:
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
                    if ack3 == 0x40:
                        logging.info("Lever pressed > right side down")
                    if ack3 == -0x40:
                        logging.info("Lever pressed > left side down")

                # get time events
                self.lib.dgt3000GetTime(clktime)

            times = list(clktime.raw)
            counter = (counter + 1) % 4
            if counter == 1:
                Display.show(Message.DGT_CLOCK_TIME, time_left=times[:3], time_right=times[3:])
            if counter == 3:  # issue 150 - force to write something to the board => check for alive connection!
                self.dgti2c.write_to_board([DgtCmd.DGT_RETURN_SERIALNR])  # the code doesnt really matter ;-)
            time.sleep(0.25)

    def _display_on_dgt_3000(self, text, beep=False):
        if len(text) > 11:
            logging.warning('DGT 3000 clock message too long [%s]', text)
        logging.debug(text)
        text = bytes(text, 'utf-8')
        with self.lock:
            res = self.lib.dgt3000Display(text, 0x03 if beep else 0x01, 0, 0)
            if res < 0:
                logging.warning('Display returned error %i', res)
                res = self.lib.dgt3000Configure()
                if res < 0:
                    logging.warning('Configure also failed %i', res)
                else:
                    res = self.lib.dgt3000Display(text, 0x03 if beep else 0x00, 0, 0)
            if res < 0:
                logging.warning('Finally failed %i', res)

    def display_text_on_clock(self, text, dgt_xl_text=None, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        self._display_on_dgt_3000(text, beep)

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG):
        beep = self.get_beep_level(beep)
        bit_board = Board(fen)
        text = bit_board.san(move)
        self._display_on_dgt_3000(text, beep)

    def light_squares_revelation_board(self, squares):
        pass

    def clear_light_revelation_board(self):
        pass

    def stop_clock(self):
        l_hms = hours_minutes_seconds(self.time_left)
        r_hms = hours_minutes_seconds(self.time_right)
        with self.lock:
            res = self.lib.dgt3000SetNRun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('SetNRun returned error %i', res)
                res = self.lib.dgt3000Configure()
                if res < 0:
                    logging.warning('Configure also failed %i', res)
                else:
                    res = self.lib.dgt3000SetNRun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = False

    def start_clock(self, time_left, time_right, side):
        l_hms = hours_minutes_seconds(time_left)
        r_hms = hours_minutes_seconds(time_right)
        self.time_left = l_hms
        self.time_right = r_hms
        with self.lock:
            res = self.lib.dgt3000SetNRun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('SetNRun returned error %i', res)
                res = self.lib.dgt3000Configure()
                if res < 0:
                    logging.warning('Configure also failed %i', res)
                else:
                    res = self.lib.dgt3000SetNRun(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = False

    def serialnr_board(self):
        self.dgti2c.write_to_board([DgtCmd.DGT_RETURN_SERIALNR])
