# GPL v2 licence, Pierre Boulenguez 2007
import os
import sys
import select
import binascii
import socket
import os, os.path
import types
import time
import threading
from curses import ascii
import string
import array
import struct

init = "false"
gameExample = "s/600/600,e2e4,o,z/1,e7e5,o,z/1,g1f3,o,z/1,b8c6,o,z/1,f1b5,o,z/1,,o,z/1,a7a6,o,z/1,b5a4,o,z/1,g8f6,o,z/1,e1g1,o,z/1,h1f1,o,z/1,f8e7,o,z/1,f1e1,o,z/1,b7b5,o,z/1,a4b3,o,z/1,d7d6,o,z/1,c2c3,o,z/1,e8g8,o,z/1,h8f8,o,z/1,h2h3,o,z/1,c6b8,o,z/1,10,o,z/1,d2d4,o,z/1,b8d7,o,z/1,c3c4,o,z/1,c7c6,o,z/1,c4b5,o,z/1,a6b5,o,z/1,b1c3,o,z/1,c8b7,o,z/1,c1g5,o,z/1,b5b4,o,z/1,c3b1,o,z/1,h7h6,o,z/1,g5h4,o,z/1,c6c5,o,z/1,d4e5,o,z/1,f6e4,o,z/1,h4e7,o,z/1,d8e7,o,z/1,e5d6,o,z/1,e7f6,o,z/1,20,o,z/1,b1d2,o,z/1,e4d6,o,z/1,d2c4,o,z/1,d6c4,o,z/1,b3c4,o,z/1,d7b6,o,z/1,f3e5,o,z/1,a8e8,o,z/1,c4f7,o,z/1,f8f7,o,z/1,e5f7,o,z/1,e8e1,o,z/1,d1e1,o,z/1,g8f7,o,z/1,e1e3,o,z/1,f6g5,o,z/1,e3g5,o,z/1,h6g5,o,z/1,b2b3,o,z/1,f7e6,o,z/1,a2a3,o,z/1,e6d6,o,z/1,a3b4,o,z/1,c5b4,o,z/1,a1a5,o,z/1,b6d5,o,z/1,f2f3,o,z/1,b7c8,o,z/1,g1f2,o,z/1,c8f5,o,z/1,a5a7,o,z/1,g7g6,o,z/1,a7a6,o,z/1,d6c5,o,z/1,f2e1,o,z/1,d5f4,o,z/1,g2g3,o,z/1,f4h3,o,z/1,e1d2,o,z/1,c5b5,o,z/1,40,o,z/1,a6d6,o,z/1,b5c5,o,z/1,d6a6,o,z/1,h3f2,o,z/1,g3g4,o,z/1,f5d3,o,z/1,a6e6\n"
_DGTNIX_SEND_CLK = binascii.a2b_hex("41")
_DGTNIX_SEND_BRD = binascii.a2b_hex("42")
_DGTNIX_SEND_UPDATE = binascii.a2b_hex("43")
_DGTNIX_SEND_UPDATE_BRD = binascii.a2b_hex("44")
_DGTNIX_SEND_SERIALNR = binascii.a2b_hex("45")
_DGTNIX_SEND_BUSADDRESS = binascii.a2b_hex("46")
_DGTNIX_SEND_TRADEMARK = binascii.a2b_hex("47")
_DGTNIX_SEND_VERSION = binascii.a2b_hex("4d")
_DGTNIX_SEND_UPDATE_NICE = binascii.a2b_hex("4b")
_DGTNIX_SEND_EE_MOVES = binascii.a2b_hex("49")
_DGTNIX_SEND_RESET = binascii.a2b_hex("40")

_DGTNIX_NONE = binascii.a2b_hex("00")
## ALL FOLLOWING MESSAGES ARE BINARY & TO 128 !!
_DGTNIX_BOARD_DUMP = binascii.a2b_hex("86")
_DGTNIX_BWTIME = binascii.a2b_hex("8d")
_DGTNIX_FIELD_UPDATE = binascii.a2b_hex("8e")
_DGTNIX_EE_MOVES = binascii.a2b_hex("8f")
_DGTNIX_BUSADDRESS = binascii.a2b_hex("90")
_DGTNIX_SERIALNR = binascii.a2b_hex("91")
_DGTNIX_TRADEMARK = binascii.a2b_hex("92")
_DGTNIX_VERSION = binascii.a2b_hex("93")

