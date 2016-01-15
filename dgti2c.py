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
from struct import unpack
from utilities import *
from threading import Timer

try:
    import enum
except ImportError:
    import enum34 as enum

char_to_DGTXL = {
    '0': 0x01 | 0x02 | 0x20 | 0x08 | 0x04 | 0x10, '1': 0x02 | 0x04, '2': 0x01 | 0x40 | 0x08 | 0x02 | 0x10,
    '3': 0x01 | 0x40 | 0x08 | 0x02 | 0x04, '4': 0x20 | 0x04 | 0x40 | 0x02, '5': 0x01 | 0x40 | 0x08 | 0x20 | 0x04,
    '6': 0x01 | 0x40 | 0x08 | 0x20 | 0x04 | 0x10, '7': 0x02 | 0x04 | 0x01,
    '8': 0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10 | 0x08, '9': 0x01 | 0x40 | 0x08 | 0x02 | 0x04 | 0x20,
    'a': 0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10, 'b': 0x20 | 0x04 | 0x40 | 0x08 | 0x10, 'c': 0x01 | 0x20 | 0x10 | 0x08,
    'd': 0x10 | 0x40 | 0x08 | 0x02 | 0x04, 'e': 0x01 | 0x40 | 0x08 | 0x20 | 0x10, 'f': 0x01 | 0x40 | 0x20 | 0x10,
    'g': 0x01 | 0x20 | 0x10 | 0x08 | 0x04, 'h': 0x20 | 0x10 | 0x04 | 0x40, 'i': 0x02 | 0x04,
    'j': 0x02 | 0x04 | 0x08 | 0x10, 'k': 0x01 | 0x20 | 0x40 | 0x04 | 0x10, 'l': 0x20 | 0x10 | 0x08,
    'm': 0x01 | 0x40 | 0x04 | 0x10, 'n': 0x40 | 0x04 | 0x10, 'o': 0x40 | 0x04 | 0x10 | 0x08,
    'p': 0x01 | 0x40 | 0x20 | 0x10 | 0x02, 'q': 0x01 | 0x40 | 0x20 | 0x04 | 0x02, 'r': 0x40 | 0x10,
    's': 0x01 | 0x40 | 0x08 | 0x20 | 0x04, 't': 0x20 | 0x10 | 0x08 | 0x40, 'u': 0x08 | 0x02 | 0x20 | 0x04 | 0x10,
    'v': 0x08 | 0x02 | 0x20, 'w': 0x40 | 0x08 | 0x20 | 0x02, 'x': 0x20 | 0x10 | 0x04 | 0x40 | 0x02,
    'y': 0x20 | 0x08 | 0x04 | 0x40 | 0x02, 'z': 0x01 | 0x40 | 0x08 | 0x02 | 0x10, ' ': 0x00, '-': 0x40
}

piece_to_char = {
    0x01: 'P', 0x02: 'R', 0x03: 'N', 0x04: 'B', 0x05: 'K', 0x06: 'Q',
    0x07: 'p', 0x08: 'r', 0x09: 'n', 0x0a: 'b', 0x0b: 'k', 0x0c: 'q', 0x00: '.'
}


