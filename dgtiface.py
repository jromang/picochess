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

from chess import Board
from utilities import hours_minutes_seconds, switch, DisplayDgt, DispatchDgt
import logging
import queue
from dgtutil import ClockIcons, ClockSide
from dgtapi import Dgt, DgtApi
from threading import Thread
from dgttranslate import DgtTranslate


class DgtIface(DisplayDgt, Thread):

    """an Interface class for DgtHw, DgtPi, DgtVr."""

    def __init__(self, dgttranslate: DgtTranslate, dgtboard=None):
        super(DgtIface, self).__init__()

        self.dgtboard = dgtboard
        self.dgttranslate = dgttranslate

        self.clock_running = False
        self.enable_dgt_3000 = False
        self.enable_ser_clock = False
        self.time_left = None
        self.time_right = None

    def display_text_on_clock(self, message):
        """override this function."""
        raise NotImplementedError()

    def display_move_on_clock(self, message):
        """override this function."""
        raise NotImplementedError()

    def display_time_on_clock(self, message):
        """override this function."""
        raise NotImplementedError()

    def light_squares_revelation_board(self, squares):
        """override this function."""
        raise NotImplementedError()

    def clear_light_revelation_board(self):
        """override this function."""
        raise NotImplementedError()

    def stop_clock(self, devs):
        """override this function."""
        raise NotImplementedError()

    def _resume_clock(self, side):
        """override this function."""
        raise NotImplementedError()

    def start_clock(self, time_left, time_right, side, devs):
        """override this function."""
        raise NotImplementedError()

    def getName(self):
        return self.__class__.__name__

    def get_san(self, message, is_xl=False):
        """create a chess.board plus a text ready to display on clock."""
        bit_board = Board(message.fen)
        if bit_board.is_legal(message.move):
            move_text = bit_board.san(message.move)
        else:
            logging.warning('[{}] illegal move {} found fen: {}'.format(self.getName(), message.move, message.fen))
            move_text = 'er{}' if is_xl else 'err {}'
            move_text = move_text.format(message.move.uci()[:4])

        if message.side == ClockSide.RIGHT:
            move_text = move_text.rjust(6 if is_xl else 8)
        text = self.dgttranslate.move(move_text)
        return bit_board, text

    def _process_message(self, message):
        for case in switch(message):
            if case(DgtApi.DISPLAY_MOVE):
                self.display_move_on_clock(message)
                break
            if case(DgtApi.DISPLAY_TEXT):
                self.display_text_on_clock(message)
                break
            if case(DgtApi.DISPLAY_TIME):
                self.display_time_on_clock(message)
                break
            if case(DgtApi.LIGHT_CLEAR):
                self.clear_light_revelation_board()
                break
            if case(DgtApi.LIGHT_SQUARES):
                self.light_squares_revelation_board(message.uci_move)
                break
            if case(DgtApi.CLOCK_STOP):
                if self.clock_running:
                    self.stop_clock(message.devs)
                else:
                    logging.debug('[{}] clock is already stopped'.format(self.getName()))
                break
            if case(DgtApi.CLOCK_START):
                # log times
                l_hms = hours_minutes_seconds(message.time_left)
                r_hms = hours_minutes_seconds(message.time_right)
                logging.debug('[{}] last time received from clock l:{} r:{}'
                              .format(self.getName(), self.time_left, self.time_right))
                logging.debug('[{}] sending time to clock l:{} r:{}'.format(self.getName(), l_hms, r_hms))
                self.start_clock(message.time_left, message.time_right, message.side, message.devs)
                break
            if case(DgtApi.CLOCK_VERSION):
                text = self.dgttranslate.text('Y20_picochess', devs={message.dev})
                text.rd = ClockIcons.DOT
                DispatchDgt.fire(text)
                DispatchDgt.fire(Dgt.DISPLAY_TIME(force=True, wait=True, devs={message.dev}))
                if message.dev != 'i2c':
                    self.enable_ser_clock = True
                    if message.main == 2:
                        self.enable_dgt_3000 = True
                break
            if case(DgtApi.CLOCK_TIME):
                logging.debug('[{}] ({}) clock: received time from clock l:{} r:{}'
                              .format(self.getName(), message.dev, message.time_left, message.time_right))
                self.time_left = message.time_left
                self.time_right = message.time_right
                break
            if case():  # Default
                pass

    def _create_task(self, msg):
        self._process_message(msg)

    def run(self):
        """called from threading.Thread by its start() function."""
        logging.info('[{}] dgt_queue ready'.format(self.getName()))
        while True:
            # Check if we have something to display
            try:
                message = self.dgt_queue.get()
                self._create_task(message)
            except queue.Empty:
                pass