_DGTNIX_EMPTY = binascii.a2b_hex("00")
_DGTNIX_WPAWN = binascii.a2b_hex("01")
_DGTNIX_WROOK = binascii.a2b_hex("02")
_DGTNIX_WKNIGHT = binascii.a2b_hex("03")
_DGTNIX_WBISHOP = binascii.a2b_hex("04")
_DGTNIX_WKING = binascii.a2b_hex("05")
_DGTNIX_WQUEEN = binascii.a2b_hex("06")
_DGTNIX_BPAWN = binascii.a2b_hex("07")
_DGTNIX_BROOK = binascii.a2b_hex("08")
_DGTNIX_BKNIGHT = binascii.a2b_hex("09")
_DGTNIX_BBISHOP = binascii.a2b_hex("0a")
_DGTNIX_BKING = binascii.a2b_hex("0b")
_DGTNIX_BQUEEN = binascii.a2b_hex("0c")

_DGTNIX_CLOCK_MESSAGE_HEADER = binascii.a2b_hex("2b")
_DGTNIX_CLOCK_MESSAGE_FIRST_BIT = binascii.a2b_hex("0b")
_DGTNIX_CLOCK_MESSAGE_SECOND_BIT = binascii.a2b_hex("03")
_DGTNIX_CLOCK_MESSAGE_THIRD_BIT = binascii.a2b_hex("01")
_DGTNIX_CLOCK_MESSAGE_10 = binascii.a2b_hex("10")
_DGTNIX_CLOCK_MESSAGE_16 = binascii.a2b_hex("16")
_DGTNIX_CLOCK_ACK = binascii.a2b_hex("0a")


def timeMessageThread(client, lock):
    global clockon
    global wtime
    global btime
    global wturn
    second = False

    # Should send clock ack (if needed) and time messages

    while True:
        try:
            #            time.sleep(1)
            data = client.recv(1)
            manageClockMessage(client, data)
        #            lock.acquire()
        #            sendTimeMessage(client, clockon, wtime, btime, wturn)
        #            if second == True:
        #                if wturn:
        #                    wtime -= 1
        #                else:
        #                    btime -= 1
        #                if wtime < 0:
        #                    wtime = 0
        #                if btime < 0:
        #                    btime = 0
        #                second = False
        #            else:
        #                second = True
        #            lock.release()
        except socket.error:
            print("")
            print("client closed, press enter to quit")
            clockon = "end"


# not yet safe, obviously :)
def safesend(client, message):
    client.send(message)


def initBoard():
    board = array.array("c")
    for i in range(64):
        board.append(_DGTNIX_EMPTY)
    return board


def convertStrangeCharValue(v):
    s = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
    25, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41,
    42, 43, 44, 45, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 50, 51, 52, 53, 54, 55, 56, 57, 58,
    59, 60, 61, 62, 63, 64, 65, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 70, 71, 72, 73, 74, 75,
    76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 90, 91, 92,
    93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    111, 112, 113, 114, 115, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 120, 121,
    122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 130, 131, 132, 133, 134, 135, 136, 137, 138,
    139, 140, 141, 142, 143, 144, 145, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155,
    150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165)
    for i in range(0, 255):
        if s[i] == v:
            return i


def setPiece(board, line, column, piece):
    board[(line - 1) * 8 + column - 1] = piece


def getPiece(board, line, column):
    return board[(line - 1) * 8 + column - 1]


def printBoard(board):
    pr = "   A B C D E F G H\n"
    for i in range(64):
        if (i % 8) == 0 and i != 0:
            pr += "|\n"
        if i % 8 == 0:
            pr += str(8 - i / 8)
            pr += " "
        c, d = pieceToChar(board[i])
        pr += "|%c" % c
    pr += "|\n"
    sys.stdout.write(pr)


def waitForInitialisationMessages(client):
    while init == "false":
        try:
            data = client.recv(1)
            manageMessage(client, data)

        except socket.error:
            print("client closed")
            return


def secondsToHMS(seconds):
    return (seconds / 3600, (seconds % 3600) / 60, (seconds % 3600) % 60)