class DGTi2c(Display):
    def __init__(self, device):
        super(DGTi2c, self).__init__()
        self.device = device
        self.serial = None
        self.serial_error = False
        self.waitchars = ['/', '-', '\\', '|']

    def write_to_board(self, message):
        logging.debug('->DGT [%s], length %i', message[0], len(message))
        array = []
        for v in message:
            if type(v) is int:
                array.append(v)
            elif isinstance(v, enum.Enum):
                array.append(v.value)
            elif type(v) is str:
                for c in v:
                    array.append(char_to_DGTXL[c.lower()])
            else:
                logging.error('Type not supported [%s]', type(v))

        while True:
            if self.serial_error:
                self.setup_serial()
            try:
                self.serial.write(bytearray(array))
                break
            except ValueError:
                logging.error('Invalid bytes sent {0}'.format(message))
                break
            except pyserial.SerialException as e:
                self.serial_error = True
                logging.error(e)
                self.serial.close()
                self.serial = None
            except IOError as e:
                self.serial_error = True
                logging.error(e)
                self.serial.close()
                self.serial = None

    def process_board_message(self, message_id, message):
        for case in switch(message_id):
            if case(DgtMsg.DGT_MSG_VERSION):  # Get the DGT board version
                board_version = str(message[0]) + '.' + str(message[1])
                logging.debug("DGT board version %0.2f", float(board_version))
                if self.device.find('rfc') == -1:
                    text = 'USB E-board'
                    text_xl = 'ok usb'
                    channel = 'USB'
                else:
                    text = 'BT E-board'
                    text_xl = 'ok bt'
                    channel = 'BT'
                Display.show(Message.EBOARD_VERSION, text=text, text_xl=text_xl, channel=channel)
                Display.show(Message.WAIT_STATE)
                break
            if case(DgtMsg.DGT_MSG_BWTIME):
                if ((message[0] & 0x0f) == 0x0a) or ((message[3] & 0x0f) == 0x0a):  # Clock ack message
                    # Construct the ack message
                    ack0 = ((message[1]) & 0x7f) | ((message[3] << 3) & 0x80)
                    ack1 = ((message[2]) & 0x7f) | ((message[3] << 2) & 0x80)
                    ack2 = ((message[4]) & 0x7f) | ((message[0] << 3) & 0x80)
                    ack3 = ((message[5]) & 0x7f) | ((message[0] << 2) & 0x80)
                    if ack0 != 0x10:
                        logging.warning("DGT clock ACK error %s", (ack0, ack1, ack2, ack3))
                        # self.clock_lock = False  # for issue 142
                        # return
                        break
                    else:
                        logging.debug("DGT clock ACK [%s]", DgtClk(ack1))
                    if ack1 == 0x88:
                        # this are the other (ack2-ack3) codes
                        # 6-49 34-52 18-51 10-50 66-53 | button 0-4 (single)
                        #      38-52 22-51 14-50 70-53 | button 0 + 1-4
                        #            50-51 42-50 98-53 | button 1 + 2-4
                        #                  26-50 82-53 | button 2 + 3-4
                        #                        74-53 | button 3 + 4
                        if ack3 == 49:
                            logging.info("Button 0 pressed")
                            Display.show(Message.DGT_BUTTON, button=0)
                        if ack3 == 52:
                            logging.info("Button 1 pressed")
                            Display.show(Message.DGT_BUTTON, button=1)
                        if ack3 == 51:
                            logging.info("Button 2 pressed")
                            Display.show(Message.DGT_BUTTON, button=2)
                        if ack3 == 50:
                            logging.info("Button 3 pressed")
                            Display.show(Message.DGT_BUTTON, button=3)
                        if ack3 == 53:
                            logging.info("Button 4 pressed")
                            Display.show(Message.DGT_BUTTON, button=4)
                    if ack1 == 0x09:
                        main_version = ack2 >> 4
                        sub_version = ack2 & 0x0f
                        logging.debug("DGT clock version %0.2f", float(str(main_version) + '.' + str(sub_version)))
                        Display.show(Message.DGT_CLOCK_VERSION, main_version=main_version, sub_version=sub_version, attached="serial")
                elif any(message[:6]):
                    r_hours = message[0] & 0x0f
                    r_mins = (message[1] >> 4) * 10 + (message[1] & 0x0f)
                    r_secs = (message[2] >> 4) * 10 + (message[2] & 0x0f)
                    l_hours = message[3] & 0x0f
                    l_mins = (message[4] >> 4) * 10 + (message[4] & 0x0f)
                    l_secs = (message[5] >> 4) * 10 + (message[5] & 0x0f)
                    tr = [r_hours, r_mins, r_secs]
                    tl = [l_hours, l_mins, l_secs]
                    logging.info('DGT clock time received {} : {}'.format(tl, tr))
                    Display.show(Message.DGT_CLOCK_TIME, time_left=tl, time_right=tr)
                else:
                    logging.debug('DGT clock (null) message ignored')
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

                # Attention! This fen is NOT flipped
                logging.debug("Raw-Fen [%s]", fen)
                Display.show(Message.DGT_FEN, fen=fen)
                break
            if case(DgtMsg.DGT_MSG_FIELD_UPDATE):
                self.write_to_board([DgtCmd.DGT_SEND_BRD])  # Ask for the board when a piece moved
                break
            if case(DgtMsg.DGT_MSG_SERIALNR):
                # logging.debug(message)
                break
            if case():  # Default
                logging.warning("DGT message not handled [%s]", DgtMsg(message_id))

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
            logging.debug("<-DGT [%s], length %i", DgtMsg(message_id), message_length)
        except ValueError:
            logging.warning("Unknown message value %i", message_id)
        if message_length:
            message = unpack('>' + str(message_length) + 'B', self.serial.read(message_length))
            self.process_board_message(message_id, message)
            return message_id

    def process_incoming_board_forever(self):
        while True:
            try:
                if not self.serial_error:
                    c = self.serial.read(1)
                    if c:
                        self.read_board_message(head=c)
            except pyserial.SerialException as e:
                pass
            except TypeError:
                pass

    def startup_board(self):
        self.write_to_board([DgtCmd.DGT_SEND_UPDATE_NICE])  # Set the board update mode
        self.write_to_board([DgtCmd.DGT_SEND_VERSION])  # Get board version
        self.write_to_board([DgtCmd.DGT_SEND_BRD])  # Update the board

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
                w = self.waitchars[wait_counter]
                Display.show(Message.NO_EBOARD_ERROR, text='no E-board' + w, text_xl='board' + w)
                wait_counter = (wait_counter + 1) % len(self.waitchars)
                time.sleep(0.5)
        self.serial_error = False
        self.startup_board()

    def run(self):
        self.setup_serial()
        incoming_board_thread = Timer(0, self.process_incoming_board_forever)
        incoming_board_thread.start()
