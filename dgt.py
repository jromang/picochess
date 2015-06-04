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

import logging
import queue
import serial as pyserial
import chess
import time

from timecontrol import *
from struct import unpack
from collections import OrderedDict
from utilities import *

try:
    import enum
except ImportError:  # Python 3.3 support
    import enum34 as enum
try:
    import asyncio
except ImportError:  # Python 3.3 support
    import asyncio34 as asyncio


@enum.unique
class Commands(enum.Enum):
    """ COMMAND CODES FROM PC TO BOARD """
    # Commands not resulting in returning messages:
    DGT_SEND_RESET = 0x40  # Puts the board in IDLE mode, cancelling any UPDATE mode
    DGT_STARTBOOTLOADER = 0x4e  # Makes a long jump to the FC00 boot loader code. Start FLIP now
    # Commands resulting in returning message(s):
    DGT_SEND_CLK = 0x41  # Results in a DGT_MSG_BWTIME message
    DGT_SEND_BRD = 0x42  # Results in a DGT_MSG_BOARD_DUMP message
    DGT_SEND_UPDATE = 0x43  # Results in DGT_MSG_FIELD_UPDATE messages and DGT_MSG_BWTIME messages
                            # as long as the board is in UPDATE mode
    DGT_SEND_UPDATE_BRD = 0x44  # Results in DGT_MSG_FIELD_UPDATE messages as long as the board is in UPDATE_BOARD mode
    DGT_RETURN_SERIALNR = 0x45  # Results in a DGT_MSG_SERIALNR message
    DGT_RETURN_BUSADRES = 0x46  # Results in a DGT_MSG_BUSADRES message
    DGT_SEND_TRADEMARK = 0x47  # Results in a DGT_MSG_TRADEMARK message
    DGT_SEND_EE_MOVES = 0x49  # Results in a DGT_MSG_EE_MOVES message
    DGT_SEND_UPDATE_NICE = 0x4b  # Results in DGT_MSG_FIELD_UPDATE messages and DGT_MSG_BWTIME messages,
                                 # the latter only at time changes, as long as the board is in UPDATE_NICE mode
    DGT_SEND_BATTERY_STATUS = 0x4c  # New command for bluetooth board. Requests the battery status from the board.
    DGT_SEND_VERSION = 0x4d  # Results in a DGT_MSG_VERSION message
    DGT_SEND_BRD_50B = 0x50  # Results in a DGT_MSG_BOARD_DUMP_50 message: only the black squares
    DGT_SCAN_50B = 0x51  # Sets the board in scanning only the black squares. This is written in EEPROM
    DGT_SEND_BRD_50W = 0x52  # Results in a DGT_MSG_BOARD_DUMP_50 message: only the black squares
    DGT_SCAN_50W = 0x53  # Sets the board in scanning only the black squares. This is written in EEPROM.
    DGT_SCAN_100 = 0x54  # Sets the board in scanning all squares. This is written in EEPROM
    DGT_RETURN_LONG_SERIALNR = 0x55  # Results in a DGT_LONG_SERIALNR message
    DGT_SET_LEDS = 0x60  # Only for the Revelation II to switch a LED pattern on. This is a command that
                         # has three extra bytes with data.
    #Clock commands, returns ACK message if mode is in UPDATE or UPDATE_NICE
    DGT_CLOCK_MESSAGE = 0x2b  # This message contains a command for the clock.


class Clock(enum.Enum):
    DGT_CMD_CLOCK_DISPLAY = 0x01  # This command can control the segments of six 7-segment characters,
                                  # two dots, two semicolons and the two '1' symbols.
    DGT_CMD_CLOCK_ICONS = 0x02  # Used to control the clock icons like flags etc.
    DGT_CMD_CLOCK_END = 0x03  # This command clears the message and brings the clock back to the
                              # normal display (showing clock times).
    DGT_CMD_CLOCK_BUTTON = 0x08  # Requests the current button pressed (if any).
    DGT_CMD_CLOCK_VERSION = 0x09  # This commands requests the clock version.
    DGT_CMD_CLOCK_SETNRUN = 0x0a  # This commands controls the clock times and counting direction, when
                                  # the clock is in mode 23. A clock can be paused or counting down. But
                                  # counting up isn't supported on current DGT XL's (1.14 and lower) yet.
    DGT_CMD_CLOCK_BEEP = 0x0b  # This clock command turns the beep on, for a specified time (64ms * byte 5)
    DGT_CMD_CLOCK_ASCII = 0x0c  # This clock commands sends a ASCII message to the clock that
                                # can be displayed only by the DGT3000.
    DGT_CMD_CLOCK_START_MESSAGE = 0x03
    DGT_CMD_CLOCK_END_MESSAGE = 0x00


