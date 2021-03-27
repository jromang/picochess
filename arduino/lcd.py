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

# for this (picotalker) to work you need to run these commands (if you haven't done before)
# apt-get install vorbis-tools
# apt-get install sox

import threading
import logging
import subprocess
import queue
from pathlib import Path
from shutil import which
import requests
import chess
import time
from utilities import DisplayMsg
from utilities import get_relevant_usb_devices
from timecontrol import TimeControl
from dgt.api import Message
from dgt.util import GameResult, PlayMode, Voice
from dgt.api import Dgt, Event, Message
from utilities import DisplayMsg, Observable
from nanpy import SerialManager
from nanpy.lcd import Lcd


class ArduinoDisplay(DisplayMsg, threading.Thread):

    """Listen on messages for talking."""

    USER = 'user'
    COMPUTER = 'computer'
    SYSTEM = 'system'

    def __init__(self, picochess_version):
        """
        Initialize a PicoTalkerDisplay with voices for the user and/or computer players.

        :param user_voice: The voice to use for the user (eg. en:al).
        :param computer_voice: The voice to use for the computer (eg. en:christina).
        """
        super(ArduinoDisplay, self).__init__()
        self.picochess_version = picochess_version

    def set_computer(self, picotalker):
        """Set the computer talker."""
        self.computer_picotalker = picotalker

    def set_user(self, picotalker):
        """Set the user talker."""
        self.user_picotalker = picotalker

    def set_factor(self, speed_factor):
        """Set speech factor."""
        if self.computer_picotalker:
            self.computer_picotalker.set_speed_factor(speed_factor)
        if self.user_picotalker:
            self.user_picotalker.set_speed_factor(speed_factor)

    def display(self, text, dev=SYSTEM):

        print("got text: {}".format(text[0]))

        if self.lcd:
            with self.lcd_lock:

                self.lcd.printString("                ", 0, 0)
                self.lcd.printString("                ", 0, 1)
                for t in text:
                    self.lcd.printString(t, 0, 0)

    def run(self):
        """Start listening for Messages on our queue and generate speech as appropriate."""
        previous_move = chess.Move.null()  # Ignore repeated broadcasts of a move
        logging.info('msg_queue ready')
        self.lcd_lock = threading.RLock()
        self.lcd = None
        if not self.lcd:
            try:
                with self.lcd_lock:
                    relevant_usb_devices = get_relevant_usb_devices()
                    if "ARDUINO_LCD" in relevant_usb_devices:
                        arduino_lcd_device = relevant_usb_devices["ARDUINO_LCD"]
                        connection = SerialManager(device=arduino_lcd_device)
                        self.lcd = Lcd([8, 9, 4, 5, 6, 7], [16, 2], connection=connection)
                        logging.error("Arduino Uno R3 LCD Found!!")
                    else:
                        raise Exception("Arduino Device Not Auto-detected via USB")
                # time.sleep(1)
            except Exception as e:
                logging.error(e)
                return

        while True:

            try:
                # Check if we have something to say
                message = self.msg_queue.get()

                if False:  # switch-case
                    pass
                elif isinstance(message, Message.ENGINE_FAIL):
                    logging.debug('announcing ENGINE_FAIL')
                    self.display(['error'])

                elif isinstance(message, Message.START_NEW_GAME):
                    if message.newgame:
                        logging.debug('announcing START_NEW_GAME')
                        self.display(['New Game'])
                        self.play_game = None

                elif isinstance(message, Message.COMPUTER_MOVE):
                    if message.move and message.game and message.move != previous_move:
                        logging.debug('announcing COMPUTER_MOVE [%s]', message.move)
                        game_copy = message.game.copy()
                        game_copy.push(message.move)
                        last_san_move = self.get_last_move_san(game_copy)
                        self.display([last_san_move])
                        previous_move = message.move
                        self.play_game = game_copy

                elif isinstance(message, Message.COMPUTER_MOVE_DONE):
                    self.play_game = None

                elif isinstance(message, Message.USER_MOVE_DONE):
                    if message.move and message.game and message.move != previous_move:
                        logging.debug('announcing USER_MOVE_DONE [%s]', message.move)
                        # game_copy = message.game.copy()
                        # game_copy.push(message.move)
                        last_san_move = self.get_last_move_san(message.game)
                        self.display([last_san_move])
                        # self.display([message.move])
                        previous_move = message.move
                        self.play_game = None

                elif isinstance(message, Message.REVIEW_MOVE_DONE):
                    if message.move and message.game and message.move != previous_move:
                        logging.debug('announcing REVIEW_MOVE_DONE [%s]', message.move)
                        last_san_move = self.get_last_move_san(message.game)
                        self.display([last_san_move])
                        # self.display([message.move])
                        previous_move = message.move
                        self.play_game = None  # @todo why thats not set in dgtdisplay?

                elif isinstance(message, Message.GAME_ENDS):
                    if message.result == GameResult.OUT_OF_TIME:
                        logging.debug('announcing GAME_ENDS/TIME_CONTROL')
                        wins = 'whitewins.ogg' if message.game.turn == chess.BLACK else 'blackwins.ogg'
                        self.display(['Time Loss'])
                    elif message.result == GameResult.INSUFFICIENT_MATERIAL:
                        logging.debug('announcing GAME_ENDS/INSUFFICIENT_MATERIAL')
                        self.display(['Insufficent Material', 'Draw'])
                    elif message.result == GameResult.MATE:
                        logging.debug('announcing GAME_ENDS/MATE')
                        self.display(['Checkmate'])
                    elif message.result == GameResult.STALEMATE:
                        logging.debug('announcing GAME_ENDS/STALEMATE')
                        self.display(['Stalemate'])
                    elif message.result == GameResult.ABORT:
                        logging.debug('announcing GAME_ENDS/ABORT')
                        self.display(['Abort'])
                    elif message.result == GameResult.DRAW:
                        logging.debug('announcing GAME_ENDS/DRAW')
                        self.display(['Draw'])
                    elif message.result == GameResult.WIN_WHITE:
                        logging.debug('announcing GAME_ENDS/WHITE_WIN')
                        self.display(['White wins'])
                    elif message.result == GameResult.WIN_BLACK:
                        logging.debug('announcing GAME_ENDS/BLACK_WIN')
                        self.display(['Black wins'])
                    elif message.result == GameResult.FIVEFOLD_REPETITION:
                        logging.debug('announcing GAME_ENDS/FIVEFOLD_REPETITION')
                        self.display(['repetition', 'draw'])

                elif isinstance(message, Message.TAKE_BACK):
                    logging.debug('announcing TAKE_BACK')
                    self.display(['takeback'])
                    self.play_game = None
                    previous_move = chess.Move.null()

                elif isinstance(message, Message.TIME_CONTROL):
                    logging.debug('announcing TIME_CONTROL')
                    self.display(['oktime'])

                elif isinstance(message, Message.INTERACTION_MODE):
                    logging.debug('announcing INTERACTION_MODE')
                    self.display(['okmode'])

                elif isinstance(message, Message.LEVEL):
                    if message.do_speak:
                        logging.debug('announcing LEVEL')
                        self.display(['oklevel'])
                    else:
                        logging.debug('dont announce LEVEL cause its also an engine message')

                elif isinstance(message, Message.OPENING_BOOK):
                    logging.debug('announcing OPENING_BOOK')
                    self.display(['okbook'])

                elif isinstance(message, Message.ENGINE_READY):
                    logging.debug('announcing ENGINE_READY')
                    self.display(['okengine'])

                elif isinstance(message, Message.PLAY_MODE):
                    logging.debug('announcing PLAY_MODE')
                    self.play_mode = message.play_mode
                    userplay = 'user is black' if message.play_mode == PlayMode.USER_BLACK else 'user is white'
                    self.display([userplay])

                elif isinstance(message, Message.STARTUP_INFO):
                    self.play_mode = message.info['play_mode']
                    logging.debug('announcing PICOCHESS')
                    self.display(['Picochess'])

                elif isinstance(message, Message.CLOCK_TIME):
                    self.low_time = message.low_time
                    if self.low_time:
                        logging.debug('time too low, disable voice - w: %i, b: %i', message.time_white,
                                      message.time_black)

                elif isinstance(message, Message.ALTERNATIVE_MOVE):
                    self.play_mode = message.play_mode
                    self.play_game = None

                elif isinstance(message, Message.SYSTEM_SHUTDOWN):
                    logging.debug('announcing SHUTDOWN')
                    self.display(['Goodbye'])

                elif isinstance(message, Message.SYSTEM_REBOOT):
                    logging.debug('announcing REBOOT')
                    self.display(['Please wait'])

                elif isinstance(message, Message.SET_VOICE):
                    self.speed_factor = (90 + (message.speed % 10) * 5) / 100
                    localisation_id_voice = message.lang + ':' + message.speaker
                    if message.type == Voice.USER:
                        self.set_user(ArduinoLCD(localisation_id_voice, self.speed_factor))
                    if message.type == Voice.COMP:
                        self.set_computer(ArduinoLCD(localisation_id_voice, self.speed_factor))
                    if message.type == Voice.SPEED:
                        self.set_factor(self.speed_factor)

                elif isinstance(message, Message.WRONG_FEN):
                    if self.play_game and self.setpieces_voice:
                        self.display(self.say_last_move(self.play_game), self.COMPUTER)

                else:  # Default
                    pass
            except queue.Empty:
                pass

    @staticmethod
    def get_last_move_san(game: chess.Board):
        bit_board = game.copy()
        move = bit_board.pop()
        san_move = bit_board.san(move)
        return san_move

    @staticmethod
    def say_last_move(game: chess.Board):
        """Take a chess.BitBoard instance and speaks the last move from it."""
        move_parts = {
            'K': 'king.ogg',
            'B': 'bishop.ogg',
            'N': 'knight.ogg',
            'R': 'rook.ogg',
            'Q': 'queen.ogg',
            'P': 'pawn.ogg',
            '+': '',
            '#': '',
            'x': 'takes.ogg',
            '=': 'promote.ogg',
            'a': 'a.ogg',
            'b': 'b.ogg',
            'c': 'c.ogg',
            'd': 'd.ogg',
            'e': 'e.ogg',
            'f': 'f.ogg',
            'g': 'g.ogg',
            'h': 'h.ogg',
            '1': '1.ogg',
            '2': '2.ogg',
            '3': '3.ogg',
            '4': '4.ogg',
            '5': '5.ogg',
            '6': '6.ogg',
            '7': '7.ogg',
            '8': '8.ogg'
        }

        bit_board = game.copy()
        move = bit_board.pop()
        san_move = bit_board.san(move)
        voice_parts = []

        if san_move.startswith('O-O-O'):
            voice_parts += ['castlequeenside.ogg']
        elif san_move.startswith('O-O'):
            voice_parts += ['castlekingside.ogg']
        else:
            for part in san_move:
                try:
                    sound_file = move_parts[part]
                except KeyError:
                    logging.warning('unknown char found in san: [%s : %s]', san_move, part)
                    sound_file = ''
                if sound_file:
                    voice_parts += [sound_file]

        if game.is_game_over():
            if game.is_checkmate():
                wins = 'whitewins.ogg' if game.turn == chess.BLACK else 'blackwins.ogg'
                voice_parts += ['checkmate.ogg', wins]
            elif game.is_stalemate():
                voice_parts += ['stalemate.ogg']
            else:
                if game.is_seventyfive_moves():
                    voice_parts += ['75moves.ogg', 'draw.ogg']
                elif game.is_insufficient_material():
                    voice_parts += ['material.ogg', 'draw.ogg']
                elif game.is_fivefold_repetition():
                    voice_parts += ['repetition.ogg', 'draw.ogg']
                else:
                    voice_parts += ['draw.ogg']
        elif game.is_check():
            voice_parts += ['check.ogg']

        if bit_board.is_en_passant(move):
            voice_parts += ['enpassant.ogg']

        return voice_parts
