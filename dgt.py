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


import serial
import sys
import time
from threading import Thread
from threading import RLock
from struct import unpack

from itertools import cycle
clock_blink_iterator = cycle(range(2))

BOARD = "Board"

FEN = "FEN"
CLOCK_BUTTON_PRESSED = "CLOCK_BUTTON_PRESSED"
CLOCK_ACK = "CLOCK_ACK"
CLOCK_LEVER = "CLOCK_LEVER"

DGTNIX_MSG_UPDATE = 0x05
_DGTNIX_SEND_BRD = 0x42
_DGTNIX_MESSAGE_BIT = 0x80
_DGTNIX_BOARD_DUMP =  0x06
_DGTNIX_BWTIME = 0x0d

_DGTNIX_MSG_BOARD_DUMP = _DGTNIX_MESSAGE_BIT|_DGTNIX_BOARD_DUMP

_DGTNIX_SEND_UPDATE_NICE = 0x4b

# message emitted when a piece is added onto the board
DGTNIX_MSG_MV_ADD = 0x00
#message emitted when a piece is removed from the board
DGTNIX_MSG_MV_REMOVE = 0x01

DGT_SIZE_FIELD_UPDATE = 5
_DGTNIX_FIELD_UPDATE =   0x0e
_DGTNIX_EMPTY = 0x00
_DGTNIX_WPAWN = 0x01
_DGTNIX_WROOK = 0x02
_DGTNIX_WKNIGHT = 0x03
_DGTNIX_WBISHOP = 0x04
_DGTNIX_WKING = 0x05
_DGTNIX_WQUEEN = 0x06
_DGTNIX_BPAWN =      0x07
_DGTNIX_BROOK  =     0x08
_DGTNIX_BKNIGHT =    0x09
_DGTNIX_BBISHOP =    0x0a
_DGTNIX_BKING   =    0x0b
_DGTNIX_BQUEEN  =    0x0c

_DGTNIX_CLOCK_MESSAGE = 0x2b
_DGTNIX_SEND_CLK = 0x41
_DGTNIX_SEND_UPDATE = 0x43
_DGTNIX_SEND_UPDATE_BRD = 0x44
_DGTNIX_SEND_SERIALNR = 0x45
_DGTNIX_SEND_BUSADDRESS = 0x46
_DGTNIX_SEND_TRADEMARK = 0x47
_DGTNIX_SEND_VERSION = 0x4d
_DGTNIX_SEND_EE_MOVES = 0x49
_DGTNIX_SEND_RESET = 0x40

_DGTNIX_SIZE_BOARD_DUMP = 67
_DGTNIX_NONE = 0x00
_DGTNIX_BOARD_DUMP = 0x06
_DGTNIX_EE_MOVES = 0x0f
_DGTNIX_BUSADDRESS = 0x10
_DGTNIX_SERIALNR = 0x11
_DGTNIX_TRADEMARK = 0x12
_DGTNIX_VERSION = 0x13

DGTNIX_RIGHT_DOT = 0x01
DGTNIX_RIGHT_SEMICOLON = 0x02
DGTNIX_RIGHT_1 = 0x04
DGTNIX_LEFT_DOT = 0x08
DGTNIX_LEFT_SEMICOLON = 0x10
DGTNIX_LEFT_1 = 0x20

piece_map = {
    _DGTNIX_EMPTY : ' ',
    _DGTNIX_WPAWN : 'P',
    _DGTNIX_WROOK : 'R',
    _DGTNIX_WKNIGHT : 'N',
    _DGTNIX_WBISHOP : 'B',
    _DGTNIX_WKING : 'K',
    _DGTNIX_WQUEEN : 'Q',
    _DGTNIX_BPAWN : 'p',
    _DGTNIX_BROOK : 'r',
    _DGTNIX_BKNIGHT : 'n',
    _DGTNIX_BBISHOP : 'b',
    _DGTNIX_BKING : 'k',
    _DGTNIX_BQUEEN : 'q'
}

dgt_send_message_list = [_DGTNIX_CLOCK_MESSAGE, _DGTNIX_SEND_CLK, _DGTNIX_SEND_BRD, _DGTNIX_SEND_UPDATE,
                         _DGTNIX_SEND_UPDATE_BRD, _DGTNIX_SEND_SERIALNR, _DGTNIX_SEND_BUSADDRESS, _DGTNIX_SEND_TRADEMARK,
                         _DGTNIX_SEND_VERSION, _DGTNIX_SEND_UPDATE_NICE, _DGTNIX_SEND_EE_MOVES, _DGTNIX_SEND_RESET]

