# Copyright (C) 2013-2018 Jean-Francois Romang (jromang@posteo.de)
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

import struct
import logging
import subprocess
from threading import Timer, Lock
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read, path, listdir
from serial import Serial, SerialException, STOPBITS_ONE, PARITY_NONE, EIGHTBITS
import time

from dgt.util import DgtAck, DgtClk, DgtCmd, DgtMsg, ClockIcons, ClockSide, enum
from dgt.api import Message, Dgt
from utilities import RepeatedTimer, DisplayMsg, hms_time


class DgtBoard(object):

    """Handle the DGT board communication."""

    def __init__(self, device: str, disable_revelation_leds: bool, is_pi: bool, disable_end: bool, field_factor=0):
        super(DgtBoard, self).__init__()
        self.given_device = device
        self.device = device
        # rev2 flags
        self.disable_revelation_leds = disable_revelation_leds
        self.enable_revelation_pi = False
        self.is_revelation = False

        self.is_pi = is_pi
        self.disable_end = disable_end  # @todo for test - XL needs a "end_text" maybe!
        self.field_factor = field_factor % 10

        self.serial = None
        self.lock = Lock()  # lock the serial write
        self.incoming_board_thread = None
        self.lever_pos = None
        # the next three are only used for "not dgtpi" mode
        self.clock_lock = False  # serial connected clock is locked
        self.last_clock_command = []  # Used for resend last (failed) clock command
        self.enable_ser_clock = None  # None = "unknown status" False="only board found" True="clock also found"
        self.watchdog_timer = RepeatedTimer(1, self._watchdog)
        # bluetooth vars for Jessie upwards & autoconnect
        self.btctl = None
        self.bt_rfcomm = None
        self.bt_state = -1
        self.bt_line = ''
        self.bt_current_device = -1
        self.bt_mac_list = []
        self.bt_name_list = []
        self.bt_name = ''
        self.wait_counter = 0
        # keep the last time to find out errorous DGT_MSG_BWTIME messages (error: current time > last time)
        self.r_time = 3600 * 10  # max value cause 10h cant be reached by clock
        self.l_time = 3600 * 10  # max value cause 10h cant be reached by clock

        self.bconn_text = None
        # keep track of changed board positions
        self.field_timer = None
        self.field_timer_running = False
        self.channel = None

        self.in_settime = False  # this is true between set_clock and clock_start => use set values instead of clock
        self.low_time = False  # This is set from picochess.py and used to limit the field timer

    def expired_field_timer(self):
        """Board position hasnt changed for some time."""
        logging.debug('board position now stable => ask for complete board')
        self.field_timer_running = False
        self.write_command([DgtCmd.DGT_SEND_BRD])  # Ask for the board when a piece moved

    def stop_field_timer(self):
        """Stop the field timer cause another field change been send."""
        logging.debug('board position was unstable => ignore former field update')
        self.field_timer.cancel()
        self.field_timer.join()
        self.field_timer_running = False

    def start_field_timer(self):
        """Start the field timer waiting for a stable board position."""
        if self.low_time:
            wait = (0.2 if self.channel == 'BT' else 0.10) + 0.06 * self.field_factor  # bullet => allow more sliding
        else:
            wait = (0.5 if self.channel == 'BT' else 0.25) + 0.03 * self.field_factor  # BT's scanning in half speed
        logging.debug('board position changed => wait %.2fsecs for a stable result low_time: %s', wait, self.low_time)
        self.field_timer = Timer(wait, self.expired_field_timer)
        self.field_timer.start()
        self.field_timer_running = True

    def write_command(self, message: list):
        """Write the message list to the dgt board."""
        mes = message[3] if message[0].value == DgtCmd.DGT_CLOCK_MESSAGE.value else message[0]
        if not mes == DgtCmd.DGT_RETURN_SERIALNR:
            logging.debug('(ser) board put [%s] length: %i', mes, len(message))
            if mes.value == DgtClk.DGT_CMD_CLOCK_ASCII.value:
                logging.debug('sending text [%s] to (ser) clock', ''.join([chr(elem) for elem in message[4:12]]))
            if mes.value == DgtClk.DGT_CMD_REV2_ASCII.value:
                logging.debug('sending text [%s] to (rev) clock', ''.join([chr(elem) for elem in message[4:15]]))

        array = []
        char_to_xl = {
            '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66, '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f,
            '9': 0x6f, 'a': 0x5f, 'b': 0x7c, 'c': 0x58, 'd': 0x5e, 'e': 0x7b, 'f': 0x71, 'g': 0x3d, 'h': 0x74,
            'i': 0x10, 'j': 0x1e, 'k': 0x75, 'l': 0x38, 'm': 0x55, 'n': 0x54, 'o': 0x5c, 'p': 0x73, 'q': 0x67,
            'r': 0x50, 's': 0x6d, 't': 0x78, 'u': 0x3e, 'v': 0x2a, 'w': 0x7e, 'x': 0x64, 'y': 0x6e, 'z': 0x5b,
            ' ': 0x00, '-': 0x40, '/': 0x52, '|': 0x36, '\\': 0x64, '?': 0x53, '@': 0x65, '=': 0x48, '_': 0x08
        }
        for item in message:
            if isinstance(item, int):
                array.append(item)
            elif isinstance(item, enum.Enum):
                array.append(item.value)
            elif isinstance(item, str):
                for character in item:
                    array.append(char_to_xl[character.lower()])
            else:
                logging.error('type not supported [%s]', type(item))
                return False

        while True:
            if self.serial:
                with self.lock:
                    try:
                        self.serial.write(bytearray(array))
                        break
                    except ValueError:
                        logging.error('invalid bytes sent %s', message)
                        return False
                    except SerialException as write_expection:
                        logging.error(write_expection)
                        self.serial.close()
                        self.serial = None
                    except IOError as write_expection:
                        logging.error(write_expection)
                        self.serial.close()
                        self.serial = None
            if mes == DgtCmd.DGT_RETURN_SERIALNR:
                break
            time.sleep(0.1)

        if message[0] == DgtCmd.DGT_SET_LEDS:
            logging.debug('(rev) leds turned %s', 'on' if message[2] else 'off')
        if message[0] == DgtCmd.DGT_CLOCK_MESSAGE:
            self.last_clock_command = message
            if self.clock_lock:
                logging.warning('(ser) clock is already locked. Maybe a "resend"?')
            else:
                logging.debug('(ser) clock is locked now')
            self.clock_lock = time.time()
        else:
            time.sleep(0.1)  # give the board some time to process the command
        return True

    def _process_board_message(self, message_id: int, message: tuple, message_length: int):
        if False:  # switch-case
            pass
        elif message_id == DgtMsg.DGT_MSG_VERSION:
            if message_length != 2:
                logging.warning('illegal length in data')
            board_version = str(message[0]) + '.' + str(message[1])
            logging.debug('(ser) board version %0.2f', float(board_version))
            self.write_command([DgtCmd.DGT_SEND_BRD])  # Update the board => get first FEN
            if self.device.find('rfc') == -1:
                text_l, text_m, text_s = 'USB e-Board', 'USBboard', 'ok usb'
                self.channel = 'USB'
            else:
                btname5 = self.bt_name[-5:]
                if 'REVII' in self.bt_name:
                    text_l, text_m, text_s = 'RevII ' + btname5, 'Rev' + btname5, 'b' + btname5
                    self.is_revelation = True
                    self.write_command([DgtCmd.DGT_RETURN_LONG_SERIALNR])
                elif 'DGT_BT' in self.bt_name:
                    text_l, text_m, text_s = 'DGTBT ' + btname5, 'BT ' + btname5, 'b' + btname5
                else:
                    text_l, text_m, text_s = 'BT e-Board', 'BT board', 'ok bt'
                self.channel = 'BT'
                self.ask_battery_status()
            self.bconn_text = Dgt.DISPLAY_TEXT(l=text_l, m=text_m, s=text_s, wait=True, beep=False, maxtime=1.1,
                                               devs={'i2c', 'web'})  # serial clock lateron
            DisplayMsg.show(Message.DGT_EBOARD_VERSION(text=self.bconn_text, channel=self.channel))
            self.startup_serial_clock()  # now ask the serial clock to answer
            if self.watchdog_timer.is_running():
                logging.warning('watchdog timer is already running')
            else:
                logging.debug('watchdog timer is started')
                self.watchdog_timer.start()

        elif message_id == DgtMsg.DGT_MSG_BWTIME:
            if message_length != 7:
                logging.warning('illegal length in data')
            if ((message[0] & 0x0f) == 0x0a) or ((message[3] & 0x0f) == 0x0a):  # Clock ack message
                # Construct the ack message
                ack0 = ((message[1]) & 0x7f) | ((message[3] << 3) & 0x80)
                ack1 = ((message[2]) & 0x7f) | ((message[3] << 2) & 0x80)
                ack2 = ((message[4]) & 0x7f) | ((message[0] << 3) & 0x80)
                ack3 = ((message[5]) & 0x7f) | ((message[0] << 2) & 0x80)
                if ack0 != 0x10:
                    logging.warning('(ser) clock ACK error %s', (ack0, ack1, ack2, ack3))
                    if self.last_clock_command:
                        logging.debug('(ser) clock resending failed message [%s]', self.last_clock_command)
                        self.write_command(self.last_clock_command)
                        self.last_clock_command = []  # only resend once
                    return
                else:
                    logging.debug('(ser) clock ACK okay [%s]', DgtAck(ack1))
                    if self.last_clock_command:
                        cmd = self.last_clock_command[3]  # type: DgtClk
                        if cmd.value != ack1 and ack1 < 0x80:
                            logging.warning('(ser) clock ACK [%s] out of sync - last: [%s]', DgtAck(ack1), cmd)
                # @todo these lines are better as what is done on DgtHw but it doesnt work
                # if ack1 == DgtAck.DGT_ACK_CLOCK_SETNRUN.value:
                #     logging.info('(ser) clock out of set time now')
                #     self.in_settime = False
                if ack1 == DgtAck.DGT_ACK_CLOCK_BUTTON.value:
                    # this are the other (ack2-ack3) codes
                    # 05-49 33-52 17-51 09-50 65-53 | button 0-4 (single)
                    #       37-52 21-51 13-50 69-53 | button 0 + 1-4
                    #             49-51 41-50 97-53 | button 1 + 2-4
                    #                   25-50 81-53 | button 2 + 3-4
                    #                         73-53 | button 3 + 4
                    if ack3 == 49:
                        logging.info('(ser) clock button 0 pressed - ack2: %i', ack2)
                        DisplayMsg.show(Message.DGT_BUTTON(button=0, dev='ser'))
                    if ack3 == 52:
                        logging.info('(ser) clock button 1 pressed - ack2: %i', ack2)
                        DisplayMsg.show(Message.DGT_BUTTON(button=1, dev='ser'))
                    if ack3 == 51:
                        logging.info('(ser) clock button 2 pressed - ack2: %i', ack2)
                        DisplayMsg.show(Message.DGT_BUTTON(button=2, dev='ser'))
                    if ack3 == 50:
                        logging.info('(ser) clock button 3 pressed - ack2: %i', ack2)
                        DisplayMsg.show(Message.DGT_BUTTON(button=3, dev='ser'))
                    if ack3 == 53:
                        if ack2 == 69:
                            logging.info('(ser) clock button 0+4 pressed - ack2: %i', ack2)
                            DisplayMsg.show(Message.DGT_BUTTON(button=0x11, dev='ser'))
                        else:
                            logging.info('(ser) clock button 4 pressed - ack2: %i', ack2)
                            DisplayMsg.show(Message.DGT_BUTTON(button=4, dev='ser'))
                if ack1 == DgtAck.DGT_ACK_CLOCK_VERSION.value:
                    self.enable_ser_clock = True
                    main = ack2 >> 4
                    sub = ack2 & 0x0f
                    logging.debug('(ser) clock version %0.2f', float(str(main) + '.' + str(sub)))
                    if self.bconn_text:
                        self.bconn_text.devs = {'ser'}  # Now send the (delayed) message to serial clock
                        dev = 'ser'
                    else:
                        dev = 'err'
                    DisplayMsg.show(Message.DGT_CLOCK_VERSION(main=main, sub=sub, dev=dev, text=self.bconn_text))
            elif any(message[:7]):
                r_hours = message[0] & 0x0f
                r_mins = (message[1] >> 4) * 10 + (message[1] & 0x0f)
                r_secs = (message[2] >> 4) * 10 + (message[2] & 0x0f)
                l_hours = message[3] & 0x0f
                l_mins = (message[4] >> 4) * 10 + (message[4] & 0x0f)
                l_secs = (message[5] >> 4) * 10 + (message[5] & 0x0f)
                r_time = r_hours * 3600 + r_mins * 60 + r_secs
                l_time = l_hours * 3600 + l_mins * 60 + l_secs
                errtim = r_hours > 9 or l_hours > 9 or r_mins > 59 or l_mins > 59 or r_secs > 59 or l_secs > 59
                if errtim:  # complete illegal package received
                    logging.warning('(ser) clock illegal new time received %s', message)
                elif r_time > self.r_time or l_time > self.l_time:  # the new time is higher as the old => ignore
                    logging.warning('(ser) clock strange old time received %s l:%s r:%s',
                                    message, hms_time(self.l_time), hms_time(self.r_time))
                    if self.in_settime:
                        logging.info('(ser) clock still in set mode, ignore received time')
                        errtim = True
                    elif r_time - self.r_time > 3600 or l_time - self.l_time > 3600:
                        logging.info('(ser) clock new time over 1h difference, ignore received time')
                        errtim = True
                else:
                    logging.info('(ser) clock new time received l:%s r:%s', hms_time(l_time), hms_time(r_time))
                    status = message[6] & 0x3f
                    connect = not status & 0x20
                    if connect:
                        right_side_down = -0x40 if status & 0x02 else 0x40
                        if self.lever_pos != right_side_down:
                            logging.debug('(ser) clock button status: 0x%x old lever: %s', status, self.lever_pos)
                            if self.lever_pos is not None:
                                DisplayMsg.show(Message.DGT_BUTTON(button=right_side_down, dev='ser'))
                            self.lever_pos = right_side_down
                    else:
                        logging.info('(ser) clock not connected, sending old time l:%s r:%s',
                                     hms_time(self.l_time), hms_time(self.r_time))
                        l_time = self.l_time
                        r_time = self.r_time
                    if self.in_settime:
                        logging.info('(ser) clock still in set mode, sending old time l:%s r:%s',
                                     hms_time(self.l_time), hms_time(self.r_time))
                        l_time = self.l_time
                        r_time = self.r_time
                    DisplayMsg.show(Message.DGT_CLOCK_TIME(time_left=l_time, time_right=r_time, connect=connect,
                                                           dev='ser'))
                    if not self.enable_ser_clock:
                        dev = 'rev' if 'REVII' in self.bt_name else 'ser'
                        if self.watchdog_timer.is_running():  # a running watchdog means: board already found
                            logging.info('(%s) clock restarting setup', dev)
                            self.startup_serial_clock()
                        else:
                            logging.info('(%s) clock sends messages already but (%s) board still not found', dev, dev)
                if not errtim:
                    self.r_time = r_time
                    self.l_time = l_time
            else:
                logging.debug('(ser) clock null message ignored')
            if self.clock_lock:
                logging.debug('(ser) clock unlocked after %.3f secs', time.time() - self.clock_lock)
                self.clock_lock = False

        elif message_id == DgtMsg.DGT_MSG_BOARD_DUMP:
            if message_length != 64:
                logging.warning('illegal length in data')
            piece_to_char = {
                0x01: 'P', 0x02: 'R', 0x03: 'N', 0x04: 'B', 0x05: 'K', 0x06: 'Q',
                0x07: 'p', 0x08: 'r', 0x09: 'n', 0x0a: 'b', 0x0b: 'k', 0x0c: 'q',
                0x0d: '$', 0x0e: '%', 0x0f: '&', 0x00: '.'
            }
            board = ''
            for character in message:
                board += piece_to_char[character & 0x0f]
            logging.debug('\n' + '\n'.join(board[0 + i:8 + i] for i in range(0, len(board), 8)))  # Show debug board
            # Create fen from board
            fen = ''
            empty = 0
            for square in range(0, 64):
                if message[square] != 0 and message[square] < 0x0d:  # @todo for the moment ignore the special pieces
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    fen += piece_to_char[message[square] & 0x0f]
                else:
                    empty += 1
                if (square + 1) % 8 == 0:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    if square < 63:
                        fen += '/'

            # Attention! This fen is NOT flipped
            logging.debug('raw fen [%s]', fen)
            DisplayMsg.show(Message.DGT_FEN(fen=fen, raw=True))

        elif message_id == DgtMsg.DGT_MSG_FIELD_UPDATE:
            if message_length != 2:
                logging.warning('illegal length in data')
            if self.field_timer_running:
                self.stop_field_timer()
            self.start_field_timer()

        elif message_id == DgtMsg.DGT_MSG_SERIALNR:
            if message_length != 5:
                logging.warning('illegal length in data')
            DisplayMsg.show(Message.DGT_SERIAL_NR(number=''.join([chr(elem) for elem in message])))

        elif message_id == DgtMsg.DGT_MSG_LONG_SERIALNR:
            if message_length != 10:
                logging.warning('illegal length in data')
            number = ''.join([chr(elem) for elem in message])
            self.enable_revelation_pi = float(number[:4]) >= 3.25  # "3.250010001"=yes "0000000001"=no
            logging.info('(rev) clock in PiMode: %s - serial: %s', 'yes' if self.enable_revelation_pi else 'no', number)

        elif message_id == DgtMsg.DGT_MSG_BATTERY_STATUS:
            if message_length != 9:
                logging.warning('illegal length in data')
            DisplayMsg.show(Message.BATTERY(percent=message[0]))

        else:  # Default
            logging.warning('message not handled [%s]', DgtMsg(message_id))

    def _read_serial(self, bytes_toread=1):
        try:
            return self.serial.read(bytes_toread)
        except SerialException:
            pass
        except AttributeError:  # serial is None (race condition)
            pass
        return b''

    def _read_board_message(self, head: bytes):
        message = ()
        header_len = 3
        header = head + self._read_serial(header_len - 1)
        try:
            header = struct.unpack('>BBB', header)
        except struct.error:
            logging.warning('timeout in header reading')
            return message
        message_id = header[0]
        message_length = counter = (header[1] << 7) + header[2] - header_len
        if message_length <= 0 or message_length > 64:
            if message_id == 0x8f and message_length == 0x1f00:  # @todo find out why this can happen
                logging.warning('falsely DGT_SEND_EE_MOVES send before => receive and ignore EE_MOVES result')
                self.watchdog_timer.stop()  # this serial read gonna take around 8secs
                now = time.time()
                while counter > 0:
                    ee_moves = self._read_serial(counter)
                    logging.info('EE_MOVES 0x%x bytes read - inWaiting: 0x%x', len(ee_moves), self.serial.inWaiting())
                    counter -= len(ee_moves)
                    if time.time() - now > 15:
                        logging.warning('EE_MOVES needed over 15secs => ignore not readed 0x%x bytes now', counter)
                        break
                self.watchdog_timer.start()
            else:
                logging.warning('illegal length in message header 0x%x length: %i', message_id, message_length)
            return message

        try:
            if not message_id == DgtMsg.DGT_MSG_SERIALNR:
                logging.debug('(ser) board get [%s] length: %i', DgtMsg(message_id), message_length)
        except ValueError:
            logging.warning('illegal id in message header 0x%x length: %i', message_id, message_length)
            return message

        while counter:
            byte = self._read_serial()
            try:
                if byte:
                    data = struct.unpack('>B', byte)
                    counter -= 1
                    if data[0] & 0x80:
                        logging.warning('illegal data in message 0x%x found', message_id)
                        logging.warning('ignore collected message data %s', message)
                        return self._read_board_message(byte)
                    message += data
                else:
                    logging.warning('timeout in data reading')
            except struct.error:
                logging.warning('struct error => maybe a reconnected board?')

        self._process_board_message(message_id, message, message_length)
        return message

    def _process_incoming_board_forever(self):
        counter = 0
        logging.info('incoming_board ready')
        while True:
            byte = b''
            if self.serial:
                byte = self._read_serial()
            else:
                self._setup_serial_port()
                if self.serial:
                    logging.debug('sleeping for 0.5 secs. Afterwards startup the (ser) board')
                    time.sleep(0.5)
                    counter = 0
                    self._startup_serial_board()
            if byte and byte[0] & 0x80:
                self._read_board_message(head=byte)
            else:
                counter = (counter + 1) % 10
                if counter == 0 and not self.watchdog_timer.is_running():
                    self._watchdog()  # issue 150 - check for alive connection, so write something to the board
                time.sleep(0.1)

    def ask_battery_status(self):
        """Ask the BT board for the battery status."""
        self.write_command([DgtCmd.DGT_SEND_BATTERY_STATUS])  # Get battery status

    def startup_serial_clock(self):
        """Ask the clock for its version."""
        self.clock_lock = False
        self.enable_ser_clock = False
        command = [DgtCmd.DGT_CLOCK_MESSAGE, 0x03, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                   DgtClk.DGT_CMD_CLOCK_VERSION, DgtClk.DGT_CMD_CLOCK_END_MESSAGE]
        self.write_command(command)  # Get clock version

    def _startup_serial_board(self):
        self.write_command([DgtCmd.DGT_SEND_UPDATE_NICE])  # Set the board update mode
        self.write_command([DgtCmd.DGT_SEND_VERSION])  # Get board version

    def _watchdog(self):
        if self.clock_lock and not self.is_pi:
            if time.time() - self.clock_lock > 2:
                logging.warning('(ser) clock is locked over 2secs')
                logging.debug('resending locked (ser) clock message [%s]', self.last_clock_command)
                self.clock_lock = False
                self.write_command(self.last_clock_command)
        self.write_command([DgtCmd.DGT_RETURN_SERIALNR])  # ask for this AFTER cause of - maybe - old board hardware

    def _open_bluetooth(self):
        if self.bt_state == -1:
            # only for jessie upwards
            if path.exists('/usr/bin/bluetoothctl'):
                self.bt_state = 0

                # get rid of old rfcomm
                if path.exists('/dev/rfcomm123'):
                    logging.debug('BT releasing /dev/rfcomm123')
                    subprocess.call(['rfcomm', 'release', '123'])
                    subprocess.call(['cat', '/dev/rfcomm123'])  # Lucas
                self.bt_current_device = -1
                self.bt_mac_list = []
                self.bt_name_list = []

                logging.debug('BT starting bluetoothctl')
                self.btctl = subprocess.Popen('/usr/bin/bluetoothctl',
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              universal_newlines=True,
                                              shell=True)

                # set the O_NONBLOCK flag of file descriptor:
                flags = fcntl(self.btctl.stdout, F_GETFL)  # get current flags
                fcntl(self.btctl.stdout, F_SETFL, flags | O_NONBLOCK)

                self.btctl.stdin.write("power on\n")
                self.btctl.stdin.flush()
        else:  # state >= 0 so bluetoothctl is running
            try:  # check for new data from bluetoothctl
                while True:
                    bt_byte = read(self.btctl.stdout.fileno(), 1).decode(encoding='UTF-8', errors='ignore')
                    self.bt_line += bt_byte
                    if bt_byte == '' or bt_byte == '\n':
                        break
            except OSError:
                time.sleep(0.1)

            # complete line
            if '\n' in self.bt_line:
                if False:  # switch-case
                    pass
                elif 'Changing power on succeeded' in self.bt_line:
                    self.bt_state = 1
                    self.btctl.stdin.write("agent on\n")
                    self.btctl.stdin.flush()
                elif 'Agent registered' in self.bt_line:
                    self.bt_state = 2
                    self.btctl.stdin.write("default-agent\n")
                    self.btctl.stdin.flush()
                elif 'Default agent request successful' in self.bt_line:
                    self.bt_state = 3
                    self.btctl.stdin.write("scan on\n")
                    self.btctl.stdin.flush()
                elif 'Discovering: yes' in self.bt_line:
                    self.bt_state = 4
                elif 'Pairing successful' in self.bt_line:
                    self.bt_state = 6
                    logging.debug('BT pairing successful')
                elif 'Failed to pair: org.bluez.Error.AlreadyExists' in self.bt_line:
                    self.bt_state = 6
                    logging.debug('BT already paired')
                elif 'Failed to pair' in self.bt_line:
                    # try the next
                    self.bt_state = 4
                    logging.debug('BT pairing failed')
                elif 'not available' in self.bt_line:
                    # remove and try the next
                    self.bt_state = 4
                    self.bt_mac_list.remove(self.bt_mac_list[self.bt_current_device])
                    self.bt_name_list.remove(self.bt_name_list[self.bt_current_device])
                    self.bt_current_device -= 1
                    logging.debug('BT pairing failed, unknown device')
                elif ('DGT_BT_' in self.bt_line or 'PCS-REVII' in self.bt_line) and \
                        ('NEW' in self.bt_line or 'CHG' in self.bt_line) and 'Device' in self.bt_line:
                    # New e-Board found add to list
                    try:
                        if not self.bt_line.split()[3] in self.bt_mac_list:
                            self.bt_mac_list.append(self.bt_line.split()[3])
                            self.bt_name_list.append(self.bt_line.split()[4])
                            logging.debug('BT found device: %s %s', self.bt_line.split()[3], self.bt_line.split()[4])
                    except IndexError:
                        logging.error('BT wrong line [%s]', self.bt_line)
                # clear the line
                self.bt_line = ''

            # if 'Enter PIN code:' in self.bt_line:
            if 'PIN code' in self.bt_line:
                if 'DGT_BT_' in self.bt_name_list[self.bt_current_device]:
                    self.btctl.stdin.write("0000\n")
                    self.btctl.stdin.flush()
                if 'PCS-REVII' in self.bt_name_list[self.bt_current_device]:
                    self.btctl.stdin.write("1234\n")
                    self.btctl.stdin.flush()
                self.bt_line = ''

            if 'Confirm passkey' in self.bt_line:
                self.btctl.stdin.write("yes\n")
                self.btctl.stdin.flush()
                self.bt_line = ''

            # if there are devices in the list try one
            if self.bt_state == 4:
                if len(self.bt_mac_list) > 0:
                    self.bt_state = 5
                    self.bt_current_device += 1
                    if self.bt_current_device >= len(self.bt_mac_list):
                        self.bt_current_device = 0
                    logging.debug('BT pairing to: %s %s',
                                  self.bt_mac_list[self.bt_current_device],
                                  self.bt_name_list[self.bt_current_device])
                    self.btctl.stdin.write('pair ' + self.bt_mac_list[self.bt_current_device] + "\n")
                    self.btctl.stdin.flush()

            # pair successful, try rfcomm
            if self.bt_state == 6:
                # now try rfcomm
                self.bt_state = 7
                self.bt_rfcomm = subprocess.Popen('rfcomm connect 123 ' + self.bt_mac_list[self.bt_current_device],
                                                  stdin=subprocess.PIPE,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  universal_newlines=True,
                                                  shell=True)

            # wait for rfcomm to fail or succeed
            if self.bt_state == 7:
                # rfcomm succeeded
                if path.exists('/dev/rfcomm123'):
                    logging.debug('BT connected to: %s', self.bt_name_list[self.bt_current_device])
                    if self._open_serial('/dev/rfcomm123'):
                        self.btctl.stdin.write("quit\n")
                        self.btctl.stdin.flush()
                        self.bt_name = self.bt_name_list[self.bt_current_device]

                        self.bt_state = -1
                        return True
                # rfcomm failed
                if self.bt_rfcomm.poll() is not None:
                    logging.debug('BT rfcomm failed')
                    self.btctl.stdin.write('remove ' + self.bt_mac_list[self.bt_current_device] + "\n")
                    self.bt_mac_list.remove(self.bt_mac_list[self.bt_current_device])
                    self.bt_name_list.remove(self.bt_name_list[self.bt_current_device])
                    self.bt_current_device -= 1
                    self.btctl.stdin.flush()
                    self.bt_state = 4
        return False

    def _open_serial(self, device: str):
        assert not self.serial, 'serial connection still active: %s' % self.serial
        try:
            self.serial = Serial(device, stopbits=STOPBITS_ONE, parity=PARITY_NONE, bytesize=EIGHTBITS, timeout=0.5)
        except SerialException:
            return False
        return True

    def _setup_serial_port(self):
        def _success(device: str):
            self.device = device
            logging.debug('(ser) board connected to %s', self.device)
            return True

        waitchars = ['/', '-', '\\', '|']

        if self.watchdog_timer.is_running():
            logging.debug('watchdog timer is stopped now')
            self.watchdog_timer.stop()
        if self.serial:
            return True
        with self.lock:
            if self.given_device:
                if self._open_serial(self.given_device):
                    return _success(self.given_device)
            else:
                for file in listdir('/dev'):
                    if file.startswith('ttyACM') or file.startswith('ttyUSB') or file == 'rfcomm0':
                        dev = path.join('/dev', file)
                        if self._open_serial(dev):
                            return _success(dev)
                if self._open_bluetooth():
                    return _success('/dev/rfcomm123')

        # text = self.dgttranslate.text('N00_noboard', 'Board' + waitchars[self.wait_counter])
        bwait = 'Board' + waitchars[self.wait_counter]
        text = Dgt.DISPLAY_TEXT(l='no e-' + bwait, m='no' + bwait, s=bwait, wait=True, beep=False, maxtime=0.1,
                                devs={'i2c', 'web'})
        DisplayMsg.show(Message.DGT_NO_EBOARD_ERROR(text=text))
        self.wait_counter = (self.wait_counter + 1) % len(waitchars)
        return False

    # dgtHw functions start
    def _wait_for_clock(self, func: str):
        has_to_wait = False
        counter = 0
        while self.clock_lock:
            if not has_to_wait:
                has_to_wait = True
                logging.debug('(ser) clock is locked => waiting to serve: %s', func)
            time.sleep(0.1)
            counter = (counter + 1) % 30
            if counter == 0:
                logging.warning('(ser) clock is locked over 3secs')
        if has_to_wait:
            logging.debug('(ser) clock is released now')

    def set_text_rp(self, text: str, beep: int):
        """Display a text on a Pi enabled Rev2."""
        self._wait_for_clock('SetTextRp()')
        res = self.write_command([DgtCmd.DGT_CLOCK_MESSAGE, 0x0f, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                                  DgtClk.DGT_CMD_REV2_ASCII,
                                  text[0], text[1], text[2], text[3], text[4], text[5], text[6], text[7],
                                  text[8], text[9], text[10], beep,
                                  DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        return res

    def set_text_3k(self, text: str, beep: int):
        """Display a text on a 3000 Clock."""
        self._wait_for_clock('SetText3K()')
        res = self.write_command([DgtCmd.DGT_CLOCK_MESSAGE, 0x0c, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                                  DgtClk.DGT_CMD_CLOCK_ASCII,
                                  text[0], text[1], text[2], text[3], text[4], text[5], text[6], text[7], beep,
                                  DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        return res

    def set_text_xl(self, text: str, beep: int, left_icons=ClockIcons.NONE, right_icons=ClockIcons.NONE):
        """Display a text on a XL clock."""
        def _transfer(icons: ClockIcons):
            result = 0
            if icons == ClockIcons.DOT:
                result = 0x01
            if icons == ClockIcons.COLON:
                result = 0x02
            return result

        self._wait_for_clock('SetTextXL()')
        icn = (_transfer(right_icons) & 0x07) | (_transfer(left_icons) << 3) & 0x38
        res = self.write_command([DgtCmd.DGT_CLOCK_MESSAGE, 0x0b, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                                  DgtClk.DGT_CMD_CLOCK_DISPLAY,
                                  text[2], text[1], text[0], text[5], text[4], text[3], icn, beep,
                                  DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        return res

    def set_and_run(self, lr: int, lh: int, lm: int, ls: int, rr: int, rh: int, rm: int, rs: int):
        """Set the clock with times and let it run."""
        self._wait_for_clock('SetAndRun()')
        side = ClockSide.NONE
        if lr == 1 and rr == 0:
            side = ClockSide.LEFT
        if lr == 0 and rr == 1:
            side = ClockSide.RIGHT
        res = self.write_command([DgtCmd.DGT_CLOCK_MESSAGE, 0x0a, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                                  DgtClk.DGT_CMD_CLOCK_SETNRUN,
                                  lh, lm, ls, rh, rm, rs, side,
                                  DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        return res

    def end_text(self):
        """Return the clock display to time display."""
        self._wait_for_clock('EndText()')
        res = self.write_command([DgtCmd.DGT_CLOCK_MESSAGE, 0x03, DgtClk.DGT_CMD_CLOCK_START_MESSAGE,
                                  DgtClk.DGT_CMD_CLOCK_END,
                                  DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
        return res

    def light_squares_on_revelation(self, uci_move: str):
        """Light the Rev2 leds."""
        if self.is_revelation and not self.disable_revelation_leds:
            # self._wait_for_clock('LIGHTon')
            logging.debug('(rev) leds turned on - move: %s', uci_move)
            fr_s = (8 - int(uci_move[1])) * 8 + ord(uci_move[0]) - ord('a')
            to_s = (8 - int(uci_move[3])) * 8 + ord(uci_move[2]) - ord('a')
            self.write_command([DgtCmd.DGT_SET_LEDS, 0x04, 0x01, fr_s, to_s, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])

    def clear_light_on_revelation(self):
        """Clear the Rev2 leds."""
        if self.is_revelation and not self.disable_revelation_leds:
            # self._wait_for_clock('LIGHToff')
            logging.debug('(rev) leds turned off')
            self.write_command([DgtCmd.DGT_SET_LEDS, 0x04, 0x00, 0x40, 0x40, DgtClk.DGT_CMD_CLOCK_END_MESSAGE])
    # dgtHw functions end

    def run(self):
        """NOT called from threading.Thread instead inside the __init__ function from hw.py."""
        self.incoming_board_thread = Timer(0, self._process_incoming_board_forever)
        self.incoming_board_thread.start()
