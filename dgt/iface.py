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
import queue
from threading import Thread

from chess import Board
from utilities import hms_time, DisplayDgt, DispatchDgt
from dgt.util import ClockIcons, ClockSide
from dgt.api import Dgt
from dgt.translate import DgtTranslate
from dgt.board import DgtBoard


class DgtIface(DisplayDgt, Thread):

    """An Interface class for DgtHw, DgtPi, DgtVr."""

    def __init__(self, dgtboard: DgtBoard):
        super(DgtIface, self).__init__()

        self.dgtboard = dgtboard

        self.side_running = ClockSide.NONE
        self.enable_dgt3000 = False
        self.case_res = True

    def display_text_on_clock(self, message):
        """Override this function."""
        raise NotImplementedError()

    def display_move_on_clock(self, message):
        """Override this function."""
        raise NotImplementedError()

    def display_time_on_clock(self, message):
        """Override this function."""
        raise NotImplementedError()

    def light_squares_on_revelation(self, uci_move):
        """Override this function."""
        raise NotImplementedError()

    def clear_light_on_revelation(self):
        """Override this function."""
        raise NotImplementedError()

    def _resume_clock(self, side):
        """Override this function."""
        raise NotImplementedError()

    def start_clock(self, side, devs):
        """Override this function."""
        raise NotImplementedError()

    def set_clock(self, time_left, time_right, devs):
        """Override this function."""
        raise NotImplementedError()

    def stop_clock(self, devs):
        """Override this function."""
        raise NotImplementedError()

    def get_name(self):
        """Override this function."""
        raise NotImplementedError()

    def get_san(self, message, is_xl=False):
        """Create a chess.board plus a text ready to display on clock."""

        def move(text: str, language: str, capital: bool, short: bool):
            """Return move text for clock display."""
            if short:
                directory = {}
                if language == 'de':
                    directory = {'R': 'T', 'N': 'S', 'B': 'L', 'Q': 'D'}
                if language == 'nl':
                    directory = {'R': 'T', 'N': 'P', 'B': 'L', 'Q': 'D'}
                if language == 'fr':
                    directory = {'R': 'T', 'N': 'C', 'B': 'F', 'Q': 'D', 'K': '@'}
                if language == 'es':
                    directory = {'R': 'T', 'N': 'C', 'B': 'A', 'Q': 'D', 'K': '@'}
                if language == 'it':
                    directory = {'R': 'T', 'N': 'C', 'B': 'A', 'Q': 'D', 'K': '@'}
                for i, j in directory.items():
                    text = text.replace(i, j)
                text = text.replace('@', 'R')  # replace the King "@" from fr, es, it languages
            if capital:
                return text.upper()
            else:
                return text

        bit_board = Board(message.fen, message.uci960)
        if bit_board.is_legal(message.move):
            if message.long:
                move_text = message.move.uci()
            else:
                move_text = bit_board.san(message.move)
        else:
            logging.warning('[%s] illegal move %s found - uci960: %s fen: %s', self.get_name(), message.move,
                            message.uci960, message.fen)
            move_text = 'er{}' if is_xl else 'err {}'
            move_text = move_text.format(message.move.uci()[:4])

        if message.side == ClockSide.RIGHT:
            move_text = move_text.rjust(6 if is_xl else 8)
        return bit_board, move(move_text, message.lang, message.capital and not is_xl, not message.long)

    def _process_message(self, message):
        if self.get_name() not in message.devs:
            return True

        logging.debug('(%s) handle DgtApi: %s started', ','.join(message.devs), message)
        self.case_res = True

        if False:  # switch-case
            pass
        elif isinstance(message, Dgt.DISPLAY_MOVE):
            self.case_res = self.display_move_on_clock(message)
        elif isinstance(message, Dgt.DISPLAY_TEXT):
            self.case_res = self.display_text_on_clock(message)
        elif isinstance(message, Dgt.DISPLAY_TIME):
            self.case_res = self.display_time_on_clock(message)
        elif isinstance(message, Dgt.LIGHT_CLEAR):
            self.case_res = self.clear_light_on_revelation()
        elif isinstance(message, Dgt.LIGHT_SQUARES):
            self.case_res = self.light_squares_on_revelation(message.uci_move)
        elif isinstance(message, Dgt.CLOCK_SET):
            self.case_res = self.set_clock(message.time_left, message.time_right, message.devs)
        elif isinstance(message, Dgt.CLOCK_START):
            self.case_res = self.start_clock(message.side, message.devs)
        elif isinstance(message, Dgt.CLOCK_STOP):
            if self.side_running != ClockSide.NONE:
                self.case_res = self.stop_clock(message.devs)
            else:
                logging.debug('(%s) clock is already stopped', ','.join(message.devs))
        elif isinstance(message, Dgt.CLOCK_VERSION):
            if 'i2c' in message.devs:
                logging.debug('(i2c) clock found => starting the board connection')
                self.dgtboard.run()  # finally start the serial board connection - see picochess.py
            else:
                if message.main == 2:
                    self.enable_dgt3000 = True
        else:  # switch-default
            pass
        logging.debug('(%s) handle DgtApi: %s ended', ','.join(message.devs), message)
        return self.case_res

    def _create_task(self, msg):
        res = self._process_message(msg)
        if not res:
            logging.warning('DgtApi command %s failed result: %s', msg, res)

    def run(self):
        """Call by threading.Thread start() function."""
        logging.info('[%s] dgt_queue ready', self.get_name())
        while True:
            # Check if we have something to display
            try:
                message = self.dgt_queue.get()
                self._create_task(message)
            except queue.Empty:
                pass
