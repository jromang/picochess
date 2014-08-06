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

import queue
import os
from enum import Enum

# picochess version
version = '024'

event_queue = queue.Queue()


class Event(Enum):
    def __new__(cls): # Autonumber
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    # User events
    FEN = ()  # User has moved one or more pieces, and we have a new fen position.
    LEVEL = ()  # User sets engine level (from 1 to 20).
    NEW_GAME = ()  # User starts a new game
    USER_MOVE = ()  # User sends a move
    OPENING_BOOK = ()  # User chooses an opening book

    #Engine event
    BESTMOVE = ()  # Engine has found a move


class Observable(object):
    @staticmethod
    def fire(event, parameter=None):
        event.parameter = parameter
        event_queue.put(event)


# switch/case instruction in python
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


def get_opening_books():
    book_list = sorted(os.listdir('books'))
    library = [('nobook', None)]
    for book in book_list:
        library.append((book[2:book.index('.')], 'books' + os.sep + book))
    return library