class Event(object):
    pass



class DGTBoard(object):
    def __init__(self, device, virtual = False, send_board = True):
        self.board_reversed = False
        self.clock_ack_recv = False
        # self.clock_queue = Queue()
        self.dgt_clock = False
        self.dgt_clock_lock = RLock()
        # self.dgt_clock_ack_lock = RLock()
        # self.dgt_clock_ack_queue = Queue()

        if not virtual:
            self.ser = serial.Serial(device,stopbits=serial.STOPBITS_ONE)
            self.write(chr(_DGTNIX_SEND_UPDATE_NICE))
            if send_board:
                self.write(chr(_DGTNIX_SEND_BRD))

        self.callbacks = []

    def get_board(self):
        self.write(chr(_DGTNIX_SEND_BRD))

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def fire(self, **attrs):
        e = Event()
        e.source = self
        for k, v in attrs.iteritems():
            setattr(e, k, v)
        for fn in self.callbacks:
            fn(e)

    def convertInternalPieceToExternal(self, c):
        if piece_map.has_key(c):
            return piece_map[c]

    def sendMessageToBoard(self, i):
        if i in dgt_send_message_list:
            self.write(i)
        else:
            raise "Critical, cannot send - Unknown command: {0}".format(unichr(i))

    def dump_board(self, board):
        pattern = '>'+'B'*len(board)
        buf = unpack(pattern, board)

        if self.board_reversed:
            buf = buf[::-1]

        output = "__"*8+"\n"
        for square in xrange(0,len(board)):
            if square and square%8 == 0:
                output+= "|\n"
                output += "__"*8+"\n"

            output+= "|"
            output+= self.convertInternalPieceToExternal(buf[square])
        output+= "|\n"
        output+= "__"*8
        return output

    # Two reverse calls will bring back board to original orientation
    def reverse_board(self):
        print "Reversing board!"
        self.board_reversed = not self.board_reversed

    def extract_base_fen(self, board):
        FEN = []
        empty = 0
        for sq in range(0, 64):
            if board[sq] != 0:
                if empty > 0:
                    FEN.append(str(empty))
                    empty = 0
                FEN.append(self.convertInternalPieceToExternal(board[sq]))
            else:
                empty += 1
            if (sq + 1) % 8 == 0:
                if empty > 0:
                    FEN.append(str(empty))
                    empty = 0
                if sq < 63:
                    FEN.append("/")
                empty = 0

        return FEN

    def get_fen(self, board, tomove='w'):
        pattern = '>'+'B'*len(board)
        board = unpack(pattern, board)

        if self.board_reversed:
            board = board[::-1]

        FEN = self.extract_base_fen(board)# Check if board needs to be reversed
        if ''.join(FEN) == "RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr":
            self.reverse_board()
            board = board[::-1]
            # Redo FEN generation - should be a fast operation
            FEN = self.extract_base_fen(board)# Check if board needs to be reversed

        FEN.append(' ')

        FEN.append(tomove)

        FEN.append(' ')
