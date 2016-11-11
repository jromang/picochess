#!/usr/bin/env python3

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

# for this (picotalker) to work you need to run these commands (if you haven't done before)
# pip3 install sounddevice
# pip3 install soundfile
# apt-get install python3-numpy
# apt-get install libportaudio2
# apt-get install python3-cffi

import threading
import chess
from utilities import *

import sounddevice as sd
import soundfile as sf

from pathlib import Path

sd.default.blocksize = 2048


class PicoTalkerDisplay(DisplayMsg, threading.Thread):
    def __init__(self, user_voice, computer_voice):
        """
        Initialize a PicoTalkerDisplay with voices for the user and/or computer players.
        :param user_voice: The voice to use for the user (eg. en:al).
        :param computer_voice:  The voice to use for the computer (eg. en:dgt).
        """
        super(PicoTalkerDisplay, self).__init__()
        self.user_picotalker = None
        self.computer_picotalker = None

        if user_voice:
            logging.debug('creating user voice: [%s]', str(user_voice))
            self.user_picotalker = PicoTalker(user_voice)
        if computer_voice:
            logging.debug('creating computer voice: [%s]', str(computer_voice))
            self.computer_picotalker = PicoTalker(computer_voice)

    def run(self):
        """
        Start listening for Messages on our queue and generate speech as appropriate.
        """
        previous_move = ''  # Ignore repeated broadcasts of a move.
        system_picotalker = self.system_voice()
        logging.info('msg_queue ready')
        # Only run if we have any voices configured for user/computer
        while self.user_picotalker or self.computer_picotalker:
            try:
                # Check if we have something to say.
                message = self.msg_queue.get()
                logging.debug("received message from msg_queue: %s", message)

                for case in switch(message):
                    if case(MessageApi.START_NEW_GAME):
                        if system_picotalker:
                            logging.debug('announcing START_NEW_GAME')
                            system_picotalker.say_new_game()
                        break
                    if case(MessageApi.COMPUTER_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.computer_picotalker is not None:
                            logging.debug('announcing COMPUTER_MOVE [%s]', message.move)
                            self.computer_picotalker.say_move(message.move, message.fen, message.game.copy())
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.USER_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.user_picotalker is not None:
                            logging.debug('announcing USER_MOVE [%s]', message.move)
                            self.user_picotalker.say_move(message.move, message.fen, message.game.copy())
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.REVIEW_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.user_picotalker is not None:
                            logging.debug('announcing REVIEW_MOVE [%s]', message.move)
                            self.user_picotalker.say_move(message.move, message.fen, message.game.copy())
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.GAME_ENDS):
                        if message.result == GameResult.OUT_OF_TIME:
                            logging.debug('announcing GAME_ENDS/TIME_CONTROL')
                            system_picotalker.say_out_of_time(not message.game.turn)
                        elif message.result == GameResult.INSUFFICIENT_MATERIAL:
                            logging.debug('announcing GAME_ENDS/INSUFFICIENT_MATERIAL')
                            system_picotalker.say_draw_insufficient_material()
                        elif message.result == GameResult.MATE:
                            logging.debug('announcing GAME_ENDS/MATE')
                            system_picotalker.say_checkmate()
                        elif message.result == GameResult.STALEMATE:
                            logging.debug('announcing GAME_ENDS/STALEMATE')
                            system_picotalker.say_stalemate()
                        elif message.result == GameResult.ABORT:
                            logging.debug('announcing GAME_ENDS/ABORT')
                            system_picotalker.say_game_aborted()
                        elif message.result == GameResult.DRAW:
                            logging.debug('announcing DRAW')
                            system_picotalker.say_draw()
                        elif message.result == GameResult.WIN_WHITE:
                            logging.debug('announcing WHITE WIN')
                            system_picotalker.say_winner(chess.WHITE)
                        elif message.result == GameResult.WIN_BLACK:
                            logging.debug('announcing BLACK WIN')
                            system_picotalker.say_winner(chess.BLACK)
                        elif message.result == GameResult.FIVEFOLD_REPETITION:
                            logging.debug('announcing GAME_ENDS/FIVEFOLD_REPETITION')
                            system_picotalker.say_draw_fivehold_repetition()
                        break
                    if case(MessageApi.USER_TAKE_BACK):
                        system_picotalker.say_takeback()
                        break
                    if case(MessageApi.TIME_CONTROL):
                        system_picotalker.say_oktime()
                        break
                    if case(MessageApi.INTERACTION_MODE):
                        system_picotalker.say_okmode()
                        break
                    if case(MessageApi.LEVEL):
                        system_picotalker.say_oklevel()
                        break
                    if case(MessageApi.OPENING_BOOK):
                        system_picotalker.say_okbook()
                        break
                    if case(MessageApi.ENGINE_READY):
                        system_picotalker.say_okengine()
                        break
                    if case():  # Default
                        # print(message)
                        pass
            except queue.Empty:
                pass

    def system_voice(self):
        """
        Returns a voice object to use for system announcements (settings changes, etc).
        Attempts to return the computer voice first, otherwise returns the user voice.
        """
        if self.computer_picotalker:
            return self.computer_picotalker
        else:
            return self.user_picotalker


