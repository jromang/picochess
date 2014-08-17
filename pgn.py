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


class PgnDisplay(Display, threading.Thread):
    def __init__(self, pgn_file_name):
        super(PgnDisplay, self).__init__()
        self.file_name = pgn_file_name

    def run(self):
        while True:
            #Check if we have something to display
            try:
                message = self.message_queue.get()
                if message == Message.GAME_ENDS:
                    logging.debug('Saving game to [' + self.file_name+']')
                    for move in message.moves:
                        print(move.uci())

            except queue.Empty:
                pass