#         possible castlings
        FEN.append('K')
        FEN.append('Q')
        FEN.append('k')
        FEN.append('q')
        FEN.append(' ')
        FEN.append('-')
        FEN.append(' ')
        FEN.append('0')
        FEN.append(' ')
        FEN.append('1')
        FEN.append('0')

        return ''.join(FEN)

    def read(self, message_length):
        return self.ser.read(message_length)

    def write(self, message):
        self.ser.write(message)

    # Converts a lowercase ASCII character or digit to DGT Clock representation
    @staticmethod
    def char_to_lcd_code(c):
        if c == '0':
            return 0x01 | 0x02 | 0x20 | 0x08 | 0x04 | 0x10
        if c == '1':
            return 0x02 | 0x04
        if c == '2':
            return 0x01 | 0x40 | 0x08 | 0x02 | 0x10
        if c == '3':
            return 0x01 | 0x40 | 0x08 | 0x02 | 0x04
        if c == '4':
            return 0x20 | 0x04 | 0x40 | 0x02
        if c == '5':
            return 0x01 | 0x40 | 0x08 | 0x20 | 0x04
        if c == '6':
            return 0x01 | 0x40 | 0x08 | 0x20 | 0x04 | 0x10
        if c == '7':
            return 0x02 | 0x04 | 0x01
        if c == '8':
            return 0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10 | 0x08
        if c == '9':
            return 0x01 | 0x40 | 0x08 | 0x02 | 0x04 | 0x20
        if c == 'a':
            return 0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10
        if c == 'b':
            return 0x20 | 0x04 | 0x40 | 0x08 | 0x10
        if c == 'c':
            return 0x01 | 0x20 | 0x10 | 0x08
        if c == 'd':
            return 0x10 | 0x40 | 0x08 | 0x02 | 0x04
        if c == 'e':
            return 0x01 | 0x40 | 0x08 | 0x20 | 0x10
        if c == 'f':
            return 0x01 | 0x40 | 0x20 | 0x10
        if c == 'g':
            return 0x01 | 0x20 | 0x10 | 0x08 | 0x04
        if c == 'h':
            return 0x20 | 0x10 | 0x04 | 0x40
        if c == 'i':
            return 0x02 | 0x04
        if c == 'j':
            return 0x02 | 0x04 | 0x08 | 0x10
        if c == 'k':
            return 0x01 | 0x20 | 0x40 | 0x04 | 0x10
        if c == 'l':
            return 0x20 | 0x10 | 0x08
        if c == 'm':
            return 0x01 | 0x40 | 0x04 | 0x10
        if c == 'n':
            return 0x40 | 0x04 | 0x10
        if c == 'o':
            return 0x40 | 0x04 | 0x10 | 0x08
        if c == 'p':
            return 0x01 | 0x40 | 0x20 | 0x10 | 0x02
        if c == 'q':
            return 0x01 | 0x40 | 0x20 | 0x04 | 0x02
        if c == 'r':
            return 0x40 | 0x10
        if c == 's':
            return 0x01 | 0x40 | 0x08 | 0x20 | 0x04
        if c == 't':
            return 0x20 | 0x10 | 0x08 | 0x40
        if c == 'u':
            return 0x08 | 0x02 | 0x20 | 0x04 | 0x10
        if c == 'v':
            return 0x08 | 0x02 | 0x20
        if c == 'w':
            return 0x40 | 0x08 | 0x20 | 0x02
        if c == 'x':
            return 0x20 | 0x10 | 0x04 | 0x40 | 0x02
        if c == 'y':
            return 0x20 | 0x08 | 0x04 | 0x40 | 0x02
        if c == 'z':
            return 0x01 | 0x40 | 0x08 | 0x02 | 0x10
        return 0

    @staticmethod
    def compute_dgt_time_string(t):
        if t < 0:
            return "   "
        t /= 1000

        if t < 1200:
        #minutes.seconds mode

            minutes = t / 60
            seconds = t - minutes * 60
            if minutes >= 10:
                minutes -= 10
            # print "seconds : {0}".format(seconds)
            return "{0}{1:02d}".format(minutes, seconds)
            # oss << minutes << setfill ('0') << setw (2) << seconds;

        else:
        #hours:minutes mode
            hours = t / 3600
            minutes = (t - (hours * 3600)) / 60
            return "{0}{1:02d}".format(hours, minutes)


    def print_time_on_clock(self, w_time, b_time, w_blink=True, b_blink=True):
        dots = 0
        w_dots = True
        b_dots = True
        if w_blink and w_time >= 1200000:
            w_dots = clock_blink_iterator.next()
        if b_blink and b_time >= 1200000:
            b_dots = clock_blink_iterator.next()

        if not self.board_reversed:
            s = self.compute_dgt_time_string(w_time) + self.compute_dgt_time_string(b_time)
            if w_time < 1200000: #minutes.seconds mode
                if w_dots:
                    dots |= DGTNIX_LEFT_DOT
                if w_time >= 600000:
                    dots |= DGTNIX_LEFT_1
            elif w_dots:
                dots |= DGTNIX_LEFT_SEMICOLON #hours:minutes mode
            #black
            if b_time < 1200000:
            #minutes.seconds mode

                if b_dots:
                    dots |= DGTNIX_RIGHT_DOT
                if b_time >= 600000:
                    dots |= DGTNIX_RIGHT_1

            elif b_dots:
                dots |= DGTNIX_RIGHT_SEMICOLON #hours:minutes mode

        else:
            s = self.compute_dgt_time_string(b_time) + self.compute_dgt_time_string(w_time)
            if b_time < 1200000: #minutes.seconds mode
                if b_dots:
                    dots |= DGTNIX_LEFT_DOT
                if b_time >= 600000:
                    dots |= DGTNIX_LEFT_1
            elif b_dots:
                dots |= DGTNIX_LEFT_SEMICOLON #hours:minutes mode
            #black
            if w_time < 1200000:
            #minutes.seconds mode

                if w_dots:
                    dots |= DGTNIX_RIGHT_DOT
                if w_time >= 600000:
                    dots |= DGTNIX_RIGHT_1

            elif w_dots:
                dots |= DGTNIX_RIGHT_SEMICOLON #hours:minutes mode
    #       }
    # else
    #   {
    #     s = getDgtTimeString (bClockTime) + getDgtTimeString (wClockTime);
    #     //black
    #     if (bClockTime < 1200000) //minutes.seconds mode
    #       {
    #         if (bDots) dots |= DGTNIX_LEFT_DOT;
    #         if (bClockTime >= 600000) dots |= DGTNIX_LEFT_1;
    #       }
    #     else if (bDots) dots |= DGTNIX_LEFT_SEMICOLON; //hours:minutes mode
    #     //white
    #     if (wClockTime < 1200000) //minutes.seconds mode
    #       {
    #         if (wDots) dots |= DGTNIX_RIGHT_DOT;
    #         if (wClockTime >= 600000) dots |= DGTNIX_RIGHT_1;
    #       }
    #     else if (wDots) dots |= DGTNIX_RIGHT_SEMICOLON; //hours:minutes mode
    #   }
    #     dgtnixPrintMessageOnClock (s.c_str (), false, dots);
        self.send_message_to_clock(s, False, dots)

    def send_message_to_clock(self, message, beep, dots, move=False, test_clock=False, max_num_tries = 5):
        # Todo locking?
        print "Got message to clock: {0}".format(message)
        if move:
            message = self.format_move_for_dgt(message)
        else:
            message = self.format_str_for_dgt(message)
        with self.dgt_clock_lock:
            # self.clock_ack_recv = False
                  #     time.sleep(5)
            self._sendMessageToClock(self.char_to_lcd_code(message[0]), self.char_to_lcd_code(message[1]),
                                self.char_to_lcd_code(message[2]), self.char_to_lcd_code(message[3]),
                                self.char_to_lcd_code(message[4]), self.char_to_lcd_code(message[5]),
                                beep, dots, test_clock=test_clock, max_num_tries = max_num_tries)
            # self.clock_ack_recv = False
            if test_clock and not self.dgt_clock:
                tries = 1
                while True:
                    time.sleep(1)
                    if not self.dgt_clock:
                        tries += 1
                        if tries > max_num_tries:
                            break
                        self._sendMessageToClock(self.char_to_lcd_code(message[0]), self.char_to_lcd_code(message[1]),
                                    self.char_to_lcd_code(message[2]), self.char_to_lcd_code(message[3]),
                                    self.char_to_lcd_code(message[4]), self.char_to_lcd_code(message[5]),
                                    beep, dots, test_clock=test_clock, max_num_tries = max_num_tries)
                    else:
                        break




    def test_for_dgt_clock(self, message="pic023", wait_time = 5):
    # try:
    #     signal.signal(signal.SIGALRM, self.dgt_clock_test_post_handler)

        # signal.alarm(wait_time)
        self.send_message_to_clock(message, True, False, test_clock=True, max_num_tries=wait_time)

        # signal.alarm(0)
        # except serial.serialutil.SerialException:
        #     return False
        # return True

    def dgt_clock_test_post_handler(self, signum, frame):
        if self.dgt_clock:
            print "Clock found"
            # self.dgt_clock = True
        else:
            print "No DGT Clock found"
            # self.dgt_clock = False

    def format_str_for_dgt(self, s):
        if len(s)>6:
            s = s[:6]
        if len(s) < 6:
            remainder = 6 - len(s)
            s = " "*remainder + s
        return s

    def format_move_for_dgt(self, s):
        mod_s = s[:2]+' '+s[2:]
        if len(mod_s)<6:
            mod_s+=" "
        return mod_s

    def _sendMessageToClock(self, a, b, c, d, e, f, beep, dots, test_clock = False, max_num_tries = 5):
        # pthread_mutex_lock (&clock_ack_mutex);

        # if(!(g_debugMode == DGTNIX_DEBUG_OFF))
        #   {
        #     _debug("Sending message to clock\n");
        #     if(g_descriptorDriverBoard < 0)
        #       {
        #         perror("dgtnix critical:sendMessageToBoard: invalid file descriptor\n");
        #         exit(-1);
        #       }
        #   }
        print "Sending Message to Clock.."
        # num_tries = 0
        # self.clock_queue.empty()
        # self.dgt_clock_ack_lock.acquire()
        # while not self.clock_ack_recv:
        #     num_tries += 1
        #     if num_tries > 1:
        #         time.sleep(1) # wait a bit longer for ack
        #         if self.clock_ack_recv:
        #             break
        self.ser.write(chr(_DGTNIX_CLOCK_MESSAGE))
        self.ser.write(chr(0x0b))
        self.ser.write(chr(0x03))
        self.ser.write(chr(0x01))
        self.ser.write(chr(c))
        self.ser.write(chr(b))
        self.ser.write(chr(a))
        self.ser.write(chr(f))
        self.ser.write(chr(e))
        self.ser.write(chr(d))

        if dots:
            self.ser.write(chr(dots))
        else:
            self.ser.write(chr(0))
        if beep:
            self.ser.write(chr(0x03))
        else:
            self.ser.write(chr(0x01))
        self.ser.write(chr(0x00))

        # if test_clock:
        #     time.sleep(5)

            # time.sleep(1)
            # if num_tries>1:
            #     print "try : {0}".format(num_tries)

            # if self.dgt_clock and num_tries>=5:
            #     break
            # if num_tries>=max_num_tries:
            #     break
        # if not test_clock:

        # Retry logic?
        # time.sleep(1)
        # Check clock ack?


    def read_message_from_board(self, head=None):
        # print "acquire"
        # self.dgt_clock_ack_lock.acquire()
        print "got DGT message"
        header_len = 3
        if head:
            header = head + self.read(header_len-1)
        else:
            header = self.read(header_len)
        if not header:
            # raise
            raise Exception("Invalid First char in message")
        pattern = '>'+'B'*header_len
        buf = unpack(pattern, header)
