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
import ctypes
import serial as pyserial

from timecontrol import *
from struct import unpack
from utilities import *

try:
    import enum
except ImportError:  # Python 3.3 support
    import enum34 as enum

piece_to_char = {
    0x01: 'P', 0x02: 'R', 0x03: 'N', 0x04: 'B', 0x05: 'K', 0x06: 'Q',
    0x07: 'p', 0x08: 'r', 0x09: 'n', 0x0a: 'b', 0x0b: 'k', 0x0c: 'q', 0x00: '.'
}


class DGTi2c(Display):
    def __init__(self, device):
        super(DGTi2c, self).__init__()
        self.device = device

        # Open the serial port
        try:
            self.serial = pyserial.Serial(device, stopbits=pyserial.STOPBITS_ONE,
                                          parity=pyserial.PARITY_NONE,
                                          bytesize=pyserial.EIGHTBITS,
                                          timeout=2
                                          )
        except pyserial.SerialException as e:
            logging.warning(e)
            return

        # load the dgt3000 so file
        self.lib = ctypes.cdll.LoadLibrary("/home/pi/20151118/dgt3000.so")

    def write_to_board(self, message):
        logging.debug('->DGT [%s], length:%i', message[0], len(message))
        array = []
        for v in message:
            if type(v) is int:
                array.append(v)
            elif isinstance(v, enum.Enum):
                array.append(v.value)
            else:
                logging.error('Type not supported : [%s]', type(v))
        try:
            self.serial.write(bytearray(array))
        except ValueError:
            logging.error('Invalid bytes sent {0}'.format(message))

    def write_text_to_clock(self, message, beep):
        self.lib.dgt3000Display(message,  0x03 if beep else 0x01, 0, 0)

    def write_stop_to_clock(self):
        self.lib.dgt3000SetNRun(0, 0, 0, 0, 0, 0, 0, 0)

    def write_start_to_clock(self, l_hms, r_hms, side):
        if side == 0x01:
            lr = 1
            rr = 0
        else:
            lr = 0
            rr = 1
        self.lib.dgt3000SetNRun(lr, l_hms[0], l_hms[1], l_hms[2], rr, r_hms[0], r_hms[1], r_hms[2])

    def process_board_message(self, message_id, message):
        for case in switch(message_id):
            if case(DgtMsg.DGT_MSG_VERSION):  # Get the DGT board version
                board_version = float(str(message[0]) + '.' + str(message[1]))
                logging.debug("DGT board version %0.2f", board_version)
                break
            if case(DgtMsg.DGT_MSG_BOARD_DUMP):
                board = ''
                for c in message:
                    board += piece_to_char[c]
                logging.debug('\n' + '\n'.join(board[0 + i:8 + i] for i in range(0, len(board), 8)))  # Show debug board
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

                # Attention: This fen is NOT flipped!!
                logging.debug("Raw-Fen: " + fen)
                Display.show(Message.DGT_FEN, fen=fen)
                break
            if case(DgtMsg.DGT_MSG_FIELD_UPDATE):
                self.write_to_board([DgtCmd.DGT_SEND_BRD])  # Ask for the board when a piece moved
                break
            if case():  # Default
                logging.warning("DGT message not handled : [%s]", DgtMsg(message_id))

    def read_board_message(self, head=None):
        header_len = 3
        if head:
            header = head + self.serial.read(header_len-1)
        else:
            header = self.serial.read(header_len)

        pattern = '>'+'B'*header_len
        header = unpack(pattern, header)

        # header = unpack('>BBB', (self.serial.read(3)))
        message_id = header[0]
        message_length = (header[1] << 7) + header[2] - 3

        try:
            logging.debug("<-DGT [%s], length:%i", DgtMsg(message_id), message_length)
        except ValueError:
            logging.warning("Unknown message value %i", message_id)
        if message_length:
            message = unpack('>' + str(message_length) + 'B', (self.serial.read(message_length)))
            self.process_board_message(message_id, message)
            return message_id

    def startup_board(self):
        # Set the board update mode
        self.write_to_board([DgtCmd.DGT_SEND_UPDATE_NICE])
        # Get board version
        self.write_to_board([DgtCmd.DGT_SEND_VERSION])
        # Update the board
        self.write_to_board([DgtCmd.DGT_SEND_BRD])

    def startup_clock(self):
        self.lib.dgt3000Init()
        self.lib.dgt3000Configure()

    def process_incoming_board_forever(self):
        while True:
            try:
                c = self.serial.read(1)
                if c:
                    self.read_board_message(head=c)
            except pyserial.SerialException as e:
                pass

    def process_incoming_clock_forever(self):
        but = ctypes.c_byte(0)
        buttime = ctypes.c_byte(0)
        while True:
            if self.lib.dgt3000GetButton(ctypes.pointer(but), ctypes.pointer(buttime)) == 1:
                ack3 = but.value
                if ack3 == 0x01:
                    logging.info("Button 0 pressed")
                    Display.show(Message.DGT_BUTTON, button=0)
                if ack3 == 0x02:
                    logging.info("Button 1 pressed")
                    Display.show(Message.DGT_BUTTON, button=1)
                if ack3 == 0x04:
                    logging.info("Button 2 pressed")
                    Display.show(Message.DGT_BUTTON, button=2)
                if ack3 == 0x08:
                    logging.info("Button 3 pressed")
                    Display.show(Message.DGT_BUTTON, button=3)
                if ack3 == 0x10:
                    logging.info("Button 4 pressed")
                    Display.show(Message.DGT_BUTTON, button=4)
                if ack3 == 0x20:
                    logging.info("Button on/off pressed")
                if ack3 == 0x40:
                    logging.info("Lever pressed")
            time.sleep(0.1)

    def run(self):
        self.startup_board()
        self.startup_clock()
        incoming_board_thread = threading.Timer(0, self.process_incoming_board_forever)
        incoming_board_thread.start()

        incoming_clock_thread = threading.Timer(0, self.process_incoming_clock_forever)
        incoming_clock_thread.start()