def convertToTimeFormat(value):
    value = (value << 4) / 10
    return value


def sendTimeMessage(client, clockon, wtime, btime, wturn):
    (bhour, bmin, bsecond) = secondsToHMS(btime)
    (whour, wmin, wsecond) = secondsToHMS(wtime)
    bhour = convertStrangeCharValue(bhour)
    bmin = convertStrangeCharValue(bmin)
    bsecond = convertStrangeCharValue(bsecond)
    whour = convertStrangeCharValue(whour)
    wmin = convertStrangeCharValue(wmin)
    wsecond = convertStrangeCharValue(wsecond)
    # print "sending time message %d:%d:%d %d:%d:%d" % (whour, wmin, wsecond, bhour, bmin, bsecond)
    safesend(client, _DGTNIX_BWTIME)
    safesend(client, chr(0))
    safesend(client, chr(10))
    safesend(client, chr(bhour))
    safesend(client, chr(bmin))
    safesend(client, chr(bsecond))
    safesend(client, chr(0))
    safesend(client, chr(wmin))
    safesend(client, chr(wsecond))
    if not clockon:
        safesend(client, chr(0))
    elif wturn == True:
        safesend(client, chr(1))
    else:
        safesend(client, chr(255))
    btime -= 1
    wtime -= 1
    if wturn == True:
        wturn = False
    else:
        wturn = True


def int2byte(i):
    return struct.pack("!B", i)


def manageClockMessage(client, data):
    if data == _DGTNIX_CLOCK_MESSAGE_HEADER:
        #        print "Got a clock message"
        # Handling a clock message
        first_bit = client.recv(1)
        second_bit = client.recv(1)
        third_bit = client.recv(1)
        assert first_bit == _DGTNIX_CLOCK_MESSAGE_FIRST_BIT
        assert second_bit == _DGTNIX_CLOCK_MESSAGE_SECOND_BIT
        assert third_bit == _DGTNIX_CLOCK_MESSAGE_THIRD_BIT

        message = []

        for i in range(6):
            message.append(convertLCDToChar(client.recv(1)))

        # For some (obscure?) reason, these bits must be swapped for the DGT XL clock
        message[0], message[2] = message[2], message[0]
        message[3], message[5] = message[5], message[3]

        for i in range(3):
            client.recv(1)

        print("Clock message received: [%s] " % message)
        client.send(_DGTNIX_BWTIME)
        client.send(_DGTNIX_NONE)

        client.send(_DGTNIX_CLOCK_MESSAGE_10)
        client.send(_DGTNIX_WPAWN)
        client.send(_DGTNIX_CLOCK_MESSAGE_10)
        client.send(_DGTNIX_NONE)
        client.send(_DGTNIX_CLOCK_ACK)
        client.send(_DGTNIX_NONE)


