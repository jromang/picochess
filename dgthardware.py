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
from subprocess import Popen

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
    # Clock commands, returns ACK message if mode is in UPDATE or UPDATE_NICE
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
    # Piece codes for chess pieces:
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
    PIECE1 = 0x0d # Magic piece: Draw
    PIECE2 = 0x0e # Magic piece: White win
    PIECE3 = 0x0f # Magic piece: Black win


class Messages(enum.IntEnum):
    """
    DESCRIPTION OF THE MESSAGES FROM BOARD TO PC
    """
    MESSAGE_BIT = 0x80 # The Message ID is the logical OR of MESSAGE_BIT and ID code
    # ID codes
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
    # DGT_MSG_BOARD_DUMP is the message that follows on a DGT_SEND_BOARD command
    DGT_MSG_BOARD_DUMP = (MESSAGE_BIT | DGT_BOARD_DUMP)
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


class DGTHardware(Observable, Display, threading.Thread):

    def __init__(self, device, enable_dgt_3000):
        super(DGTHardware, self).__init__()

        self.write_queue = queue.Queue()
        self.clock_lock = asyncio.Lock()
        self.enable_dgt_3000 = enable_dgt_3000
        self.displayed_text = None # The current clock display or None if in ClockNRun mode or unknown text

        # Open the serial port
        try:
            self.serial = pyserial.Serial(device, stopbits=pyserial.STOPBITS_ONE,
                                          parity=pyserial.PARITY_NONE,
                                          bytesize=pyserial.EIGHTBITS,
                                          timeout=2
                                          )
        except pyserial.SerialException as e:
            logging.warning(e)

        # Set the board update mode
        self.serial.write(bytearray([Commands.DGT_SEND_UPDATE_NICE.value]))

        # self.clock_found = True

        # Detect DGT XL clock
        self.clock_found = False
        self.serial.write(bytearray([0x2b, 0x04, 0x03, 0x0b, 1, 0x00]))
        time.sleep(1)
        # logging.debug('DGT clock found' if self.clock_found else 'DGT clock NOT found')

        # Get clock version
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x03, Clock.DGT_CMD_CLOCK_START_MESSAGE,
                        Clock.DGT_CMD_CLOCK_VERSION, Clock.DGT_CMD_CLOCK_END_MESSAGE])
        self._display_on_dgt_xl('pic'+version)

        # Get board version
        self.version = 0.0
        self.write([Commands.DGT_SEND_VERSION])

        # Update the board
        self.write([Commands.DGT_SEND_BRD])

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
            # Let a bit time for the message to be displayed on the clock
            time.sleep(0.05 if self.enable_dgt_3000 else 0.5)
            self.clock_lock.acquire()

    def process_message(self, message_id, message):
        for case in switch(message_id):
            if case(Messages.DGT_MSG_VERSION):  # Get the DGT board version
                self.version = float(str(message[0])+'.'+str(message[1]))
                logging.debug("DGT board version %0.2f", self.version)
                break
            # if case():
            #     logging.info("Got clock version number")
            #     break
            if case(Messages.DGT_MSG_BWTIME):
                # if message[0] == message[1] == message[2] == message[3] == message[4] == message[5] == 0:  # Clock Times message
                    # print ("tumbler message: {0}".format(message))
                    # clock_status = message[6]
                    # old_flip_clock = self.flip_clock
                    # self.flip_clock = bool(clock_status & 0x02)  # tumbler position high on right player
                    # if old_flip_clock is not None and self.flip_clock != old_flip_clock:
                    #     logging.debug("Tumbler pressed")
                    #     # self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
                    #     #            0, 0, 0, 0, 0, 0,
                    #     #            0x04 | 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])
                    #     self.display_on_dgt_3000('menu')

                # if message[0] == 10 and message[1] == 16 and message[3] == 10 and not message[5] and not message[6]:

                if 5 <= message[4] <= 6 and message[5] == 49:
                    logging.info("Button 0 pressed")
                    self.fire(Event.DGT_BUTTON, button=0)
                if 33 <= message[4] <= 34 and message[5] == 52:
                    logging.info("Button 1 pressed")
                    self.fire(Event.DGT_BUTTON, button=1)
                if 17 <= message[4] <= 18 and message[5] == 51:
                    logging.info("Button 2 pressed")
                    self.fire(Event.DGT_BUTTON, button=2)
                if 9 <= message[4] <= 10 and message[5] == 50:
                    logging.info("Button 3 pressed")
                    self.fire(Event.DGT_BUTTON, button=3)
                if 65 <= message[4] <= 66 and message[5] == 53:
                    logging.info("Button 4 pressed")
                    self.fire(Event.DGT_BUTTON, button=4)
                if ((message[0] & 0x0f) == 0x0a) or ((message[3] & 0x0f) == 0x0a):  # Clock ack message
                    # Construct the ack message
                    ack0 = ((message[1]) & 0x7f) | ((message[3] << 3) & 0x80)
                    ack1 = ((message[2]) & 0x7f) | ((message[3] << 2) & 0x80)
                    # print ("Ack1: {0}".format(ack1))
                    ack2 = ((message[4]) & 0x7f) | ((message[0] << 3) & 0x80)
                    if ack1 == 0x09:
                        if not self.clock_found:
                            self.clock_found = True
                        main_version = ack2 >> 4
                        sub_version = ack2 & 0x0f
                        logging.debug("Clock version %s", (main_version, sub_version))
                        if main_version == 2:
                            self.enable_dgt_3000 = True
                        self.display_text_on_clock('pico '+version, 'pic'+version, beep=True)

                    ack3 = ((message[5]) & 0x7f) | ((message[0] << 2) & 0x80)
                    if ack0 != 0x10:
                        logging.warning("Clock ACK error %s", (ack0, ack1, ack2, ack3))
                    else:
                        logging.debug("Clock ACK %s", (ack0, ack1, ack2, ack3))

                        if self.clock_lock.locked():
                            self.clock_lock.release()
                        return None
                else:
                    self.displayed_text = None  # reset the saved text to unknown
                break
            if case(Messages.DGT_MSG_BOARD_DUMP):
                board = ''
                for c in message:
                    board += piece_to_char[c]
                logging.debug('\n' + '\n'.join(board[0+i:8+i] for i in range(0, len(board), 8)))  # Show debug board
                # Create fen from board
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

                # Now we have a FEN -> fire a fen-event with it
                # Attention: This fen is NOT flipped!!
                logging.debug("Fen")
                self.fire(Event.DGT_FEN, fen=fen)
                break
            if case(Messages.DGT_MSG_FIELD_UPDATE):
                self.write([Commands.DGT_SEND_BRD])  # Ask for the board when a piece moved
                break
            if case():  # Default
                logging.warning("DGT message not handled : [%s]", Messages(message_id))

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
            self.process_message(message_id, message)
            return message_id

    def _display_on_dgt_xl(self, text, beep=False):
        if self.clock_found and not self.enable_dgt_3000:
            while len(text) < 6:
                text += ' '
            if len(text) > 6:
                logging.warning('DGT XL clock message too long [%s]', text)
            logging.debug(text)
            self.write([Commands.DGT_CLOCK_MESSAGE, 0x0b, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_DISPLAY,
                        text[2], text[1], text[0], text[5], text[4], text[3], 0x00, 0x03 if beep else 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def _display_on_dgt_3000(self, text, beep=False):
        if self.enable_dgt_3000:
            while len(text) < 8:
                text += ' '
            if len(text) > 8:
                logging.warning('DGT 3000 clock message too long [%s]', text)
            logging.debug(text)
            text = bytes(text, 'utf-8')
            self.write([Commands.DGT_CLOCK_MESSAGE, 0x0c, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_ASCII,
                        text[0], text[1], text[2], text[3], text[4], text[5], text[6], text[7], 0x03 if beep else 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def display_text_on_clock(self, text, dgt_xl_text=None, beep=False, force=True):
        if self.enable_dgt_3000:
            if force or self.displayed_text != text:
                self._display_on_dgt_3000(text, beep)
        else:
            if dgt_xl_text:
                text = dgt_xl_text
            if force or self.displayed_text != text:
                self._display_on_dgt_xl(text, beep)
        self.displayed_text = text

    def display_move_on_clock(self, move, fen, beep=False, force=True):
        if self.enable_dgt_3000:
            bit_board = chess.Board(fen)
            text = bit_board.san(move)
            if force or self.displayed_text != text:
                self._display_on_dgt_3000(text, beep)
        else:
            text = ' ' + move.uci()
            if force or self.displayed_text != text:
                self._display_on_dgt_xl(text, beep)
        self.displayed_text = text

    def light_squares_revelation_board(self, squares, enable_board_leds):
        if enable_board_leds:
            for sq in squares:
                dgt_square = (8 - int(sq[1])) * 8 + ord(sq[0]) - ord('a')
                logging.debug("REV2 light on square %s(%i)", sq, dgt_square)
                self.write([Commands.DGT_SET_LEDS, 0x04, 0x01, dgt_square, dgt_square])

    def clear_light_revelation_board(self, enable_board_leds):
        if enable_board_leds:
            self.write([Commands.DGT_SET_LEDS, 0x04, 0x00, 0, 63])

    def stop_clock(self):
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
           0, 0, 0, 0, 0, 0,
           0x04 | 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def start_clock(self, time_left, time_right, side):
        l_hms = hours_minutes_seconds(time_left)
        r_hms = hours_minutes_seconds(time_right)
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
            l_hms[0], l_hms[1], l_hms[2], r_hms[0], r_hms[1], r_hms[2],
            side, Clock.DGT_CMD_CLOCK_END_MESSAGE])
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x03, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_END, Clock.DGT_CMD_CLOCK_END_MESSAGE])

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
                    if case(Dgt.DISPLAY_MOVE):
                        self.display_move_on_clock(message.move, message.fen, message.beep)
                        break
                    if case(Dgt.DISPLAY_TEXT):
                        self.display_text_on_clock(message.text, message.xl, message.beep)
                        break
                    if case(Dgt.LIGHT_CLEAR):
                        self.clear_light_revelation_board(message.enable_board_leds)
                        break
                    if case(Dgt.LIGHT_SQUARES):
                        self.light_squares_revelation_board(message.squares, message.enable_board_leds)
                        break
                    if case(Dgt.CLOCK_STOP):
                        self.stop_clock()
                        break
                    if case(Dgt.CLOCK_START):
                        self.start_clock(message.time_left, message.time_right, message.side)
                        break
                    if case():  # Default
                        pass
            except queue.Empty:
                pass