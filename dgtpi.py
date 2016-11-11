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
from ctypes import *
from utilities import *
from threading import Lock, Timer


class DgtPi(DgtIface):
    def __init__(self, dgtserial, dgttranslate):
        super(DgtPi, self).__init__(dgtserial, dgttranslate)

        self.lib_lock = Lock()
        self.lib = cdll.LoadLibrary('dgt/dgtpicom.so')

        self._startup_i2c_clock()
        incoming_clock_thread = Timer(0, self._process_incoming_clock_forever)
        incoming_clock_thread.start()
        # self.dgtserial.run()

    def _startup_i2c_clock(self):
        while self.lib.dgtpicom_init() < 0:
            logging.warning('Init failed - Jack half connected?')
            DisplayMsg.show(Message.JACK_CONNECTED_ERROR())
            time.sleep(0.5)  # dont flood the log
        if self.lib.dgtpicom_configure() < 0:
            logging.warning('Configure failed - Jack connected back?')
            DisplayMsg.show(Message.JACK_CONNECTED_ERROR())
        DisplayMsg.show(Message.DGT_CLOCK_VERSION(main=2, sub=2, attached="i2c"))

    def _process_incoming_clock_forever(self):
        but = c_byte(0)
        buttime = c_byte(0)
        clktime = create_string_buffer(6)
        counter = 0
        logging.info('incoming_clock ready')
        while True:
            with self.lib_lock:
                # get button events
                res = self.lib.dgtpicom_get_button_message(pointer(but), pointer(buttime))
                if res > 0:
                    ack3 = but.value
                    if ack3 == 0x01:
                        logging.info('DGT clock [i2c]: button 0 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=0))
                    if ack3 == 0x02:
                        logging.info('DGT clock [i2c]: button 1 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=1))
                    if ack3 == 0x04:
                        logging.info('DGT clock [i2c]: button 2 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=2))
                    if ack3 == 0x08:
                        logging.info('DGT clock [i2c]: button 3 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=3))
                    if ack3 == 0x10:
                        logging.info('DGT clock [i2c]: button 4 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=4))
                    if ack3 == 0x20:
                        logging.info('DGT clock [i2c]: button on/off pressed')
                        self.lib.dgtpicom_configure()  # restart the clock - cause its OFF
                        DisplayMsg.show(Message.DGT_BUTTON(button=0x11))
                    if ack3 == 0x11:
                        logging.info('DGT clock [i2c]: button 0+4 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=0x11))
                    if ack3 == 0x40:
                        logging.info('DGT clock [i2c]: lever pressed > right side down')
                        DisplayMsg.show(Message.DGT_BUTTON(button=0x40))
                    if ack3 == -0x40:
                        logging.info('DGT clock [i2c]: lever pressed > left side down')
                        DisplayMsg.show(Message.DGT_BUTTON(button=-0x40))
                if res < 0:
                    logging.warning('GetButtonMessage returned error %i', res)

                # get time events
                self.lib.dgtpicom_get_time(clktime)

            times = list(clktime.raw)
            counter = (counter + 1) % 10
            if counter == 0:
                DisplayMsg.show(Message.DGT_CLOCK_TIME(time_left=times[:3], time_right=times[3:]))
            time.sleep(0.1)

    def _display_on_dgt_pi(self, text, beep=False, left_dots=ClockDots.NONE, right_dots=ClockDots.NONE):
        if len(text) > 11:
            logging.warning('DGT PI clock message too long [%s]', text)
        logging.debug(text)
        text = bytes(text, 'utf-8')
        with self.lib_lock:
            res = self.lib.dgtpicom_set_text(text, 0x03 if beep else 0x00, left_dots.value, right_dots.value)
            if res < 0:
                logging.warning('SetText returned error %i', res)
                res = self.lib.dgtpicom_configure()
                if res < 0:
                    logging.warning('Configure also failed %i', res)
                else:
                    res = self.lib.dgtpicom_set_text(text, 0x03 if beep else 0x00, left_dots.value, right_dots.value)
            if res < 0:
                logging.warning('Finally failed %i', res)

    def display_text_on_clock(self, message):
        if 'i2c' not in message.devs:
            return
        text = message.l
        if text is None:
            text = message.m
        left_dots = message.ld if hasattr(message, 'ld') else ClockDots.NONE
        right_dots = message.rd if hasattr(message, 'rd') else ClockDots.NONE
        self._display_on_dgt_pi(text, message.beep, left_dots, right_dots)

    def display_move_on_clock(self, message):
        bit_board = Board(message.fen)
        move_text = bit_board.san(message.move)
        if message.side == ClockSide.RIGHT:
            move_text = move_text.rjust(8)
        text = self.dgttranslate.move(move_text)
        text = '{:3d}{:s}'.format(bit_board.fullmove_number, text)
        left_dots = message.ld if hasattr(message, 'ld') else ClockDots.DOT
        right_dots = message.rd if hasattr(message, 'rd') else ClockDots.NONE
        self._display_on_dgt_pi(text, message.beep, left_dots, right_dots)

    def display_time_on_clock(self, force=False):
        if self.clock_running or force:
            with self.lib_lock:
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

    def light_squares_revelation_board(self, uci_move):
        pass

    def clear_light_revelation_board(self):
        pass

    def stop_clock(self):
        self.resume_clock(ClockSide.NONE)

    def resume_clock(self, side):
        l_hms = self.time_left
        r_hms = self.time_right
        if l_hms is None or r_hms is None:
            logging.warning('time values not set - abort function')
            return

        lr = rr = 0
        if side == ClockSide.LEFT:
            lr = 1
        if side == ClockSide.RIGHT:
            rr = 1
        with self.lib_lock:
            res = self.lib.dgtpicom_run(lr, rr)
            if res < 0:
                logging.warning('Run returned error %i', res)
                res = self.lib.dgtpicom_configure()
                if res < 0:
                    logging.warning('Configure also failed %i', res)
                else:
                    res = self.lib.dgtpicom_run(lr, rr)
            if res < 0:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = (side != ClockSide.NONE)

    def start_clock(self, time_left, time_right, side):
        self.time_left = hours_minutes_seconds(time_left)
        self.time_right = hours_minutes_seconds(time_right)
        l_hms = self.time_left
        r_hms = self.time_right

        lr = rr = 0
        if side == ClockSide.LEFT:
            lr = 1
        if side == ClockSide.RIGHT:
            rr = 1
        with self.lib_lock:
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
                self.clock_running = (side != ClockSide.NONE)
