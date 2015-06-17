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

import threading
import chess
import logging
from utilities import *


class KeyboardInput(Observable, threading.Thread):
    def __init__(self):
        super(KeyboardInput, self).__init__()

    def run(self):
        while True:
            cmd = input('PicoChess v'+version+':>')

            try:
                # commands like "mode:analysis" or "mode:remote"
                if cmd.startswith('mode:'):
                    mode = cmd.split(':')[1]
                    if mode.lower() == 'analysis':
                        mode = Mode.ANALYSIS
                    elif mode.lower() == 'remote':
                        mode = Mode.REMOTE
                    logging.warning("Mode: {0}".format(mode))
                    self.fire(Event.SET_MODE, mode=mode)
                else:
                    if cmd.startswith('stop'):
                        self.fire(Event.STOP_SEARCH)
                    else:
                        move = chess.Move.from_uci(cmd)
                        self.fire(Event.USER_MOVE, move=move)
            except ValueError:
                logging.warning('Invalid user input [%s]', cmd)


class TerminalDisplay(Display, threading.Thread):
    def __init__(self):
        super(TerminalDisplay, self).__init__()

    def run(self):
        while True:
            # Check if we have something to display
            message = self.message_queue.get()
            if message == Message.BOOK_MOVE:
                print('Book move')
            elif message == Message.COMPUTER_MOVE:
                print('\n' + str(message.game))
                print('Computer move:', message.move)
            elif message == Message.START_NEW_GAME:
                print('New game')
            elif message == Message.SEARCH_STARTED:
                print('Computer is thinking...')
            elif message == Message.NEW_PV:
                print('bestmove: ' + str(message.pv[0]))