@enum.unique
class Pieces(enum.Enum):
    #Piece codes for chess pieces:
    EMPTY = 0x00
    WPAWN = 0x01
    WROOK = 0x02
    WKNIGHT = 0x03
    WBISHOP = 0x04
    WKING = 0x05
    WQUEEN = 0x06
    BPAWN = 0x07
    BROOK = 0x08
    BKNIGHT = 0x09
    BBISHOP = 0x0a
    BKING = 0x0b
    BQUEEN = 0x0c
    PIECE1 = 0x0d #  Magic piece: Draw
    PIECE2 = 0x0e #  Magic piece: White win
    PIECE3 = 0x0f #  Magic piece: Black win


class Messages(enum.IntEnum):
    """ DESCRIPTION OF THE MESSAGES FROM BOARD TO PC """
    MESSAGE_BIT = 0x80 #  The Message ID is the logical OR of MESSAGE_BIT and ID code
    #ID codes
    DGT_NONE = 0x00
    DGT_BOARD_DUMP = 0x06
    DGT_BWTIME = 0x0d
    DGT_FIELD_UPDATE = 0x0e
    DGT_EE_MOVES = 0x0f
    DGT_BUSADRES = 0x10
    DGT_SERIALNR = 0x11
    DGT_TRADEMARK = 0x12
    DGT_VERSION = 0x13
    DGT_BOARD_DUMP_50B = 0x14  # Added for Draughts board
    DGT_BOARD_DUMP_50W = 0x15  # Added for Draughts board
    DGT_BATTERY_STATUS = 0x20  # Added for Bluetooth board
    DGT_LONG_SERIALNR = 0x22  # Added for Bluetooth board
    DGT_MSG_BOARD_DUMP = (MESSAGE_BIT | DGT_BOARD_DUMP)  # DGT_MSG_BOARD_DUMP is the message that follows
                                                         # on a DGT_SEND_BOARD command
    DGT_SIZE_BOARD_DUMP = 67
    DGT_SIZE_BOARD_DUMP_DRAUGHTS = 103
    DGT_MSG_BOARD_DUMP_50B = (MESSAGE_BIT|DGT_BOARD_DUMP_50B)
    DGT_SIZE_BOARD_DUMP_50B = 53
    DGT_MSG_BOARD_DUMP_50W = (MESSAGE_BIT|DGT_BOARD_DUMP_50W)
    DGT_SIZE_BOARD_DUMP_50W = 53
    DGT_MSG_BWTIME = (MESSAGE_BIT | DGT_BWTIME)
    DGT_SIZE_BWTIME = 10
    DGT_MSG_FIELD_UPDATE = (MESSAGE_BIT | DGT_FIELD_UPDATE)
    DGT_SIZE_FIELD_UPDATE = 5
    DGT_MSG_TRADEMARK = (MESSAGE_BIT | DGT_TRADEMARK)
    DGT_MSG_BUSADRES = (MESSAGE_BIT | DGT_BUSADRES)
    DGT_SIZE_BUSADRES = 5
    DGT_MSG_SERIALNR = (MESSAGE_BIT | DGT_SERIALNR)
    DGT_SIZE_SERIALNR = 8
    DGT_MSG_LONG_SERIALNR = (MESSAGE_BIT | DGT_LONG_SERIALNR)
    DGT_SIZE_LONG_SERIALNR = 13
    DGT_MSG_VERSION = (MESSAGE_BIT | DGT_VERSION)
    DGT_SIZE_VERSION = 5
    DGT_MSG_BATTERY_STATUS = (MESSAGE_BIT | DGT_BATTERY_STATUS)
    DGT_SIZE_BATTERY_STATUS = 7
    DGT_MSG_EE_MOVES = (MESSAGE_BIT | DGT_EE_MOVES)
    # Definition of the one-byte EEPROM message codes
    EE_POWERUP = 0x6a
    EE_EOF = 0x6b
    EE_FOURROWS = 0x6c
    EE_EMPTYBOARD = 0x6d
    EE_DOWNLOADED = 0x6e
    EE_BEGINPOS = 0x6f
    EE_BEGINPOS_ROT = 0x7a
    EE_START_TAG = 0x7b
    EE_WATCHDOG_ACTION = 0x7c
    EE_FUTURE_1 = 0x7d
    EE_FUTURE_2 = 0x7e
    EE_NOP = 0x7f
    EE_NOP2 = 0x00

INITIAL_BOARD_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