def convertLCDToChar(b):
    lcd_char_map = {0x01 | 0x02 | 0x20 | 0x08 | 0x04 | 0x10: '0',
                    0x02 | 0x04: '1',
                    0x01 | 0x40 | 0x08 | 0x02 | 0x10: '2',
                    0x01 | 0x40 | 0x08 | 0x02 | 0x04: '3',
                    0x20 | 0x04 | 0x40 | 0x02: '4',
                    0x01 | 0x40 | 0x08 | 0x20 | 0x04: '5',
                    0x01 | 0x40 | 0x08 | 0x20 | 0x04 | 0x10: '6',

                    0x02 | 0x04 | 0x01: '7',
                    0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10 | 0x08: '8',
                    0x01 | 0x40 | 0x08 | 0x02 | 0x04 | 0x20: '9',
                    0x01 | 0x02 | 0x20 | 0x40 | 0x04 | 0x10: 'a',
                    0x20 | 0x04 | 0x40 | 0x08 | 0x10: 'b',
                    0x01 | 0x20 | 0x10 | 0x08: 'c',
                    0x10 | 0x40 | 0x08 | 0x02 | 0x04: 'd',
                    0x01 | 0x40 | 0x08 | 0x20 | 0x10: 'e',
                    0x01 | 0x40 | 0x20 | 0x10: 'f',
                    0x01 | 0x20 | 0x10 | 0x08 | 0x04: 'g',
                    0x20 | 0x10 | 0x04 | 0x40: 'h',
                    0x02 | 0x04: 'i',
                    0x02 | 0x04 | 0x08 | 0x10: 'j',
                    0x01 | 0x20 | 0x40 | 0x04 | 0x10: 'k',
                    0x20 | 0x10 | 0x08: 'l',
                    0x01 | 0x40 | 0x04 | 0x10: 'm',
                    0x40 | 0x04 | 0x10: 'n',
                    0x40 | 0x04 | 0x10 | 0x08: 'o',
                    0x01 | 0x40 | 0x20 | 0x10 | 0x02: 'p',
                    0x01 | 0x40 | 0x20 | 0x04 | 0x02: 'q',
                    0x40 | 0x10: 'r',
                    0x01 | 0x40 | 0x08 | 0x20 | 0x04: 's',
                    0x20 | 0x10 | 0x08 | 0x40: 't',
                    0x08 | 0x02 | 0x20 | 0x04 | 0x10: 'u',
                    0x08 | 0x02 | 0x20: 'v',
                    0x40 | 0x08 | 0x20 | 0x02: 'w',
                    0x20 | 0x10 | 0x04 | 0x40 | 0x02: 'x',
                    0x20 | 0x08 | 0x04 | 0x40 | 0x02: 'y',
                    0x01 | 0x40 | 0x08 | 0x02 | 0x10: 'z'}
    if ord(b) in lcd_char_map:
        return lcd_char_map[ord(b)]
    return ' '


def manageMessage(client, data):
    message = ""
    global init
    if data != "":
        if data == _DGTNIX_SEND_BRD:
            message = "received DGTNIX_SEND_BRD"
            safesend(client, _DGTNIX_BOARD_DUMP)
            safesend(client, _DGTNIX_NONE)
            safesend(client, binascii.a2b_hex("43"))
            # the board is initially set to be empty
            for x in range(64):
                safesend(client, _DGTNIX_EMPTY)
        elif data == _DGTNIX_SEND_UPDATE_BRD:
            message = "received DGTNIX_SEND_UPDATE_BRD"
            sys.exit()
        elif data == _DGTNIX_SEND_SERIALNR:
            message = "received DGTNIX_SEND_SERIALNR"
            safesend(client, _DGTNIX_SERIALNR)
            safesend(client, _DGTNIX_NONE)
            safesend(client, binascii.a2b_hex("06"))
            safesend(client, '0')
            safesend(client, '.')
            safesend(client, '0')
        elif data == _DGTNIX_SEND_BUSADDRESS:
            message = "received DGTNIX_SEND_BUSADDRESS"
            safesend(client, _DGTNIX_BUSADDRESS)
            safesend(client, _DGTNIX_NONE)
            safesend(client, binascii.a2b_hex("05"))
            safesend(client, binascii.a2b_hex("00"))
            safesend(client, binascii.a2b_hex("00"))
        elif data == _DGTNIX_SEND_TRADEMARK:
            message = "received DGTNIX_SEND_TRADEMARK"
            safesend(client, _DGTNIX_TRADEMARK)
            safesend(client, _DGTNIX_NONE)
            trademark = "dgtnix virtual board, http://dgtnix.sourceforge.net/"
            safesend(client, chr(len(trademark) + 3))
            safesend(client, trademark)
        elif data == _DGTNIX_SEND_VERSION:
            message = "received DGTNIX_SEND_VERSION"
            safesend(client, _DGTNIX_VERSION)
            safesend(client, _DGTNIX_NONE)
            safesend(client, binascii.a2b_hex("05"))
            safesend(client, binascii.a2b_hex("00"))
            safesend(client, binascii.a2b_hex("00"))
        elif data == _DGTNIX_SEND_UPDATE_NICE:
            message = "received DGTNIX_SEND_UPDATE_NICE"
        elif data == _DGTNIX_SEND_RESET:
            message = "received DGTNIX_SEND_RESET"
        elif data == _DGTNIX_SEND_UPDATE:
            print("received DGTNIX_SEND_UPDATE")
            init = "true"

        ####################This message are not handled by dgtnix !
        elif data == _DGTNIX_SEND_EE_MOVES:
            print("received DGTNIX_SEND_EE_MOVES")
            print("this message is not handled by dgtnix")
            sys.exit()
        elif data == _DGTNIX_SEND_CLK:
            print("received DGTNIX_SEND_CLK")
            print("this message is not handled by dgtnix")
            sys.exit()
        else:
            message = "unrecognized message from dgtnix:%c" % data  #
            print(message)
            sys.exit()


