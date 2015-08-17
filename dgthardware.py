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
import chess
from dgtinterface import *
import serial as pyserial
from utilities import *
from struct import unpack

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


class DGTHardware(DGTInterface):
    def __init__(self, device, enable_board_leds, disable_dgt_clock_beep):
        super(DGTHardware, self).__init__(enable_board_leds, disable_dgt_clock_beep)
        self.displayed_text = None  # The current clock display or None if in ClockNRun mode or unknown text
        self.clock_lock = False
        self.serial = None
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

        incoming_thread = threading.Timer(0, self.process_incoming_forever)
        incoming_thread.start()
        outgoing_thread = threading.Timer(0, self.process_outgoing_forever)
        outgoing_thread.start()
        self.startup(device)

    def write(self, message):
        serial_queue.put(message)

    def send_command(self, message):
        mes = message[3] if message[0].value == Commands.DGT_CLOCK_MESSAGE.value else message[0]
        logging.debug('->DGT [%s], length:%i', mes, len(message))
        if mes.value == Clock.DGT_CMD_CLOCK_ASCII.value:
            logging.debug('ASCII ' + str(message[4:10]))
        array = []
        for v in message:
            if type(v) is int:
                array.append(v)
            elif isinstance(v, enum.Enum):
                array.append(v.value)
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
            logging.debug('DGT clock locked')
            self.clock_lock = True

    def process_message(self, message_id, message):
        for case in switch(message_id):
            if case(Messages.DGT_MSG_VERSION):  # Get the DGT board version
                logging.debug("DGT board version %0.2f", float(str(message[0]) + '.' + str(message[1])))
                break
            # if case():
            #     logging.info("Got clock version number")
            #     break
            if case(Messages.DGT_MSG_BWTIME):
                if ((message[0] & 0x0f) == 0x0a) or ((message[3] & 0x0f) == 0x0a):  # Clock ack message
                    # Construct the ack message
                    ack0 = ((message[1]) & 0x7f) | ((message[3] << 3) & 0x80)
                    ack1 = ((message[2]) & 0x7f) | ((message[3] << 2) & 0x80)
                    ack2 = ((message[4]) & 0x7f) | ((message[0] << 3) & 0x80)
                    ack3 = ((message[5]) & 0x7f) | ((message[0] << 2) & 0x80)
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
                    if ack1 == 0x09:  # we using the beep command, to find out if a clock is there
                        main_version = ack2 >> 4
                        sub_version = ack2 & 0x0f
                        logging.debug("DGT clock version %0.2f", float(str(main_version) + '.' + str(sub_version)))
                        Display.show(Message.DGT_CLOCK_VERSION, main_version=main_version, sub_version=sub_version)
                    if ack0 != 0x10:
                        logging.warning("Clock ACK error %s", (ack0, ack1, ack2, ack3))
                        return
                    else:
                        logging.debug("Clock ACK [%s]", Clock(ack1))
                elif any(message[:6]):
                    r_hours = message[0] & 0x0f
                    r_mins = (message[1] >> 4) * 10 + (message[1] & 0x0f)
                    r_secs = (message[2] >> 4) * 10 + (message[1] & 0x0f)
                    l_hours = message[3] & 0x0f
                    l_mins = (message[4] >> 4) * 10 + (message[4] & 0x0f)
                    l_secs = (message[5] >> 4) * 10 + (message[5] & 0x0f)
                    logging.info(
                        'DGT clock time received {} : {}'.format((l_hours, l_mins, l_secs), (r_hours, r_mins, r_secs)))
                    self.displayed_text = None # reset saved text to unknown
                else:
                    logging.debug('DGT clock message ignored')

                if self.clock_lock:
                    logging.debug('DGT clock unlocked')
                    self.clock_lock = False
                else:
                    logging.debug('DGT clock already released')
                break
            if case(Messages.DGT_MSG_BOARD_DUMP):
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
            if case(Messages.DGT_MSG_FIELD_UPDATE):
                self.write([Commands.DGT_SEND_BRD])  # Ask for the board when a piece moved
                break
            if case():  # Default
                logging.warning("DGT message not handled : [%s]", Messages(message_id))

    def read_message(self, head=None):
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
            logging.debug("<-DGT [%s], length:%i", Messages(message_id), message_length)
        except ValueError:
            logging.warning("Unknown message value %i", message_id)
        if message_length:
            message = unpack('>' + str(message_length) + 'B', (self.serial.read(message_length)))
            self.process_message(message_id, message)
            return message_id

    def startup(self, device):
        # Set the board update mode
        self.write([Commands.DGT_SEND_UPDATE_NICE])
        # we sending a beep command, and see if its ack'ed
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x04, Clock.DGT_CMD_CLOCK_START_MESSAGE,
                    Clock.DGT_CMD_CLOCK_BEEP, 1, Clock.DGT_CMD_CLOCK_END_MESSAGE])
        # Get clock version
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x03, Clock.DGT_CMD_CLOCK_START_MESSAGE,
                    Clock.DGT_CMD_CLOCK_VERSION, Clock.DGT_CMD_CLOCK_END_MESSAGE])
        # Get board version
        self.write([Commands.DGT_SEND_VERSION])
        # Update the board
        self.write([Commands.DGT_SEND_BRD])

    def process_incoming_forever(self):
        while True:
            try:
                c = self.serial.read(1)
                if c:
                    self.read_message(head=c)
            except pyserial.SerialException as e:
                # device reports readiness to read but returned no data (device disconnected?)
                pass

    def process_outgoing_forever(self):
        while True:
            if not self.clock_lock:
                # Check if we have something to send
                try:
                    command = serial_queue.get()
                    # print ("get without waiting..")
                    self.send_command(command)
                except queue.Empty:
                    pass

    def _display_on_dgt_xl(self, text, beep=False):
        if self.clock_found and not self.enable_dgt_3000:
            while len(text) < 6:
                text += ' '
            if len(text) > 6:
                logging.warning('DGT XL clock message too long [%s]', text)
            logging.debug(text)
            self.write(
                [Commands.DGT_CLOCK_MESSAGE, 0x0b, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_DISPLAY,
                 text[2], text[1], text[0], text[5], text[4], text[3], 0x00, 0x03 if beep else 0x01,
                 Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def _display_on_dgt_3000(self, text, beep=False):
        if self.enable_dgt_3000:
            while len(text) < 8:
                text += ' '
            if len(text) > 8:
                logging.warning('DGT 3000 clock message too long [%s]', text)
            logging.debug(text)
            text = bytes(text, 'utf-8')
            self.write([Commands.DGT_CLOCK_MESSAGE, 0x0c, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_ASCII,
                        text[0], text[1], text[2], text[3], text[4], text[5], text[6], text[7], 0x03 if beep else 0x01,
                        Clock.DGT_CMD_CLOCK_END_MESSAGE])

    def display_text_on_clock(self, text, dgt_xl_text=None, beep=BeepLevel.CONFIG, force=True):
        beep = self.get_beep_level(beep)
        if self.enable_dgt_3000:
            if force or self.displayed_text != text:
                self._display_on_dgt_3000(text, beep)
        else:
            if dgt_xl_text:
                text = dgt_xl_text
            if force or self.displayed_text != text:
                self._display_on_dgt_xl(text, beep)
        self.displayed_text = text

    def display_move_on_clock(self, move, fen, beep=BeepLevel.CONFIG, force=True):
        beep = self.get_beep_level(beep)
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

    def light_squares_revelation_board(self, squares):
        if self.enable_board_leds:
            for sq in squares:
                dgt_square = (8 - int(sq[1])) * 8 + ord(sq[0]) - ord('a')
                logging.debug("REV2 light on square %s(%i)", sq, dgt_square)
                self.write([Commands.DGT_SET_LEDS, 0x04, 0x01, dgt_square, dgt_square])

    def clear_light_revelation_board(self):
        if self.enable_board_leds:
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
        self.write([Commands.DGT_CLOCK_MESSAGE, 0x03, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_END,
                    Clock.DGT_CMD_CLOCK_END_MESSAGE])
