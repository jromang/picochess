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
import serial as pyserial
import time
from threading import Timer, Lock

from struct import unpack
from utilities import *

piece_to_char = {
    0x01: 'P', 0x02: 'R', 0x03: 'N', 0x04: 'B', 0x05: 'K', 0x06: 'Q',
    0x07: 'p', 0x08: 'r', 0x09: 'n', 0x0a: 'b', 0x0b: 'k', 0x0c: 'q', 0x00: '.'
}


class DGTpiboard(Display):
    def __init__(self, device):
        super(DGTpiboard, self).__init__()
        self.device = device
        self.serial = None
        self.lock = Lock()
        self.waitchars = [b'/', b'-', b'\\', b'|']
        self.lib = None

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

        serial_error = False
        while True:
            if serial_error:
                self.setup_serial()
            try:
                self.serial.write(bytearray(array))
                break
            except ValueError:
                logging.error('Invalid bytes sent {0}'.format(message))
                break
            except pyserial.SerialException as e:
                logging.error(e)
                serial_error = True

    def process_board_message(self, message_id, message):
        for case in switch(message_id):
            if case(DgtMsg.DGT_MSG_VERSION):  # Get the DGT board version
                board_version = float(str(message[0]) + '.' + str(message[1]))
                logging.debug("DGT board version %0.2f", board_version)
                self.lock.acquire()  # These locks prob. not working - since the split of clock & board
                if self.device.find('rfc') == -1:
                    text = b'USB E-board'
                else:
                    text = b'BT E-board'
                self.lib.dgt3000Display(text, 0, 0, 0)
                time.sleep(0.5)
                self.lock.release()
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
            if case(DgtMsg.DGT_MSG_SERIALNR):
                # logging.debug(message)
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
        self.write_to_board([DgtCmd.DGT_SEND_UPDATE_NICE])  # Set the board update mode
        self.write_to_board([DgtCmd.DGT_SEND_VERSION])  # Get board version
        self.write_to_board([DgtCmd.DGT_SEND_BRD])  # Update the board

    def process_incoming_board_forever(self):
        while True:
            try:
                c = self.serial.read(1)
                if c:
                    self.read_board_message(head=c)
            except pyserial.SerialException as e:
                pass
            except TypeError:
                pass

    def setup_serial(self):
        wait_counter = 0
        while not self.serial:
            # Open the serial port
            try:
                self.serial = pyserial.Serial(self.device, stopbits=pyserial.STOPBITS_ONE,
                                              parity=pyserial.PARITY_NONE,
                                              bytesize=pyserial.EIGHTBITS,
                                              timeout=2
                                              )
            except pyserial.SerialException as e:
                logging.error(e)
                self.lock.acquire()  # These locks prob. not working - since the split of clock & board
                res = self.lib.dgt3000Display(b'no E-board' + self.waitchars[wait_counter], 0, 0, 0)
                self.lock.release()
                if res < 0:
                    logging.warning('dgt lib returned error: %i', res)
                wait_counter = (wait_counter + 1) % len(self.waitchars)
                time.sleep(0.5)

    def run(self, lib):
        self.lib = lib
        self.setup_serial()
        self.startup_board()
        incoming_board_thread = Timer(0, self.process_incoming_board_forever)
        incoming_board_thread.start()