def pieceToChar(piece):
    if piece == _DGTNIX_WPAWN:
        return 'P', "white pawn"
    elif piece == _DGTNIX_WROOK:
        return 'R', "white rook"
    elif piece == _DGTNIX_WKNIGHT:
        return 'N', "white knight"
    elif piece == _DGTNIX_WBISHOP:
        return 'B', "white bishop"
    elif piece == _DGTNIX_WKING:
        return 'K', "white king"
    elif piece == _DGTNIX_WQUEEN:
        return 'Q', "white queen"
    elif piece == _DGTNIX_BPAWN:
        return 'p', "black pawn"
    elif piece == _DGTNIX_BROOK:
        return 'r', "black rook"
    elif piece == _DGTNIX_BKNIGHT:
        return 'n', "black knight"
    elif piece == _DGTNIX_BBISHOP:
        return 'b', "black bishop"
    elif piece == _DGTNIX_BKING:
        return 'k', "black king"
    elif piece == _DGTNIX_BQUEEN:
        return 'q', "black queen"
    elif piece == _DGTNIX_EMPTY:
        return ' ', "empty"
    else:
        return 0, "error"


def toColumnLine(c, l):
    if ascii.isalpha(c) == False:
        print("invalid column")
        return -1, -1
    if ascii.isupper(c):
        cColumn = c.lower()
    else:
        cColumn = c
    column = ord(cColumn) - ord('a')
    if column < 0 or column > 7:
        print("invalid column")
        return -1, -1
    if ascii.isdigit(l) == False:
        print("invalid line")
        return -1, -1
    line = int(l) - 1
    line = 7 - line
    if line < 0 or line > 7:
        print("invalid line")
        return -1, -1
    return column, line


def charToPiece(char):
    if char == 'P':
        return _DGTNIX_WPAWN, "white pawn"
    elif char == 'R':
        return _DGTNIX_WROOK, "white rook"
    elif char == 'N':
        return _DGTNIX_WKNIGHT, "white knight"
    elif char == 'B':
        return _DGTNIX_WBISHOP, "white bishop"
    elif char == 'K':
        return _DGTNIX_WKING, "white king"
    elif char == 'Q':
        return _DGTNIX_WQUEEN, "white queen"
    elif char == 'p':
        return _DGTNIX_BPAWN, "black pawn"
    elif char == 'r':
        return _DGTNIX_BROOK, "black rook"
    elif char == 'n':
        return _DGTNIX_BKNIGHT, "black knight"
    elif char == 'b':
        return _DGTNIX_BBISHOP, "black bishop"
    elif char == 'k':
        return _DGTNIX_BKING, "black king"
    elif char == 'q':
        return _DGTNIX_BQUEEN, "black queen"
    elif char == 'd' or char == 'D':
        return _DGTNIX_EMPTY, "nothing"
    else:
        return 0, "error"


def manageStandardMove(c, board):
    if len(c) != 4:
        print("invalid command :%s " % c)
        return 0
    column_i, line_i = toColumnLine(c[0], c[1])
    if column_i == -1:
        return 0
    column_f, line_f = toColumnLine(c[2], c[3])
    if column_f == -1:
        return 0
    if getPiece(board, line_i + 1, column_i + 1) == _DGTNIX_EMPTY:
        print("move piece from %c%c impossible, the square is empty" % (c[0], c[1]))
        return 0
    piece = getPiece(board, line_i + 1, column_i + 1)
    msgRemove = "t" + chr(ord('a') + column_i) + str(8 - line_i)
    if manageRemovePiece(msgRemove, board) == 0:
        return 0

    if getPiece(board, line_f + 1, column_f + 1) != _DGTNIX_EMPTY:
        msgRemove = "t" + chr(ord('a') + column_f) + str(8 - line_f)
        manageRemovePiece(msgRemove, board)

    piece, s = pieceToChar(piece)
    msgAdd = piece + chr(ord('a') + column_f) + str(8 - line_f)
    manageAddPiece(msgAdd, board)
    return 1