#        print buf
#        print buf[0] & 128
#        if not buf[0] & 128:
#            raise Exception("Invalid message -2- readMessageFromBoard")
        command_id = buf[0] & 127
        print "command_id: {0}".format(command_id)
#
#        if buf[1] & 128:
#            raise Exception ("Invalid message -4- readMessageFromBoard")
#
#        if buf[2] & 128:
#            raise Exception ("Invalid message -6- readMessageFromBoard")

        message_length = (buf[1] << 7) + buf[2]
        message_length-=3

#        if command_id == _DGTNIX_NONE:
#            print "Received _DGTNIX_NONE from the board\n"
#            message = self.ser.read(message_length)

        if command_id == _DGTNIX_BOARD_DUMP:
            print "Received DGTNIX_DUMP message\n"
            message = self.read(message_length)
#            self.dump_board(message)
#            print self.get_fen(message)
            self.fire(type=FEN, message=self.get_fen(message))
            self.fire(type=BOARD, message=self.dump_board(message))

        elif command_id == _DGTNIX_BWTIME:
            print "Received DGTNIX_BWTIME message from the board\n"
            message = self.read(message_length)

            pattern = '>'+'B'*message_length
            buf = unpack(pattern, message)
            # print buf

            if buf:
                if buf[0] == buf[1] == buf[2] == buf[3] == buf[4] == buf[5] == 0:
                    self.fire(type=CLOCK_LEVER, message=buf[6])
                if buf[0] == 10 and buf[1] == 16 and buf[2] == 1 and buf[3] == 10 and not buf[4] and not buf[5] and not buf[6]:
                    # print "clock ACK received!"

                    # self.clock_ack_recv = True
                    # self.dgt_clock_ack_lock.acquire()
                    # self.clock_queue.get()
                    # self.clock_queue.task_done()
                    if not self.dgt_clock:
                        self.dgt_clock = True
                    self.fire(type=CLOCK_ACK, message='')
                if 5 <= buf[4] <= 6 and buf[5] == 49:
                    self.fire(type=CLOCK_BUTTON_PRESSED, message=0)

                if 33 <= buf[4] <= 34 and buf[5] == 52:
                    self.fire(type=CLOCK_BUTTON_PRESSED, message=1)

                if 17 <= buf[4] <= 18 and buf[5] == 51:
                    self.fire(type=CLOCK_BUTTON_PRESSED, message=2)

                if 9 <= buf[4] <= 10 and buf[5] == 50:
                    self.fire(type=CLOCK_BUTTON_PRESSED, message=3)

                if 65 <= buf[4] <= 66 and buf[5] == 53:
                    self.fire(type=CLOCK_BUTTON_PRESSED, message=4)


        elif command_id == _DGTNIX_EE_MOVES:
            print "Received _DGTNIX_EE_MOVES from the board\n"

        elif command_id == _DGTNIX_BUSADDRESS:
            print "Received _DGTNIX_BUSADDRESS from the board\n"

        elif command_id == _DGTNIX_SERIALNR:
            print "Received _DGTNIX_SERIALNR from the board\n"
            message = self.read(message_length)

        elif command_id == _DGTNIX_TRADEMARK:
            print "Received _DGTNIX_TRADEMARK from the board\n"
            message = self.read(message_length)

        elif command_id == _DGTNIX_VERSION:
            print "Received _DGTNIX_VERSION from the board\n"

        elif command_id == _DGTNIX_FIELD_UPDATE:
            print "Received _DGTNIX_FIELD_UPDATE from the board"
            print "message_length : {0}".format(message_length)

            if message_length == 2:
                message = self.read(message_length)
                self.write(chr(_DGTNIX_SEND_BRD))
            else:
                message = self.read(4)