char_to_DGTXL = {
    '0': 0x01 | 0x02 | 0x20 | 0x08 | 0x04 | 0x10,  '1':  0x02 | 0x04,  '2':  0x01 | 0x40 | 0x08 | 0x02 | 0x10,
    '3': 0x01 | 0x40 | 0x08 | 0x02 | 0x04, '4': 0x20 | 0x04 | 0x40 | 0x02,  '5': 0x01 | 0x40 | 0x08 | 0x20 | 0x04,
    '6': 0x01 | 0x40 | 0x08 | 0x20 | 0x04 | 0x10, '7': 0x02 | 0x04 | 0x01,
    '8': 0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10 | 0x08, '9': 0x01 | 0x40 | 0x08 | 0x02 | 0x04 | 0x20,
    'a': 0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10, 'b': 0x20 | 0x04 | 0x40 | 0x08 | 0x10,  'c': 0x01 | 0x20 | 0x10 | 0x08,
    'd': 0x10 | 0x40 | 0x08 | 0x02 | 0x04, 'e': 0x01 | 0x40 | 0x08 | 0x20 | 0x10, 'f': 0x01 | 0x40 | 0x20 | 0x10,
    'g': 0x01 | 0x20 | 0x10 | 0x08 | 0x04, 'h': 0x20 | 0x10 | 0x04 | 0x40, 'i': 0x02 | 0x04,
    'j': 0x02 | 0x04 | 0x08 | 0x10, 'k': 0x01 | 0x20 | 0x40 | 0x04 | 0x10, 'l': 0x20 | 0x10 | 0x08,
    'm': 0x01 | 0x40 | 0x04 | 0x10, 'n': 0x40 | 0x04 | 0x10, 'o': 0x40 | 0x04 | 0x10 | 0x08,
    'p': 0x01 | 0x40 | 0x20 | 0x10 | 0x02,  'q': 0x01 | 0x40 | 0x20 | 0x04 | 0x02, 'r': 0x40 | 0x10,
    's': 0x01 | 0x40 | 0x08 | 0x20 | 0x04, 't': 0x20 | 0x10 | 0x08 | 0x40, 'u': 0x08 | 0x02 | 0x20 | 0x04 | 0x10,
    'v': 0x08 | 0x02 | 0x20,  'w': 0x40 | 0x08 | 0x20 | 0x02, 'x': 0x20 | 0x10 | 0x04 | 0x40 | 0x02,
    'y': 0x20 | 0x08 | 0x04 | 0x40 | 0x02, 'z': 0x01 | 0x40 | 0x08 | 0x02 | 0x10, ' ': 0x00, '-': 0x40
}

piece_to_char = {
    0x01: 'P', 0x02: 'R', 0x03: 'N', 0x04: 'B', 0x05: 'K', 0x06: 'Q',
    0x07: 'p', 0x08: 'r', 0x09: 'n', 0x0a: 'b', 0x0b: 'k', 0x0c: 'q', 0x00: '.'
}

level_map = ("rnbqkbnr/pppppppp/q7/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/1q6/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/2q5/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/3q4/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/4q3/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/5q2/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/6q1/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/7q/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/q7/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/1q6/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/2q5/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/3q4/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/4q3/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/5q2/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/6q1/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/7q/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/q7/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/1q6/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/2q5/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/3q4/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/4q3/8/PPPPPPPP/RNBQKBNR")

book_map = ("rnbqkbnr/pppppppp/8/8/8/q7/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/1q6/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/2q5/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/3q4/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/4q3/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/5q2/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/6q1/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/7q/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/7q/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/6q1/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/5q2/8/PPPPPPPP/RNBQKBNR")

shutdown_map = ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQQBNR", "8/8/8/8/8/8/8/3QQ3", "3QQ3/8/8/8/8/8/8/8")

mode_map = {"rnbqkbnr/pppppppp/8/Q7/8/8/PPPPPPPP/RNBQKBNR": Mode.GAME,
            "rnbqkbnr/pppppppp/8/1Q6/8/8/PPPPPPPP/RNBQKBNR": Mode.ANALYSIS,
            "rnbqkbnr/pppppppp/8/2Q5/8/8/PPPPPPPP/RNBQKBNR": Mode.PLAY_WHITE,
            "rnbqkbnr/pppppppp/8/3Q4/8/8/PPPPPPPP/RNBQKBNR": Mode.KIBITZ,
            "rnbqkbnr/pppppppp/8/4Q3/8/8/PPPPPPPP/RNBQKBNR": Mode.OBSERVE,
            "rnbq1bnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": Mode.PLAY_BLACK,  # Player plays black
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQ1BNR": Mode.PLAY_WHITE,  # Player plays white
            "RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbq1bnr": Mode.PLAY_BLACK,  # Player plays black (reversed board)
            "RNBQ1BNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr": Mode.PLAY_WHITE}  # Player plays white (reversed board)