def manageRemovePiece(c, board):
    if len(c) != 3:
        print("invalid command")
        return 0
    column, line = toColumnLine(c[1], c[2])
    if column == -1:
        return 0
    position = column + line * 8
    if getPiece(board, line + 1, column + 1) == _DGTNIX_EMPTY:
        print("cannot take piece from %c%c, the square is empty" % (c[1], c[2]))
        return 1
    piece, sPiece = pieceToChar(getPiece(board, line + 1, column + 1))
    print("Removing %s from %c%c" % (sPiece, c[1], c[2]))
    safesend(client, _DGTNIX_FIELD_UPDATE)
    safesend(client, _DGTNIX_NONE)
    safesend(client, chr(5))
    safesend(client, chr(position))
    safesend(client, _DGTNIX_EMPTY)
    setPiece(board, line + 1, column + 1, _DGTNIX_EMPTY)
    return 1


def manageAddPiece(c, board):
    if len(c) != 3:
        print("invalid command")
        return 0
    piece, sPiece = charToPiece(c[0])
    if piece == 0:
        print("invalid piece")
        return 0
    column, line = toColumnLine(c[1], c[2])
    if column == -1:
        return 0

    position = column + line * 8
    if getPiece(board, line + 1, column + 1) != _DGTNIX_EMPTY:
        print("cannot add piece on %c%c, the square is not empty!" % (c[1], c[2]))
        return 2, column, line
    print("Adding %s on %c%c" % (sPiece, c[1], c[2]))
    safesend(client, _DGTNIX_FIELD_UPDATE)
    safesend(client, _DGTNIX_NONE)
    safesend(client, chr(5))
    safesend(client, chr(position))
    safesend(client, piece)
    setPiece(board, line + 1, column + 1, piece)
    return 1


filename = ""
print("**************************")
print("* dgtnix virtual board   *")
print("**************************")
if len(sys.argv) == 1:
    filename = "/tmp/dgtnixBoard"
    print("Using default filename for socket(%s)" % filename)
    print("(you can change it by passing the filename as first argument)")
    print("Use this name as the port for the dgtnixInit(const char *port) function")
elif len(sys.argv) == 2:
    filename = sys.argv[1]
    print("using %s filename for socket" % sys.argv[1])
else:
    print("usage:%s <exchangeFile>" % sys.argv[0])
    sys.exit()

if os.path.exists(filename):
    os.remove(filename)
try:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(filename)
except socket.error as msg:
    # print "open->I/O error(%s): %s" % (errno, strerror)
    print('open->I/O error(%s)', msg)
    if os.path.exists(filename):
        os.remove(filename)
    sys.exit()

