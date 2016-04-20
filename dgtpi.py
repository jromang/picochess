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

from chess import Board
from dgtiface import *
from dgtserial import *
from ctypes import *
from utilities import *
from threading import Lock, Timer


class DgtPi(DgtIface):
    def __init__(self, dgtserial, dgtttranslate, enable_revelation_leds):
        super(DgtPi, self).__init__(enable_revelation_leds)
        self.dgtserial = dgtserial
        self.dgtserial.enable_pi()
        self.dgttranslate = dgtttranslate

        self.lock = Lock()
        self.lib = cdll.LoadLibrary("dgt/dgtpicom.so")

        self.startup_pi_clock()
        incoming_clock_thread = Timer(0, self.process_incoming_clock_forever)
        incoming_clock_thread.start()
        self.dgtserial.run()

    def startup(self):
        self.dgtserial.setup_serial()
        self.dgtserial.startup_board()

    def startup_pi_clock(self):
        while self.lib.dgtpicom_init() < 0:
            logging.warning('Init failed - Jack half connected?')
            DisplayMsg.show(Message.JACK_CONNECTED_ERROR())
            time.sleep(0.5)  # dont flood the log
        if self.lib.dgtpicom_configure() < 0:
            logging.warning('Configure failed - Jack connected back?')
            DisplayMsg.show(Message.JACK_CONNECTED_ERROR())
        DisplayMsg.show(Message.DGT_CLOCK_VERSION(main_version=2, sub_version=2, attached="i2c"))

    def process_incoming_clock_forever(self):
        but = c_byte(0)
        buttime = c_byte(0)
        clktime = create_string_buffer(6)
        counter = 0
        while True:
            with self.lock:
                # get button events
                res = self.lib.dgtpicom_get_button_message(pointer(but), pointer(buttime))
                if res > 0:
                    ack3 = but.value
                    if ack3 == 0x01:
                        logging.info("DGT clock [i2c]: button 0 pressed")
                        DisplayMsg.show(Message.DGT_BUTTON(button=0))
                    if ack3 == 0x02:
                        logging.info("DGT clock [i2c]: button 1 pressed")
                        DisplayMsg.show(Message.DGT_BUTTON(button=1))
                    if ack3 == 0x04:
                        logging.info("DGT clock [i2c]: button 2 pressed")
                        DisplayMsg.show(Message.DGT_BUTTON(button=2))
                    if ack3 == 0x08:
                        logging.info("DGT clock [i2c]: button 3 pressed")
                        DisplayMsg.show(Message.DGT_BUTTON(button=3))
                    if ack3 == 0x10:
                        logging.info("DGT clock [i2c]: button 4 pressed")
                        DisplayMsg.show(Message.DGT_BUTTON(button=4))
                    if ack3 == 0x20:
                        logging.info("DGT clock [i2c]: button on/off pressed")
                        self.lib.dgtpicom_configure()  # restart the clock - cause its OFF
                        self.lib.dgtpicom_set_text(b'shutdown', 0x01, 0, 0)
                        Observable.fire(Event.SHUTDOWN())
                    if ack3 == 0x11:
                        logging.info("DGT clock [i2c]: button left/right pressed")
                        self.lib.dgtpicom_set_text(b'shutdown', 0x01, 0, 0)
                        Observable.fire(Event.SHUTDOWN())
                    if ack3 == 0x40:
                        logging.info("DGT clock [i2c]: lever pressed > right side down")
                    if ack3 == -0x40:
                        logging.info("DGT clock [i2c]: lever pressed > left side down")
                if res < 0:
                    logging.warning('GetButtonMessage returned error %i', res)

                # get time events
                self.lib.dgtpicom_get_time(clktime)

            times = list(clktime.raw)
            counter = (counter + 1) % 10
            if counter == 2:
                DisplayMsg.show(Message.DGT_CLOCK_TIME(time_left=times[:3], time_right=times[3:]))
            if counter == 7:  # issue 150 - force to write something to the board => check for alive connection!
                self.dgtserial.write_board_command([DgtCmd.DGT_RETURN_SERIALNR])  # the code doesnt really matter ;-)
            time.sleep(0.1)

    def _display_on_dgt_pi(self, text, beep=False):
        if len(text) > 11:
            logging.warning('DGT PI clock message too long [%s]', text)
        logging.debug(text)
        text = bytes(text, 'utf-8')
        with self.lock:
            res = self.lib.dgtpicom_set_text(text, 0x03 if beep else 0x00, 0, 0)
            if res < 0:
                logging.warning('SetText returned error %i', res)
                res = self.lib.dgtpicom_configure()
                if res < 0:
                    logging.warning('Configure also failed %i', res)
                else:
                    res = self.lib.dgtpicom_set_text(text, 0x03 if beep else 0x00, 0, 0)
            if res < 0:
                logging.warning('Finally failed %i', res)

    def display_text_on_clock(self, text, beep=False):
        self._display_on_dgt_pi(text, beep)

    def display_move_on_clock(self, move, fen, beep=False):
        bit_board = Board(fen)
        text = self.dgttranslate.move(bit_board.san(move))
        self._display_on_dgt_pi(text, beep)

    def light_squares_revelation_board(self, squares):
        if self.enable_revelation_leds:
            for sq in squares:
                dgt_square = (8 - int(sq[1])) * 8 + ord(sq[0]) - ord('a')
                logging.debug("REV2 light on square %s", sq)
                self.dgtserial.write_board_command([DgtCmd.DGT_SET_LEDS, 0x04, 0x01, dgt_square, dgt_square])

    def clear_light_revelation_board(self):
        if self.enable_revelation_leds:
            self.dgtserial.write_board_command([DgtCmd.DGT_SET_LEDS, 0x04, 0x00, 0, 63])

    def stop_clock(self):
        l_hms = self.time_left
        r_hms = self.time_right
        if l_hms is None and r_hms is None:
            logging.debug('time values not set - no need to stop the clock')
            return
        with self.lock:
            res = self.lib.dgtpicom_set_and_run(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('SetAndRun returned error %i', res)
                res = self.lib.dgtpicom_configure()
                if res < 0:
                    logging.warning('Configure also failed %i', res)
                else:
                    res = self.lib.dgtpicom_set_and_run(0, l_hms[0], l_hms[1], l_hms[2], 0, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = False

    def start_clock(self, time_left, time_right, side):
        l_hms = hours_minutes_seconds(time_left)
        r_hms = hours_minutes_seconds(time_right)
        lr = rr = 0
        if side == 0x01:
            lr = 1
        if side == 0x02:
            rr = 1
        self.time_left = l_hms
        self.time_right = r_hms
        with self.lock:
            res = self.lib.dgtpicom_set_and_run(lr, l_hms[0], l_hms[1], l_hms[2], rr, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('SetAndRun returned error %i', res)
                res = self.lib.dgtpicom_configure()
                if res < 0:
                    logging.warning('Configure also failed %i', res)
                else:
                    res = self.lib.dgtpicom_set_and_run(lr, l_hms[0], l_hms[1], l_hms[2], rr, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = (side != 0x04)

    def end_clock(self, force=False):
        if self.clock_running or force:
            with self.lock:
                res = self.lib.dgtpicom_end_text()
                if res < 0:
                    logging.warning('EndText returned error %i', res)
                    res = self.lib.dgtpicom_configure()
                    if res < 0:
                        logging.warning('Configure also failed %i', res)
                    else:
                        res = self.lib.dgtpicom_end_text()
                if res < 0:
                    logging.warning('Finally failed')
        else:
            logging.debug('DGT clock isnt running - no need for endClock')