class PicoTalker():
    def __init__(self, localisation_id_voice=None):
        self.voice_path = None

        try:
            (localisation_id, voice_name) = localisation_id_voice.split(':')
            self.voice_path = 'talker/voices/' + localisation_id + '/' + voice_name
            if not Path(self.voice_path).exists():
                logging.exception('voice path doesnt exist')
        except ValueError:
            logging.exception('not valid voice parameter')

    def talk(self, sounds):
        def play(file, blocking=True):
            d, f = sf.read(file, dtype='float32')
            sd.play(d, f, blocking=blocking)
            status = sd.get_status()
            if status:
                logging.warning(str(status))

        for part in sounds:
            voice_file = self.voice_path + '/' + part
            if Path(voice_file).is_file():
                play(voice_file)
            else:
                logging.warning('voice file not found {}'.format(voice_file))

    def get_castles_kingside(self):
        return ['castlekingside.ogg']

    def get_castles_queenside(self):
        return ['castlequeenside.ogg']

    def get_check(self):
        return ['check.ogg']

    def get_checkmate(self):
        return ['checkmate.ogg']

    def get_stalemate(self):
        return ['stalemate.ogg']

    def get_draw(self):
        return ['draw.ogg']

    def get_draw_seventyfive_moves(self):
        return ['75moves.ogg', 'draw.ogg']

    def get_draw_insufficient_material(self):
        return ['material.ogg', 'draw.ogg']

    def get_draw_fivefold_repetition(self):
        return ['repetition.ogg', 'draw.ogg']

    def get_winner(self, color):
        wins = 'whitewins.ogg' if color == chess.WHITE else 'blackwins.ogg'
        return [wins]

    def get_out_of_time(self, color):
        """Announce lost on time"""
        wins = 'whitewins.ogg' if color == chess.WHITE else 'blackwins.ogg'
        return ['timelost.ogg', wins]

    def get_new_game(self):
        """Announce a new game"""
        return ['newgame.ogg']

    def get_game_aborted(self):
        """Announce game aborted"""
        return ['abort.ogg']

    def get_shutdown(self):
        """Announce system shutdown"""
        return ['goodbye.ogg']

    def get_takeback(self):
        """Announce takeback"""
        return ['takeback.ogg']

    def get_ok(self):
        """Announce ok"""
        return ['ok.ogg']

    def get_okbook(self):
        """Announce ok book"""
        return ['okbook.ogg']

    def get_okengine(self):
        """Announce ok engine"""
        return ['okengine.ogg']

    def get_oklevel(self):
        """Announce ok level"""
        return ['oklevel.ogg']

    def get_okmode(self):
        """Announce ok mode"""
        return ['okmode.ogg']

    def get_oktime(self):
        """Announce ok time"""
        return ['oktime.ogg']

    def say_new_game(self):
        self.talk(self.get_new_game())

    def say_out_of_time(self, color):
        self.talk(self.get_out_of_time(color))

    def say_draw_insufficient_material(self):
        self.talk(self.get_draw_insufficient_material())

    def say_checkmate(self):
        self.talk(self.get_checkmate())

    def say_stalemate(self):
        self.talk(self.get_stalemate())

    def say_game_aborted(self):
        self.talk(self.get_game_aborted())

    def say_draw(self):
        self.talk(self.get_draw())

    def say_winner(self, color):
        self.talk(self.get_winner(color))

    def say_draw_fivehold_repetition(self):
        self.talk(self.get_draw_fivefold_repetition())

    def say_takeback(self):
        self.talk(self.get_takeback())

    def say_ok(self):
        self.talk(self.get_ok())

    def say_okbook(self):
        self.talk(self.get_okbook())

    def say_okengine(self):
        self.talk(self.get_okengine())

    def say_oklevel(self):
        self.talk(self.get_oklevel())

    def say_okmode(self):
        self.talk(self.get_okmode())

    def say_oktime(self):
        self.talk(self.get_oktime())

    def say_move(self, move, fen, game):
        """
        Takes a chess.Move instance and a chess.BitBoard instance and speaks the move.
        """
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

        bit_board = chess.Board(fen)
        san_move = bit_board.san(move)
        voice_parts = []

        if san_move.startswith('O-O-O'):
            voice_parts += self.get_castles_queenside()
        elif san_move.startswith('O-O'):
            voice_parts += self.get_castles_kingside()
        else:
            for c in san_move:
                try:
                    sound_file = move_parts[c]
                except KeyError:
                    logging.warning('unknown char found in san: [{} : {}]'.format(san_move, c))
                    sound_file = ''
                if sound_file:
                    voice_parts += [sound_file]

        if game.is_game_over():
            if game.is_checkmate():
                voice_parts += self.get_checkmate()
                voice_parts += self.get_winner(not game.turn)
            elif game.is_stalemate():
                voice_parts += self.get_stalemate()
            else:
                if game.is_seventyfive_moves():
                    voice_parts += self.get_draw_seventyfive_moves()
                elif game.is_insufficient_material():
                    voice_parts += self.get_draw_insufficient_material()
                elif game.is_fivefold_repetition():
                    voice_parts += self.get_draw_fivefold_repetition()
                else:
                    voice_parts += self.get_draw()
        elif game.is_check():
            voice_parts += self.get_check()

        self.talk(voice_parts)
