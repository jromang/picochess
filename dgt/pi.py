# Copyright (C) 2013-2018 Jean-Francois Romang (jromang@posteo.de)
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

import logging
import time
from threading import Lock, Timer
from ctypes import cdll, c_byte, create_string_buffer, pointer
from platform import machine

from utilities import DisplayMsg, hms_time
from dgt.api import Message
from dgt.util import ClockIcons, ClockSide
from dgt.translate import DgtTranslate
from dgt.board import DgtBoard
from dgt.iface import DgtIface


class DgtPi(DgtIface):

    """Handle the DgtPi communication."""

    def __init__(self, dgtboard: DgtBoard):
        super(DgtPi, self).__init__(dgtboard)

        self.lib_lock = Lock()
        self.lib = cdll.LoadLibrary('etc/dgtpicom.x86.so' if machine() == 'x86_64' else 'etc/dgtpicom.so')

        # keep the last time to find out errorous DGT_MSG_BWTIME messages (error: current time > last time)
        self.r_time = 3600 * 10  # max value cause 10h cant be reached by clock
        self.l_time = 3600 * 10  # max value cause 10h cant be reached by clock

        self.in_settime = False  # this is true between set_clock and clock_start => use set values instead of clock

        self._startup_i2c_clock()
        incoming_clock_thread = Timer(0, self._process_incoming_clock_forever)
        incoming_clock_thread.start()

    def _startup_i2c_clock(self):
        while self.lib.dgtpicom_init() < 0:
            logging.warning('Init() failed - Jack half connected?')
            DisplayMsg.show(Message.DGT_JACK_CONNECTED_ERROR())
            time.sleep(0.5)  # dont flood the log
        if self.lib.dgtpicom_configure() < 0:
            logging.warning('Configure() failed - Jack connected back?')
            DisplayMsg.show(Message.DGT_JACK_CONNECTED_ERROR())
        DisplayMsg.show(Message.DGT_CLOCK_VERSION(main=2, sub=2, dev='i2c', text=None))

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
                        logging.info('(i2c) clock button 0 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=0, dev='i2c'))
                    if ack3 == 0x02:
                        logging.info('(i2c) clock button 1 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=1, dev='i2c'))
                    if ack3 == 0x04:
                        logging.info('(i2c) clock button 2 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=2, dev='i2c'))
                    if ack3 == 0x08:
                        logging.info('(i2c) clock button 3 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=3, dev='i2c'))
                    if ack3 == 0x10:
                        logging.info('(i2c) clock button 4 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=4, dev='i2c'))
                    if ack3 == 0x20:
                        logging.info('(i2c) clock button on/off pressed')
                        self.lib.dgtpicom_configure()  # restart the clock - cause its OFF
                        DisplayMsg.show(Message.DGT_BUTTON(button=0x11, dev='i2c'))
                    if ack3 == 0x11:
                        logging.info('(i2c) clock button 0+4 pressed')
                        DisplayMsg.show(Message.DGT_BUTTON(button=0x11, dev='i2c'))
                    if ack3 == 0x40:
                        logging.info('(i2c) clock lever pressed > right side down')
                        DisplayMsg.show(Message.DGT_BUTTON(button=0x40, dev='i2c'))
                    if ack3 == -0x40:
                        logging.info('(i2c) clock lever pressed > left side down')
                        DisplayMsg.show(Message.DGT_BUTTON(button=-0x40, dev='i2c'))
                if res < 0:
                    logging.warning('GetButtonMessage returned error %i', res)

                # get time events
                self.lib.dgtpicom_get_time(clktime)

            times = list(clktime.raw)
            counter = (counter + 1) % 10
            if counter == 0:
                l_hms = times[:3]
                r_hms = times[3:]
                logging.info('(i2c) clock new time received l:%s r:%s', l_hms, r_hms)
                if self.in_settime:
                    logging.info('(i2c) clock still not finished set time, sending old time')
                else:
                    # DgtPi needs 2secs for a stopped clock to return the correct(!) time
                    # we make it easy here and just set the time from the side counting down
                    if self.side_running == ClockSide.LEFT:
                        self.l_time = l_hms[0] * 3600 + l_hms[1] * 60 + l_hms[2]
                    if self.side_running == ClockSide.RIGHT:
                        self.r_time = r_hms[0] * 3600 + r_hms[1] * 60 + r_hms[2]
                text = Message.DGT_CLOCK_TIME(time_left=self.l_time, time_right=self.r_time, connect=True, dev='i2c')
                DisplayMsg.show(text)
            time.sleep(0.1)

    def _run_configure(self):
        res = self.lib.dgtpicom_configure()
        if res < 0:
            logging.warning('Configure() also failed %i, resetting the dgtpi clock', res)
            self.lib.dgtpicom_stop()
            self.lib.dgtpicom_init()

    def _display_on_dgt_pi(self, text: str, beep=False, left_icons=ClockIcons.NONE, right_icons=ClockIcons.NONE):
        if len(text) > 11:
            logging.warning('(i2c) clock message too long [%s]', text)
        logging.debug('[%s]', text)
        text = bytes(text, 'utf-8')
        with self.lib_lock:
            res = self.lib.dgtpicom_set_text(text, 0x03 if beep else 0x00, left_icons.value, right_icons.value)
            if res < 0:
                logging.warning('SetText() returned error %i, running configure', res)
                self._run_configure()
                res = self.lib.dgtpicom_set_text(text, 0x03 if beep else 0x00, left_icons.value, right_icons.value)
        if res < 0:
            logging.warning('finally failed %i', res)
            return False
        else:
            return True

    def display_text_on_clock(self, message):
        """Display a text on the dgtpi."""
        text = message.l
        if text is None:
            text = message.m
        if self.get_name() not in message.devs:
            logging.debug('ignored %s - devs: %s', text, message.devs)
            return
        left_icons = message.ld if hasattr(message, 'ld') else ClockIcons.NONE
        right_icons = message.rd if hasattr(message, 'rd') else ClockIcons.NONE
        return self._display_on_dgt_pi(text, message.beep, left_icons, right_icons)

    def display_move_on_clock(self, message):
        """Display a move on the dgtpi."""
        bit_board, text = self.get_san(message)
        text = '{:3d}{:s}'.format(bit_board.fullmove_number, text)
        if self.get_name() not in message.devs:
            logging.debug('ignored %s - devs: %s', text, message.devs)
            return True
        left_icons = message.ld if hasattr(message, 'ld') else ClockIcons.DOT
        right_icons = message.rd if hasattr(message, 'rd') else ClockIcons.NONE
        return self._display_on_dgt_pi(text, message.beep, left_icons, right_icons)

    def display_time_on_clock(self, message):
        """Display the time on the dgtpi."""
        if self.get_name() not in message.devs:
            logging.debug('ignored endText - devs: %s', message.devs)
            return True
        if self.side_running != ClockSide.NONE or message.force:
            with self.lib_lock:
                res = self.lib.dgtpicom_end_text()
                if res < 0:
                    logging.warning('EndText() returned error %i, running configure', res)
                    self._run_configure()
                    res = self.lib.dgtpicom_end_text()
            if res < 0:
                logging.warning('finally failed %i', res)
                return False
        else:
            logging.debug('(i2c) clock isnt running - no need for endText')
        return True

    def light_squares_on_revelation(self, uci_move: str):
        """Handle this by hw.py."""
        return True

    def clear_light_on_revelation(self):
        """Handle this by hw.py."""
        return True

    def stop_clock(self, devs: set):
        """Stop the dgtpi."""
        if self.get_name() not in devs:
            logging.debug('ignored stopClock - devs: %s', devs)
            return True
        logging.debug('(%s) clock sending stop time to clock l:%s r:%s', ','.join(devs),
                      hms_time(self.l_time), hms_time(self.r_time))
        return self._resume_clock(ClockSide.NONE)

    def _resume_clock(self, side: ClockSide):
        if self.l_time >= 3600 * 10 or self.r_time >= 3600 * 10:
            logging.warning('time values not set - abort function')
            return False

        l_run = r_run = 0
        if side == ClockSide.LEFT:
            l_run = 1
        if side == ClockSide.RIGHT:
            r_run = 1
        with self.lib_lock:
            res = self.lib.dgtpicom_run(l_run, r_run)
            if res < 0:
                logging.warning('Run() returned error %i, running configure', res)
                self._run_configure()
                res = self.lib.dgtpicom_run(l_run, r_run)
        if res < 0:
            logging.warning('finally failed %i', res)
            return False
        else:
            self.side_running = side
            return True

    def start_clock(self, side: ClockSide, devs: set):
        """Start the dgtpi."""
        if self.get_name() not in devs:
            logging.debug('ignored startClock - devs: %s', devs)
            return True
        l_hms = hms_time(self.l_time)
        r_hms = hms_time(self.r_time)
        logging.debug('(%s) clock sending start time to clock l:%s r:%s', ','.join(devs), l_hms, r_hms)

        l_run = r_run = 0
        if side == ClockSide.LEFT:
            l_run = 1
        if side == ClockSide.RIGHT:
            r_run = 1
        with self.lib_lock:
            res = self.lib.dgtpicom_set_and_run(l_run, l_hms[0], l_hms[1], l_hms[2],
                                                r_run, r_hms[0], r_hms[1], r_hms[2])
            if res < 0:
                logging.warning('SetAndRun() returned error %i, running configure', res)
                self._run_configure()
                res = self.lib.dgtpicom_set_and_run(l_run, l_hms[0], l_hms[1], l_hms[2],
                                                    r_run, r_hms[0], r_hms[1], r_hms[2])
        if res < 0:
            logging.warning('finally failed %i', res)
            return False
        else:
            self.side_running = side
            Timer(0.9, self.out_settime).start()  # delay abit cause the clock needs time to update its time result
            return True

    def out_settime(self):
        self.in_settime = False

    def set_clock(self, time_left: int, time_right: int, devs: set):
        """Set the dgtpi."""
        if self.get_name() not in devs:
            logging.debug('ignored setClock - devs: %s', devs)
            return True

        l_hms = hms_time(time_left)
        r_hms = hms_time(time_right)
        logging.debug('(%s) clock received last time from clock l:%s r:%s [ign]', ','.join(devs),
                      hms_time(self.l_time), hms_time(self.r_time))
        logging.debug('(%s) clock sending set time to clock l:%s r:%s [use]', ','.join(devs), l_hms, r_hms)

        self.in_settime = True
        self.l_time = time_left
        self.r_time = time_right
        return True

    def get_name(self):
        """Get name."""
        return 'i2c'