time_control_map = OrderedDict([
("rnbqkbnr/pppppppp/Q7/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=1)),
("rnbqkbnr/pppppppp/1Q6/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=3)),
("rnbqkbnr/pppppppp/2Q5/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=5)),
("rnbqkbnr/pppppppp/3Q4/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=10)),
("rnbqkbnr/pppppppp/4Q3/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=15)),
("rnbqkbnr/pppppppp/5Q2/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=30)),
("rnbqkbnr/pppppppp/6Q1/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=60)),
("rnbqkbnr/pppppppp/7Q/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=120)),
("rnbqkbnr/pppppppp/8/8/Q7/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=1)),
("rnbqkbnr/pppppppp/8/8/1Q6/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=3)),
("rnbqkbnr/pppppppp/8/8/2Q5/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=5)),
("rnbqkbnr/pppppppp/8/8/3Q4/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=10)),
("rnbqkbnr/pppppppp/8/8/4Q3/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=15)),
("rnbqkbnr/pppppppp/8/8/5Q2/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=30)),
("rnbqkbnr/pppppppp/8/8/6Q1/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=60)),
("rnbqkbnr/pppppppp/8/8/7Q/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=90)),
("rnbqkbnr/pppppppp/8/8/8/Q7/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=3, fischer_increment=2)),
("rnbqkbnr/pppppppp/8/8/8/1Q6/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=4, fischer_increment=2)),
("rnbqkbnr/pppppppp/8/8/8/2Q5/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=5, fischer_increment=3)),
("rnbqkbnr/pppppppp/8/8/8/3Q4/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=5, fischer_increment=5)),
("rnbqkbnr/pppppppp/8/8/8/5Q2/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=25, fischer_increment=5)),
("rnbqkbnr/pppppppp/8/8/8/4Q3/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=15, fischer_increment=5)),
("rnbqkbnr/pppppppp/8/8/8/6Q1/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=90, fischer_increment=30))
])

dgt_xl_time_control_list = ["mov  1", "mov  3", "mov  5", "mov 10", "mov 15", "mov 30", "mov 60", "mov120",
                            "bl   1", "bl   3", "bl   5", "bl  10", "bl  15", "bl  30", "bl  60", "bl  90",
                            "f 3  2", "f 4  2", "f 5  3", "f 5  5", "f25  5", "f15  5", "f90 30"]

class DGTBoard(Observable, Display, threading.Thread):

    def __init__(self, device, enable_board_leds=False, enable_dgt_3000=False, enable_dgt_clock_beep=True):
        super(DGTBoard, self).__init__()
        self.flip_board = False
        self.flip_clock = None

        self.setup_to_move = chess.WHITE
        self.setup_reverse_orientation = False
        self.dgt_fen = None
        # self.dgt_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        self.enable_board_leds = enable_board_leds
        self.write_queue = queue.Queue()
        self.clock_lock = asyncio.Lock()
        self.enable_dgt_3000 = enable_dgt_3000
        self.enable_dgt_clock_beep = enable_dgt_clock_beep
        self.bit_board = chess.Board()
        self.dgt_clock_menu = Menu.GAME_MENU
        self.last_move = None
        self.last_fen = None
        self.ponder_move = None
        self.score = None
        self.mate = None
        # Open the serial port
        attempts = 0
        while attempts < 10:
            try:
                self.serial = pyserial.Serial(device, stopbits=pyserial.STOPBITS_ONE)
                break
            except pyserial.SerialException as e:
                logging.warning(e)
                time.sleep(2)

        # Set the board update mode
        self.serial.write(bytearray([Commands.DGT_SEND_UPDATE_NICE.value]))

        # Detect DGT XL clock
        self.serial.write(bytearray([0x2b, 0x04, 0x03, 0x0b, 1, 0x00]))
        tries = 0
        self.clock_found = False
        while not self.clock_found and tries < 20:
            time.sleep(0.3)
            self.clock_found = self.serial.inWaiting()
            tries += 1
        logging.debug('DGT clock found' if self.clock_found else 'DGT clock NOT found')

        self.display_on_dgt_xl('pic'+version)
        self.display_on_dgt_3000('pic'+version)
        # Get clock version
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x03, Clock.DGT_CMD_CLOCK_START_MESSAGE,
                        Clock.DGT_CMD_CLOCK_VERSION, Clock.DGT_CMD_CLOCK_END_MESSAGE])

        # Get board version
        self.version = 0.0
        self.write([Commands.DGT_SEND_VERSION])

        # Update the board
        self.write([Commands.DGT_SEND_BRD])
        #self._dgt_xl_stress_test()

    def _dgt_xl_stress_test(self):
        # Clock stress test
        for i in range(0, 9):
            self.display_on_dgt_xl(''+str(i)+'ooooo')
            self.display_on_dgt_xl('o'+str(i)+'oooo')
            self.display_on_dgt_xl('oo'+str(i)+'ooo')
            self.display_on_dgt_xl('ooo'+str(i)+'oo')
            self.display_on_dgt_xl('oooo'+str(i)+'o')
            self.display_on_dgt_xl('ooooo'+str(i)+'')
            self.display_on_dgt_xl('oooo'+str(i)+'o')
            self.display_on_dgt_xl('ooo'+str(i)+'oo')
            self.display_on_dgt_xl('oo'+str(i)+'ooo')
            self.display_on_dgt_xl('o'+str(i)+'oooo')

    def write(self, message):
        self.write_queue.put(message)

    def send_command(self, message):
        mes = message[3] if message[0] == Commands.DGT_CLOCK_MESSAGE else message[0]
        logging.debug('->DGT [%s]', mes)
        array = []
        for v in message:
            if type(v) is int: array.append(v)
            elif isinstance(v, enum.Enum): array.append(v.value)
            elif type(v) is str:
                for c in v:
                    array.append(char_to_DGTXL[c])
            else:
                logging.error('Type not supported : [%s]', type(v))
        try:
            self.serial.write(bytearray(array))
        except ValueError:
            logging.error('Invalid bytes sent {0}'.format(array))
        if message[0] == Commands.DGT_CLOCK_MESSAGE:
            # print(message)
            time.sleep(0.05 if self.enable_dgt_3000 else 0.5)  # Let a bit time for the message to be displayed on the clock
            self.clock_lock.acquire()

    def complete_dgt_fen(self, fen):
        # fen = str(self.setup_chessboard.fen())
        can_castle = False
        castling_fen = ''
        bit_board = chess.Board(fen)

        if bit_board.piece_at(chess.E1) == chess.Piece.from_symbol("K") and bit_board.piece_at(chess.H1) == chess.Piece.from_symbol("R"):
            can_castle = True
            castling_fen += 'K'

        if bit_board.piece_at(chess.E1) == chess.Piece.from_symbol("K") and bit_board.piece_at(chess.A1) == chess.Piece.from_symbol("R"):
            can_castle = True
            castling_fen += 'Q'

        if bit_board.piece_at(chess.E8) == chess.Piece.from_symbol("k") and bit_board.piece_at(chess.H8) == chess.Piece.from_symbol("r"):
            can_castle = True
            castling_fen += 'k'

        if bit_board.piece_at(chess.E8) == chess.Piece.from_symbol("k") and bit_board.piece_at(chess.A8) == chess.Piece.from_symbol("r"):
            can_castle = True
            castling_fen += 'q'

        if not can_castle:
            castling_fen = '-'

        # TODO: Support fen positions where castling is not possible even if king and rook are on right squares
        return fen.replace("KQkq", castling_fen)

    def read_message(self):
        header = unpack('>BBB', (self.serial.read(3)))
        message_id = header[0]
        message_length = (header[1] << 7) + header[2] - 3

        try:
            logging.debug("<-DGT [%s], length:%i", Messages(message_id), message_length)
        except ValueError:
            logging.warning("Unknown message value %i", message_id)
        if message_length:
            message = unpack('>'+str(message_length)+'B', (self.serial.read(message_length)))
            # print(message)
            # print(message[0] & 127)

            for case in switch(message_id):
                if case(Messages.DGT_MSG_VERSION):  # Get the DGT board version
                    self.version = float(str(message[0])+'.'+str(message[1]))
                    logging.debug("DGT board version %0.2f", self.version)
                    break

                # if case():
                #     logging.info("Got clock version number")
                #     break
                if case(Messages.DGT_MSG_BWTIME):
                    # print ("GOT BW_TIME")
                    # print ("Clock m
                    # sg")
                    # print (message)
                    if message[0] == message[1] == message[2] == message[3] == message[4] == message[5] == 0:  # Clock Times message
                        # print ("tumbler message: {0}".format(message))
                        clock_status = message[6]
                        old_flip_clock = self.flip_clock
                        self.flip_clock = bool(clock_status & 0x02)  # tumbler position high on right player
                        # if old_flip_clock is not None and self.flip_clock != old_flip_clock:
                        #     logging.debug("Tumbler pressed")
                        #     # self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
                        #     #            0, 0, 0, 0, 0, 0,
                        #     #            0x04 | 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])
                        #     self.display_on_dgt_3000('menu')
                    # if message[0] == 10 and message[1] == 16 and message[3] == 10 and not message[5] and not message[6]:

                    if 5 <= message[4] <= 6 and message[5] == 49:
                        logging.info("Button 0 pressed")
                        # print(self.dgt_clock_menu)

                        if self.dgt_clock_menu == Menu.GAME_MENU and self.last_move:
                            self.display_on_dgt_xl(' ' + self.last_move.uci(), True)
                            # self.display_on_dgt_3000('mov ' + mo, True)
                            self.bit_board.set_fen(self.last_fen)
                            # logging.info("Move is {0}".format(self.bit_board.san(message.move)))
                            self.display_on_dgt_3000(self.bit_board.san(self.last_move), False)

                        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
                            self.setup_to_move = chess.WHITE if self.setup_to_move == chess.BLACK else chess.BLACK
                            to_move_string = "white" if self.setup_to_move == chess.WHITE else "black"
                            self.display_on_dgt_clock(to_move_string, beep=True)

                    if 33 <= message[4] <= 34 and message[5] == 52:
                        logging.info("Button 1 pressed")
                        if self.dgt_clock_menu == Menu.GAME_MENU and self.ponder_move:
                            self.display_on_dgt_clock(self.ponder_move.uci(), beep=True)

                        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
                            self.setup_reverse_orientation = False if self.setup_reverse_orientation else True
                            orientation = "reversed" if self.setup_reverse_orientation else "normal"
                            self.display_on_dgt_clock(orientation, beep=True)

                    if 17 <= message[4] <= 18 and message[5] == 51:
                        logging.info("Button 2 pressed")
                        if self.dgt_clock_menu == Menu.GAME_MENU:
                            self.fire(Event.CHANGE_MODE)

                        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
                            self.display_on_dgt_clock("scan", beep=True)
                            to_move = 'w' if self.setup_to_move == chess.WHITE else 'b'
                            fen = self.dgt_fen
                            fen += " {0} KQkq - 0 1".format(to_move)
                            fen = self.complete_dgt_fen(fen)
                            self.fire(Event.SETUP_POSITION, fen=fen)

                    if 9 <= message[4] <= 10 and message[5] == 50:
                        logging.info("Button 3 pressed")
                        if self.dgt_clock_menu == Menu.GAME_MENU:
                            if self.mate is None:
                                sc = 's none' if self.score is None else 's' + str(self.score).rjust(4)
                            else:
                                sc = 'm ' + str(self.mate)
                            self.display_on_dgt_clock(sc, True)

                        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
                            self.display_on_dgt_clock('pic'+version)

                    if 65 <= message[4] <= 66 and message[5] == 53:
                        logging.info("Button 4 pressed")

                        # self.dgt_clock_menu = Menu.self.dgt_clock_menu.value+1
                        # print(self.dgt_clock_menu)
                        # print(self.dgt_clock_menu.value)
                        try:
                            self.dgt_clock_menu = Menu(self.dgt_clock_menu.value+1)
                        except ValueError:
                            self.dgt_clock_menu = Menu(1)

                        if self.dgt_clock_menu == Menu.GAME_MENU:
                            msg = 'game'
                        elif self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
                            msg = 'position'
                        elif self.dgt_clock_menu == Menu.ENGINE_MENU:
                            msg = 'engine'
                        elif self.dgt_clock_menu == Menu.SETTINGS_MENU:
                            msg = 'system'

                        self.display_on_dgt_clock(msg, beep=True)

                    if ((message[0] & 0x0f) == 0x0a) or ((message[3] & 0x0f) == 0x0a):  # Clock ack message

                        #Construct the ack message
                        ack0 = ((message[1]) & 0x7f) | ((message[3] << 3) & 0x80)
                        ack1 = ((message[2]) & 0x7f) | ((message[3] << 2) & 0x80)
                        # print ("Ack1: {0}".format(ack1))
                        ack2 = ((message[4]) & 0x7f) | ((message[0] << 3) & 0x80)
                        if ack1 == 0x09:
                            main_version = ack2 >> 4
                            if main_version == 2:
                                self.enable_dgt_3000 = True
                                # self.display_on_dgt_3000('pico '+version)
                                # time.sleep(0.5)
                                # # Some bug with certain DGT 3000 clocks?!
                                # self.display_on_dgt_3000('pico '+version)

                        ack3 = ((message[5]) & 0x7f) | ((message[0] << 2) & 0x80)
                        if ack0 != 0x10: logging.warning("Clock ACK error %s", (ack0, ack1, ack2, ack3))
                        else:
                            logging.debug("Clock ACK %s", (ack0, ack1, ack2, ack3))
                            if self.clock_lock.locked():
                                self.clock_lock.release()
                            return None

                    break
                if case(Messages.DGT_MSG_BOARD_DUMP):
                    board = ''
                    for c in message:
                        board += piece_to_char[c]
                    logging.debug('\n' + '\n'.join(board[0+i:8+i] for i in range(0, len(board), 8)))  # Show debug board
                    #Create fen from board
                    fen = ''
                    empty = 0
                    for sq in range(0, 64):
                        if message[sq] != 0:
                            if empty > 0:
                                fen += str(empty)
                                empty = 0
                            fen += piece_to_char[message[sq]]
                        else:
                            empty += 1
                        if (sq + 1) % 8 == 0:
                            if empty > 0:
                                fen += str(empty)
                                empty = 0
                            if sq < 63:
                                fen += "/"
                            empty = 0
                    if self.flip_board:  # Flip the board if needed
                        fen = fen[::-1]
                    if fen == "RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr":  # Check if we have to flip the board
                        logging.debug('Flipping the board')
                        #Flip the board
                        self.flip_board = not self.flip_board
                        fen = fen[::-1]
                    logging.debug(fen)
                    self.dgt_fen = fen

                    #Fire the appropriate event
                    if fen in level_map:  # User sets level
                        level = level_map.index(fen)
                        self.fire(Event.LEVEL, level=level)
                        Display.show(Event.LEVEL, level=level)
                        self.display_on_dgt_xl('lvl ' + str(level), self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000('level '+ str(level), self.enable_dgt_clock_beep)
                    elif fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR":  # New game
                        logging.debug("New game")
                        self.fire(Event.NEW_GAME)
                    elif fen in book_map:  # Choose opening book
                        book_index = book_map.index(fen)
                        logging.debug("Opening book [%s]", get_opening_books()[book_index])
                        self.fire(Event.OPENING_BOOK, book_index=book_index)
                        Display.show(Event.OPENING_BOOK, book=get_opening_books()[book_index])

                        self.display_on_dgt_xl(get_opening_books()[book_index][0], self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000(get_opening_books()[book_index][0], self.enable_dgt_clock_beep)
                    elif fen in mode_map:  # Set interaction mode
                        logging.debug("Interaction mode [%s]", mode_map[fen])
                        self.fire(Event.SET_MODE, mode=mode_map[fen])
                    elif fen in time_control_map:
                        logging.debug("Setting time control %s", time_control_map[fen].mode)
                        self.fire(Event.SET_TIME_CONTROL, time_control=time_control_map[fen])
                        Display.show(Event.SET_TIME_CONTROL, time_control_string=dgt_xl_time_control_list[list(time_control_map.keys()).index(fen)])

                        self.display_on_dgt_xl(dgt_xl_time_control_list[list(time_control_map.keys()).index(fen)], self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000(dgt_xl_time_control_list[list(time_control_map.keys()).index(fen)], self.enable_dgt_clock_beep)
                    elif fen in shutdown_map:
                        self.fire(Event.SHUTDOWN)
                        self.display_on_dgt_xl('powoff', self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000('poweroff', self.enable_dgt_clock_beep)
                    else:
                        logging.debug("Fen")
                        self.fire(Event.FEN, fen=fen)
                    break
                if case(Messages.DGT_MSG_FIELD_UPDATE):
                    self.write([Commands.DGT_SEND_BRD])  # Ask for the board when a piece moved
                    break
                if case():  # Default
                    logging.warning("DGT message not handled : [%s]", Messages(message_id))

            return message_id

    def display_on_dgt_xl(self, text, beep=False):
        if self.clock_found and not self.enable_dgt_3000:
            while len(text) < 6: text += ' '
            if len(text) > 6: logging.warning('DGT XL clock message too long [%s]', text)
            self.write([Commands.DGT_CLOCK_MESSAGE, 0x0b, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_DISPLAY,
                        text[2], text[1], text[0], text[5], text[4], text[3], 0x00, 0x03 if beep else 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def display_on_dgt_3000(self, text, beep=False, force=False):
        if force or self.enable_dgt_3000:
            while len(text) < 8: text += ' '
            if len(text) > 8: logging.warning('DGT 3000 clock message too long [%s]', text)
            text = bytes(text, 'utf-8')
            self.write([Commands.DGT_CLOCK_MESSAGE, 0x0c, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_ASCII,
                        text[0], text[1], text[2], text[3], text[4], text[5], text[6], text[7], 0x03 if beep else 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def display_on_dgt_clock(self, text, beep=False, dgt_3000_text=None):
        if self.enable_dgt_3000:
            if dgt_3000_text:
                text = dgt_3000_text
            self.display_on_dgt_3000(text, beep=beep)
        else:
            self.display_on_dgt_xl(text, beep=beep)

    def light_squares_revelation_board(self, squares):
        if self.enable_board_leds:
            for sq in squares:
                dgt_square = (8 - int(sq[1])) * 8 + ord(sq[0]) - ord('a')
                logging.debug("REV2 light on square %s(%i)", sq, dgt_square)
                self.write([Commands.DGT_SET_LEDS, 0x04, 0x01, dgt_square, dgt_square])

    def clear_light_revelation_board(self):
        if self.enable_board_leds:
            self.write([Commands.DGT_SET_LEDS, 0x04, 0x00, 0, 63])

    def run(self):
        while True:
            # Check if we have a message from the board
            if self.serial.inWaiting():
                self.read_message()
            else:
                time.sleep(0.1)  # Sleep a little bit to avoid CPU usage
            if not self.clock_lock.locked():
                # Check if we have something to send
                try:
                    command = self.write_queue.get_nowait()
                    self.send_command(command)
                except queue.Empty:
                    pass
            # Check if we have something to display
            try:
                message = self.message_queue.get_nowait()
                for case in switch(message):
                    if case(Message.COMPUTER_MOVE):
                        uci_move = message.move.uci()
                        self.last_move = message.move
                        self.ponder_move = chess.Move.null() if message.ponder is None else message.ponder
                        self.last_fen = message.fen
                        logging.info("DGT SEND BEST MOVE:"+uci_move)
                        # Stop the clock before displaying a move
                        self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
                                   0, 0, 0, 0, 0, 0,
                                   0x04 | 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])
                        # Display the move
                        self.display_on_dgt_xl(' ' + uci_move, self.enable_dgt_clock_beep)
                        # self.display_on_dgt_3000('mov ' + mo, self.enable_dgt_clock_beep)
                        self.bit_board.set_fen(message.fen)
                        # logging.info("Move is {0}".format(self.bit_board.san(message.move)))
                        self.display_on_dgt_3000(self.bit_board.san(message.move), self.enable_dgt_clock_beep)
                        self.light_squares_revelation_board((uci_move[0:2], uci_move[2:4]))
                        break
                    if case(Message.START_NEW_GAME):
                        self.display_on_dgt_xl('newgam', self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000('new game', self.enable_dgt_clock_beep)
                        self.clear_light_revelation_board()
                        self.last_move = None
                        self.ponder_move = None
                        self.score = None
                        self.mate = None
                        break
                    if case(Message.COMPUTER_MOVE_DONE_ON_BOARD):
                        self.display_on_dgt_xl('ok', self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000('ok', self.enable_dgt_clock_beep)
                        self.clear_light_revelation_board()
                        break
                    if case(Message.REVIEW_MODE_MOVE):
                        uci_move = message.move.uci()
                        self.last_move = message.move
                        self.last_fen = message.fen

                        # Dont beep when reviewing a game
                        self.display_on_dgt_xl(' ' + uci_move, False)
                        self.bit_board.set_fen(message.fen)
                        self.display_on_dgt_3000(self.bit_board.san(message.move), False)
                        break
                    if case(Message.USER_TAKE_BACK):
                        self.display_on_dgt_xl('takbak', self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000('takeback', self.enable_dgt_clock_beep)
                        break
                    if case(Message.RUN_CLOCK):
                        tc = message.time_control
                        w_hms = hours_minutes_seconds(int(tc.clock_time[chess.WHITE]))
                        b_hms = hours_minutes_seconds(int(tc.clock_time[chess.BLACK]))
                        side = 0x01 if (message.turn == chess.WHITE) != self.flip_board else 0x02
                        if tc.mode == ClockMode.FIXED_TIME:
                            side = 0x02
                            b_hms = hours_minutes_seconds(tc.seconds_per_move)
                        if self.flip_board:
                            w_hms, b_hms = b_hms, w_hms
                        self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
                                   w_hms[0], w_hms[1], w_hms[2], b_hms[0], b_hms[1], b_hms[2],
                                   side, Clock.DGT_CMD_CLOCK_END_MESSAGE])
                        self.write([Commands.DGT_CLOCK_MESSAGE, 0x03, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_END, Clock.DGT_CMD_CLOCK_END_MESSAGE])
                        break
                    if case(Message.GAME_ENDS):
                        # time.sleep(3)  # Let the move displayed on clock
                        self.display_on_dgt_clock(message.result.value, beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.INTERACTION_MODE):
                        self.display_on_dgt_clock(message.mode.value, beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.SCORE):
                        self.score = message.score
                        self.mate = message.mate
                        break
                    if case(Message.BOOK_MOVE):
                        self.display_on_dgt_clock('book', beep=False)
                        break
                    if case(Message.SEARCH_STARTED):
                        #print('Search Started!')
                        break
                    if case(Message.USER_MOVE):
                        #print('UserMove')
                        break
                    if case():  # Default
                        pass
            except queue.Empty:
                pass
