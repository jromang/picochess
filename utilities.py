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
from enum import Enum, unique

# picochess version
version = '024'

event_queue = queue.Queue()
display_devices = []


class AutoNumber(Enum):
    def __new__(cls): # Autonumber
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class Event(AutoNumber):
    # User events
    FEN = ()  # User has moved one or more pieces, and we have a new fen position.
    LEVEL = ()  # User sets engine level (from 1 to 20).
    NEW_GAME = ()  # User starts a new game
    USER_MOVE = ()  # User sends a move
    OPENING_BOOK = ()  # User chooses an opening book
    SET_MODE = ()  # Change interaction mode
    #Engine events
    BEST_MOVE = ()  # Engine has found a move


class Message(AutoNumber):
    #Messages to display devices
    COMPUTER_MOVE = ()  # Show computer move
    BOOK_MOVE = ()  # Show book move
    INTERACTION_MODE = ()  # Interaction mode
    START_NEW_GAME = ()
    COMPUTER_MOVE_DONE_ON_BOARD = ()  # User has done the compute move on board


@unique
class Mode(Enum):
    #Interaction modes
    BOOK = 0
    ANALYSIS = 1
    PLAY_WHITE = 2
    KIBITZ = 3
    OBSERVE = 4
    PLAY_BLACK = 5


class Observable(object):  # Input devices are observable
    def __init__(self):
        super(Observable, self).__init__()

    @staticmethod
    def fire(event, parameter=None):
        event.parameter = parameter
        event_queue.put(event)


class Display(object):  # Display devices (DGT XL clock, Piface LCD, pgn file...)
    def __init__(self):
        super(Display, self).__init__()
        self.message_queue = queue.Queue()
        display_devices.append(self)

    @staticmethod
    def show(type, message=None):  # Sends a message on each display device
        for display in display_devices:
            display.message_queue.put((type, message))


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