#            pattern = '>'+'B'*message_length
#            buf = unpack(pattern, message)
#            print buf[0]
#            print buf[1]

        else:
            # Not a regular command id
            # Piece remove/add codes?

#            header = header + self.ser.read(1)
#            print "message_length : {0}".format(len(header))
#            print [header]
            #message[0] = code;
            #message[1] = intern_column;
            #message[2] = intern_line;
            #message[3] = piece;

#            print "diff command : {0}".format(command_id)

            if command_id == DGTNIX_MSG_MV_ADD:
                print "Add piece message"
#                board.ser.write(chr(_DGTNIX_SEND_BRD))

            elif command_id == DGTNIX_MSG_UPDATE:
                print "Update piece message"
#                board.ser.write(chr(_DGTNIX_SEND_BRD))

    # Warning, this method must be in a thread
    def poll(self):
        while True:
            c = self.read(1)
            # print "got msg"
            if c:
                self.read_message_from_board(head=c)

    def _dgt_observer(self, attrs):
        if attrs.type == FEN:
            print "FEN: {0}".format(attrs.message)
        elif attrs.type == BOARD:
            print "Board: "
            print attrs.message
            # self.send_message_to_clock(['c','h','a','n','g','e'], False, False)
            # time.sleep(1)
            # self.send_message_to_clock(['b','o','a','r','d','c'], False, False)


