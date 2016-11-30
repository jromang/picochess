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
from pathlib import Path


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

    def talk(self, sounds, path):
        def play(file):
            import sounddevice as sd
            import soundfile as sf
            sd.default.blocksize = 2048

            d, f = sf.read(file, dtype='float32')
            sd.play(d, f, blocking=True)
            status = sd.get_status()
            if status:
                logging.warning(str(status))

        for part in sounds:
            voice_file = path + '/' + part
            if Path(voice_file).is_file():
                try:
                    subprocess.call(['ogg123', voice_file], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except OSError as e:  # fallback in case "vorbis-tools" isnt installed
                    logging.info('using sounddevice for [{}] Error: {}'.format(voice_file, e))
                    play(voice_file)
            else:
                logging.warning('voice file not found {}'.format(voice_file))

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
                            self.talk(['newgame.ogg'], system_picotalker.get_path())
                        break
                    if case(MessageApi.COMPUTER_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.computer_picotalker is not None:
                            logging.debug('announcing COMPUTER_MOVE [%s]', message.move)
                            self.talk(self.say_move(message.move, message.fen, message.game.copy()),
                                      self.computer_picotalker.get_path())
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.USER_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.user_picotalker is not None:
                            logging.debug('announcing USER_MOVE [%s]', message.move)
                            self.talk(self.say_move(message.move, message.fen, message.game.copy()),
                                      self.user_picotalker.get_path())
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.REVIEW_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.user_picotalker is not None:
                            logging.debug('announcing REVIEW_MOVE [%s]', message.move)
                            self.talk(self.say_move(message.move, message.fen, message.game.copy()),
                                      self.user_picotalker.get_path())
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.GAME_ENDS):
                        if message.result == GameResult.OUT_OF_TIME:
                            logging.debug('announcing GAME_ENDS/TIME_CONTROL')
                            wins = 'whitewins.ogg' if message.game.turn == chess.BLACK else 'blackwins.ogg'
                            self.talk(['timelost.ogg', wins], system_picotalker.get_path())
                        elif message.result == GameResult.INSUFFICIENT_MATERIAL:
                            logging.debug('announcing GAME_ENDS/INSUFFICIENT_MATERIAL')
                            self.talk(['material.ogg', 'draw.ogg'], system_picotalker.get_path())
                        elif message.result == GameResult.MATE:
                            logging.debug('announcing GAME_ENDS/MATE')
                            self.talk(['checkmate.ogg'], system_picotalker.get_path())
                        elif message.result == GameResult.STALEMATE:
                            logging.debug('announcing GAME_ENDS/STALEMATE')
                            self.talk(['stalemate.ogg'], system_picotalker.get_path())
                        elif message.result == GameResult.ABORT:
                            logging.debug('announcing GAME_ENDS/ABORT')
                            self.talk(['abort.ogg'], system_picotalker.get_path())
                        elif message.result == GameResult.DRAW:
                            logging.debug('announcing DRAW')
                            self.talk(['draw.ogg'], system_picotalker.get_path())
                        elif message.result == GameResult.WIN_WHITE:
                            logging.debug('announcing WHITE WIN')
                            self.talk(['whitewins.ogg'], system_picotalker.get_path())
                        elif message.result == GameResult.WIN_BLACK:
                            logging.debug('announcing BLACK WIN')
                            self.talk(['blackwins.ogg'], system_picotalker.get_path())
                        elif message.result == GameResult.FIVEFOLD_REPETITION:
                            logging.debug('announcing GAME_ENDS/FIVEFOLD_REPETITION')
                            self.talk(['repetition.ogg', 'draw.ogg'], system_picotalker.get_path())
                        break
                    if case(MessageApi.USER_TAKE_BACK):
                        self.talk(['takeback.ogg'], system_picotalker.get_path())
                        break
                    if case(MessageApi.TIME_CONTROL):
                        self.talk(['oktime.ogg'], system_picotalker.get_path())
                        break
                    if case(MessageApi.INTERACTION_MODE):
                        self.talk(['okmode.ogg'], system_picotalker.get_path())
                        break
                    if case(MessageApi.LEVEL):
                        self.talk(['oklevel.ogg'], system_picotalker.get_path())
                        break
                    if case(MessageApi.OPENING_BOOK):
                        self.talk(['okbook.ogg'], system_picotalker.get_path())
                        break
                    if case(MessageApi.ENGINE_READY):
                        self.talk(['okengine.ogg'], system_picotalker.get_path())
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
            voice_parts += ['castlequeenside.ogg']
        elif san_move.startswith('O-O'):
            voice_parts += ['castlekingside.ogg']
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

        return voice_parts


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

    def get_path(self):
        return self.voice_path

