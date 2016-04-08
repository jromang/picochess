# Copyright (C) 2013-2016 Jean-Francois Romang (jromang@posteo.de)
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

import serial as pyserial

import struct
from utilities import *
from threading import Timer, Lock

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
    'y': 0x20 | 0x08 | 0x04 | 0x40 | 0x02, 'z': 0x01 | 0x40 | 0x08 | 0x02 | 0x10, ' ': 0x00, '-': 0x40,
    '/': 0x20 | 0x40 | 0x04, '|': 0x20 | 0x10 | 0x02 | 0x04, '\\': 0x02 | 0x40 | 0x10
}

piece_to_char = {
    0x01: 'P', 0x02: 'R', 0x03: 'N', 0x04: 'B', 0x05: 'K', 0x06: 'Q',
    0x07: 'p', 0x08: 'r', 0x09: 'n', 0x0a: 'b', 0x0b: 'k', 0x0c: 'q', 0x00: '.'
}


class DgtSerial(object):
    def __init__(self, device):
        super(DgtSerial, self).__init__()
        self.device = device
        self.serial = None
        self.waitchars = ['/', '-', '\\', '|']
        self.lock = Lock()  # inside setup_serial()
        self.incoming_board_thread = None
        # the next three are only used for "not dgtpi" mode
        self.clock_lock = False  # serial connected clock is locked
        self.last_clock_command = []  # Used for resend last (failed) clock command
        self.rt = RepeatedTimer(1, self.watchdog)

    def write_board_command(self, message):
        mes = message[3] if message[0].value == DgtCmd.DGT_CLOCK_MESSAGE.value else message[0]
        logging.debug('->DGT board [%s], length: %i', mes, len(message))
        if mes.value == DgtClk.DGT_CMD_CLOCK_ASCII.value:
            logging.debug('sending text [{}] to clock'. format(''.join([chr(elem) for elem in message[4:10]])))

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
                logging.error('type not supported [%s]', type(v))

        while True:
            if not self.serial:
                self.setup_serial()
                self.startup_board()
            try:
                self.serial.write(bytearray(array))
                break
            except ValueError:
                logging.error('invalid bytes sent {0}'.format(message))
                break
            except pyserial.SerialException as e:
                logging.error(e)
                self.serial.close()
                self.serial = None
            except IOError as e:
                logging.error(e)
                self.serial.close()
                self.serial = None
        if message[0] == DgtCmd.DGT_CLOCK_MESSAGE:
            self.last_clock_command = message
            if self.clock_lock:
                logging.warning('DGT clock [ser]: already locked. Maybe a "resend"?')
            else:
                logging.debug('DGT clock [ser]: locked')
                self.clock_lock = time.time()

    def process_board_message(self, message_id, message):
        for case in switch(message_id):
            if case(DgtMsg.DGT_MSG_VERSION):  # Get the DGT board version
                board_version = str(message[0]) + '.' + str(message[1])
                logging.debug("DGT board version %0.2f", float(board_version))
                if self.device.find('rfc') == -1:
                    text_l, text_m, text_s = 'USB E-board', 'USBboard', 'ok usb'
                    channel = 'USB'
                else:
                    text_l, text_m, text_s = 'BT E-board', 'BT board', 'ok bt'
                    channel = 'BT'
                text = Dgt.DISPLAY_TEXT(l=text_l, m=text_m, s=text_s, beep=False, duration=0.5)
                DisplayMsg.show(Message.EBOARD_VERSION(text=text, channel=channel))
                if self.rt.is_running():
                    logging.warning('watchdog timer is already running')
                else:
                    self.rt.start()
                break
            if case(DgtMsg.DGT_MSG_BWTIME):
                if ((message[0] & 0x0f) == 0x0a) or ((message[3] & 0x0f) == 0x0a):  # Clock ack message
                    # Construct the ack message
                    ack0 = ((message[1]) & 0x7f) | ((message[3] << 3) & 0x80)
                    ack1 = ((message[2]) & 0x7f) | ((message[3] << 2) & 0x80)
                    ack2 = ((message[4]) & 0x7f) | ((message[0] << 3) & 0x80)
                    ack3 = ((message[5]) & 0x7f) | ((message[0] << 2) & 0x80)
                    if ack0 != 0x10:
                        logging.warning("DGT clock [ser]: ACK error %s", (ack0, ack1, ack2, ack3))
                        if self.last_clock_command:
                            logging.debug('resending failed DGT clock message [%s]', self.last_clock_command)
                            self.write_board_command(self.last_clock_command)
                            self.last_clock_command = []  # only resend once
                        break
                    else:
                        logging.debug("DGT clock [ser]: ACK okay [%s]", DgtClk(ack1))
                    if ack1 == 0x88:
                        # this are the other (ack2-ack3) codes
                        # 05-49 33-52 17-51 09-50 65-53 | button 0-4 (single)
                        #       37-52 21-51 13-50 69-53 | button 0 + 1-4
                        #             49-51 41-50 97-53 | button 1 + 2-4
                        #                   25-50 81-53 | button 2 + 3-4
                        #                         73-53 | button 3 + 4
                        if ack3 == 49:
                            logging.info("DGT clock [ser]: button 0 pressed - ack2: %i", ack2)
                            DisplayMsg.show(Message.DGT_BUTTON(button=0))
                        if ack3 == 52:
                            logging.info("DGT clock [ser]: button 1 pressed - ack2: %i", ack2)
                            DisplayMsg.show(Message.DGT_BUTTON(button=1))
                        if ack3 == 51:
                            logging.info("DGT clock [ser]: button 2 pressed - ack2: %i", ack2)
                            DisplayMsg.show(Message.DGT_BUTTON(button=2))
                        if ack3 == 50:
                            logging.info("DGT clock [ser]: button 3 pressed - ack2: %i", ack2)
                            DisplayMsg.show(Message.DGT_BUTTON(button=3))
                        if ack3 == 53:
                            if ack2 == 69:
                                logging.info("DGT clock [ser]: button 0+4 pressed - ack2: %i", ack2)
                                DisplayMsg.show(Message.DGT_BUTTON(button=40))
                            else:
                                logging.info("DGT clock [ser]: button 4 pressed - ack2: %i", ack2)
                                DisplayMsg.show(Message.DGT_BUTTON(button=4))
                    if ack1 == 0x09:
                        main_version = ack2 >> 4
                        sub_version = ack2 & 0x0f
                        logging.debug("DGT clock [ser]: version %0.2f", float(str(main_version) + '.' + str(sub_version)))
                        DisplayMsg.show(Message.DGT_CLOCK_VERSION(main_version=main_version, sub_version=sub_version, attached="serial"))
                elif any(message[:6]):
                    r_hours = message[0] & 0x0f
                    r_mins = (message[1] >> 4) * 10 + (message[1] & 0x0f)
                    r_secs = (message[2] >> 4) * 10 + (message[2] & 0x0f)
                    l_hours = message[3] & 0x0f
                    l_mins = (message[4] >> 4) * 10 + (message[4] & 0x0f)
                    l_secs = (message[5] >> 4) * 10 + (message[5] & 0x0f)
                    tr = [r_hours, r_mins, r_secs]
                    tl = [l_hours, l_mins, l_secs]
                    logging.info('DGT clock [ser]: received time from clock l:{} r:{}'.format(tl, tr))
                    DisplayMsg.show(Message.DGT_CLOCK_TIME(time_left=tl, time_right=tr))
                else:
                    logging.debug('DGT clock [ser]: null message ignored')
                if self.clock_lock:
                    logging.debug('DGT clock [ser]: unlocked after {0:.3f} secs'.format(time.time() - self.clock_lock))
                    self.clock_lock = False
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
                DisplayMsg.show(Message.DGT_FEN(fen=fen))
                break
            if case(DgtMsg.DGT_MSG_FIELD_UPDATE):
                self.write_board_command([DgtCmd.DGT_SEND_BRD])  # Ask for the board when a piece moved
                break
            if case(DgtMsg.DGT_MSG_SERIALNR):
                # logging.debug(''.join([chr(elem) for elem in message]))
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
        header = struct.unpack(pattern, header)
        # header = struct.unpack('>BBB', (self.serial.read(3)))
        message_id = header[0]
        message_length = (header[1] << 7) + header[2] - 3

        try:
            logging.debug("<-DGT board [%s], length: %i", DgtMsg(message_id), message_length)
            message = struct.unpack('>' + str(message_length) + 'B', self.serial.read(message_length))
            self.process_board_message(message_id, message)
        except ValueError:
            logging.warning("unknown DGT message value: %i length: %i", message_id, message_length)
        return message_id

    def process_incoming_board_forever(self):
        while True:
            try:
                c = None
                if self.serial:
                    c = self.serial.read(1)
                if c:
                    self.read_board_message(head=c)
                else:
                    time.sleep(0.1)
            except pyserial.SerialException:
                pass
            except TypeError:
                pass
            except struct.error:  # can happen, when plugin board-cable again
                pass

    def startup_board(self):
        self.write_board_command([DgtCmd.DGT_SEND_UPDATE_NICE])  # Set the board update mode
        self.write_board_command([DgtCmd.DGT_SEND_VERSION])  # Get board version
        self.write_board_command([DgtCmd.DGT_SEND_BRD])  # Update the board

    def watchdog(self):
        self.write_board_command([DgtCmd.DGT_RETURN_SERIALNR])  # the code doesnt really matter ;-)

    def setup_serial(self):
        if self.rt.is_running():
            self.rt.stop()
        with self.lock:
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
                    s = 'Board' + self.waitchars[wait_counter]
                    text = Dgt.DISPLAY_TEXT(l='no e-' + s, m='no' + s, s=s, beep=False, duration=0)
                    DisplayMsg.show(Message.NO_EBOARD_ERROR(text=text))
                    wait_counter = (wait_counter + 1) % len(self.waitchars)
                    time.sleep(0.5)

    def run(self):
        self.incoming_board_thread = Timer(0, self.process_incoming_board_forever)
        self.incoming_board_thread.start()
        self.setup_serial()