class VirtualDGTBoard(DGTBoard):
    def __init__(self, device, virtual = True):
        super(VirtualDGTBoard, self).__init__(device, virtual = virtual)
        self.fen = None
        self.callbacks = []

    def read(self, bits):
        if self.fen:
            return True

    def read_message_from_board(self, head = None):
        fen = self.fen
        self.fen = None
        return self.fire(type=FEN, message = fen)

    def write(self, message):
        if message == chr(_DGTNIX_SEND_UPDATE_NICE):
            print "Got Update Nice"
        elif message == chr(_DGTNIX_SEND_BRD):
            print "Got Send board"

    def set_fen(self, fen):
        self.fen = fen


def poll_dgt(dgt):
    thread = Thread(target=dgt.poll)
    thread.start()

if __name__ == "__main__":
    if len(sys.argv)> 1:
        device = sys.argv[1]
    else:
        device = "/dev/cu.usbserial-00001004"
    board = DGTBoard(device, send_board=False)
    board.subscribe(board._dgt_observer)
    # poll_dgt(board)
    # if board.test_for_dgt_clock():
    #     print "Clock found!"
    # else:
    #     print "Clock not present"

    # board.send_message_to_clock(['a','y',' ','d','g', 't'], False, False)
    board.poll()
    # poll_dgt(board)