sock.listen(1)
while 1:
    print("Waiting for a client to connect on %s (Ctrl-c to quit)" % filename)
    (client, address) = sock.accept()
    print("*Connected*")
    board = initBoard()
    waitForInitialisationMessages(client)
    clockon = False

    #    clockAckNeeded = False

    btime = 10000
    wtime = 1000
    wturn = True
    # lock=thread.allocate_lock()
    # thread.start_new_thread(timeMessageThread, (client, lock, ))
    lock = threading.Lock
    x = threading.Thread(timeMessageThread, (client, lock,)).setDaemon(True).start()
    lock = x.lock

    savedCommands = ""
    print("command mode(h for help)")
    try:
        while 1:
            sys.stdout.write("command:")
            c = sys.stdin.readline()
            c = c.strip('\n')
            if c == "start":
                c = "Rh1, Ng1, Bf1, Ke1, Qd1, Bc1, Nb1, Ra1,"
                c += "Ph2, Pg2, Pf2, Pe2, Pd2, Pc2, Pb2, Pa2,"
                c += "rh8, ng8, bf8, ke8, qd8, bc8, nb8, ra8,"
                c += "ph7, pg7, pf7, pe7, pd7, pc7, pb7, pa7"
            elif c == "setup":
                c = "Qa1,Qh1"
            elif c == "clear":
                board = initBoard()
                continue
            elif c == "custom":
                c = "Kg2, kg7,Pg3,ta1,th1"
            for command in c.split(','):
                if clockon == "end":
                    sys.exit(1)

                command = command.strip()
                result = 1
                if command == "":
                    continue
                if command == "quit" or command == "q":
                    print("bye")
                    client.close()
                    sys.exit()
                elif command == "help" or command == "h" or command == "?":
                    print("Here is a list of the implemented commands :")
                    print("   -h or help or ? : display this help")
                    print("   -q or quit : quit")
                    print("   -d or display : display the board")
                    print("   -c or commands : display previous commands")
                    print("   -add piece simply by typing the piece and the square")
                    print("     white pieces :K,Q,R,B,N,P")
                    print("     black pieces :k,q,r,b,n,p")
                    print("     the square notation (as for example a8) is case independant")
                    print("     example, Qa8 add a white queen on a8 (if the square is free)")
                    print("   -t : take/remove a piece followed square ")
                    print("     ta4 remove piece from a4 if exists example")
                    print("   -e2e4 : you can append move in the standard form ")
                    print("          a piece 'take' will be generated and  ")
                    print("          a second if the destination square is not empty ")
                    print("          and then a piece add")
                    print("   -s/whitetime/blacktime or swatch/whitetime/blacktime")
                    print("     turn the clock on with times whitetime and blacktime")
                    print("     or turn the clock off if the clock was on (in this case ")
                    print("     whitetime and blacktime are obviously facultatives")
                    print("     example: s/600/1200 start the clock with white time 10 minutes")
                    print("     and black time 20 minutes")
                    print("     time values are integers in seconds !!")
                    print("   -o or otherplayer")
                    print("     simulate a push on the clock button")
                    print("     if it was white's turns, then it is now black's turns and")
                    print("     reciprocally")
                    print("   -z/time or zzz/time")
                    print("    simply sleep for time seconds")
                    print("    time value is real number in seconds !!")
                    print("")
                    print("You can combine multiple commands by separating them with comma")
                    print("For example you can generate an initial position by typing :")
                    sys.stdout.write("Rh1, Ng1, Bf1, Ke1, Qd1, Bc1, Nb1, Ra1,")
                    sys.stdout.write("Ph2, Pg2, Pf2, Pe2, Pd2, Pc2, Pb2, Pa2,")
                    sys.stdout.write("rh8, ng8, bf8, ke8, qd8, bc8, nb8, ra8,")
                    sys.stdout.write("ph7, pg7, pf7, pe7, pd7, pc7, pb7, pa7\n")
                    print("and you can even simulate a real game (here Fischer/Spassky 1992.11.04)")
                    print("by issuing such commands :")
                    sys.stdout.write(gameExample)
                    print("Note that at the connection, the virtual board is clear of any piece.")
                elif command == "display" or command == "d":
                    printBoard(board)
                elif command == "commands" or command == "c":
                    print(savedCommands)
                    continue
                elif command.startswith("swatch") or command[0] == "s":
                    lock.acquire()
                    if clockon == True:
                        clockon = False
                        print("clock off")
                    else:
                        wtime = int(command.split('/')[1])
                        btime = int(command.split('/')[2])
                        clockon = True
                        wturn = True
                        print("clock set to on, white player, times :%ds / %ds" % (wtime, btime))
                    lock.release()
                elif command == "otherplayer" or command == "o":
                    lock.acquire()
                    if wturn == True:
                        print("changed player's turn to black's turn")
                        wturn = False
                    else:
                        print("changed player's turn to white's turn")
                        wturn = True
                    lock.release()
                elif command.startswith("zzz") or command[0] == "z":
                    print("sleeping for %1.2f seconds" % float(command.split('/')[1]))
                    time.sleep(float(command.split('/')[1]))
                elif len(command) == 4:
                    lock.acquire()
                    result = manageStandardMove(command, board)
                    lock.release()
                elif command[0] == 't':
                    lock.acquire()
                    result = manageRemovePiece(command, board)
                    lock.release()
                else:
                    lock.acquire()
                    result = manageAddPiece(command, board)
                    lock.release()
                if result == 1:
                    if savedCommands == "":
                        savedCommands = command
                    else:
                        savedCommands = savedCommands + "," + command
    except (KeyboardInterrupt, SystemExit):
        client.close()
        if os.path.exists(filename):
            os.remove(filename)
        sys.exit()
