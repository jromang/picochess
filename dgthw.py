# Copyright (C) 2013-2017 Jean-Francois Romang (jromang@posteo.de)
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

from dgtiface import DgtIface
from utilities import hours_minutes_seconds
import logging
from dgtutil import ClockIcons, ClockSide, DgtClk, DgtCmd
from threading import Lock
from dgttranslate import DgtTranslate
from dgtboard import DgtBoard


class DgtHw(DgtIface):

    """Handle the DgtXL/3000 communication"""

    def __init__(self, dgttranslate: DgtTranslate, dgtboard: DgtBoard):
        super(DgtHw, self).__init__(dgttranslate, dgtboard)

        self.lib_lock = Lock()
        self.dgtboard.run()

    def _check_clock(self, text: str):
        if not self.enable_ser_clock:
            logging.debug('(ser) clock still not found. Ignore [%s]', text)
            self.dgtboard.startup_serial_clock()
            return False
        return True

    def _display_on_dgt_xl(self, text: str, beep=False, left_icons=ClockIcons.NONE, right_icons=ClockIcons.NONE):
        text = text.ljust(6)
        if len(text) > 6:
            logging.warning('(ser) clock message too long [%s]', text)
        logging.debug(text)
        with self.lib_lock:
            res = self.dgtboard.set_text_xl(text, 0x03 if beep else 0x00, left_icons, right_icons)
            if not res:
                logging.warning('Finally failed %i', res)

    def _display_on_dgt_3000(self, text: str, beep=False, left_icons=ClockIcons.NONE, right_icons=ClockIcons.NONE):
        text = text.ljust(8)
        if len(text) > 8:
            logging.warning('(ser) clock message too long [%s]', text)
        logging.debug(text)
        text = bytes(text, 'utf-8')
        with self.lib_lock:
            res = self.dgtboard.set_text_3k(text, 0x03 if beep else 0x00, left_icons, right_icons)
            if not res:
                logging.warning('Finally failed %i', res)

    def display_text_on_clock(self, message):
        """display a text on the dgtxl/3k."""
        display_m = self.enable_dgt_3000 and not self.dgtboard.use_revelation_leds
        text = message.m if display_m else message.s
        if text is None:
            text = message.l if display_m else message.m
        if 'ser' not in message.devs:
            logging.debug('ignored message cause of devs [{}]'.format(text))
            return
        left_icons = message.ld if hasattr(message, 'ld') else ClockIcons.NONE
        right_icons = message.rd if hasattr(message, 'rd') else ClockIcons.NONE

        if not self._check_clock(text):
            return
        if display_m:
            self._display_on_dgt_3000(text, message.beep, left_icons, right_icons)
        else:
            self._display_on_dgt_xl(text, message.beep, left_icons, right_icons)

    def display_move_on_clock(self, message):
        """display a move on the dgtxl/3k."""
        left_icons = message.ld if hasattr(message, 'ld') else ClockIcons.NONE
        right_icons = message.rd if hasattr(message, 'rd') else ClockIcons.NONE
        display_m = self.enable_dgt_3000 and not self.dgtboard.use_revelation_leds
        if display_m:
            bit_board, text = self.get_san(message)
        else:
            text = message.move.uci()
            if message.side == ClockSide.RIGHT:
                text = text.rjust(6)

        if 'ser' not in message.devs:
            logging.debug('ignored message cause of devs [{}]'.format(text))
            return
        if self._check_clock(text):
            if display_m:
                self._display_on_dgt_3000(text, message.beep, left_icons, right_icons)
            else:
                self._display_on_dgt_xl(text, message.beep, left_icons, right_icons)

    def display_time_on_clock(self, message):
        """display the time on the dgtxl/3k."""
        if 'ser' not in message.devs:
            logging.debug('ignored message cause of devs [endText]')
            return
        if self.clock_running or message.force:
            with self.lib_lock:
                if self._check_clock('END_TEXT'):
                    if self.time_left is None or self.time_right is None:
                        logging.debug('time values not set - abort function')
                    else:
                        self.dgtboard.end_text()
        else:
            logging.debug('(ser) clock isnt running - no need for endText')

    def light_squares_revelation_board(self, uci_move: str):
        """light the Rev2 leds."""
        if self.dgtboard.use_revelation_leds:
            logging.debug("REV2 lights on move {}".format(uci_move))
            fr = (8 - int(uci_move[1])) * 8 + ord(uci_move[0]) - ord('a')
            to = (8 - int(uci_move[3])) * 8 + ord(uci_move[2]) - ord('a')
            self.dgtboard.write_command([DgtCmd.DGT_SET_LEDS, 0x04, 0x01, fr, to, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])

    def clear_light_revelation_board(self):
        """clear the Rev2 leds."""
        if self.dgtboard.use_revelation_leds:
            logging.debug('REV2 lights turned off')
            self.dgtboard.write_command([DgtCmd.DGT_SET_LEDS, 0x04, 0x00, 0, 63, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])

    def stop_clock(self, devs: set):
        """stop the dgtxl/3k."""
        if 'ser' not in devs:
            logging.debug('ignored message cause of devs [stopClock]')
            return
        self._resume_clock(ClockSide.NONE)

    def _resume_clock(self, side: ClockSide):
        if not self._check_clock('RESUME_CLOCK'):
            return
        l_hms = self.time_left
        r_hms = self.time_right
        if l_hms is None or r_hms is None:
            logging.debug('time values not set - abort function')
            return

        l_run = r_run = 0
        if side == ClockSide.LEFT:
            l_run = 1
        if side == ClockSide.RIGHT:
            r_run = 1
        with self.lib_lock:
            res = self.dgtboard.set_and_run(l_run, l_hms[0], l_hms[1], l_hms[2], r_run, r_hms[0], r_hms[1], r_hms[2])
            if not res:
                logging.warning('Finally failed %i', res)
            else:
                self.clock_running = (side != ClockSide.NONE)
            # this is needed for some(!) clocks
            self.dgtboard.end_text()

    def start_clock(self, time_left: int, time_right: int, side: ClockSide, devs: set):
        """start the dgtxl/3k."""
        if 'ser' not in devs:
            logging.debug('ignored message cause of devs [startClock]')
            return
        self.time_left = hours_minutes_seconds(time_left)
        self.time_right = hours_minutes_seconds(time_right)
        self._resume_clock(side)
