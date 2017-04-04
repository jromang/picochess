# Copyright (C) 2013-2017 Jean-Francois Romang (jromang@posteo.de)
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

import threading
import chess
from utilities import DisplayMsg, switch
import logging
import subprocess
import queue
from dgtapi import MessageApi
from dgtutil import GameResult, PlayMode, VoiceType
from pathlib import Path


class PicoTalker():
    def __init__(self, localisation_id_voice=None):
        self.voice_path = None

        try:
            (localisation_id, voice_name) = localisation_id_voice.split(':')
            voice_path = 'talker/voices/' + localisation_id + '/' + voice_name
            if Path(voice_path).exists():
                self.voice_path = voice_path
            else:
                logging.warning('voice path doesnt exist')
        except ValueError:
            logging.warning('not valid voice parameter')

    def talk(self, sounds):
        """speak out the sound part by using ogg123."""
        if self.voice_path:
            for part in sounds:
                voice_file = self.voice_path + '/' + part
                if Path(voice_file).is_file():
                    try:
                        subprocess.call(['ogg123', voice_file], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    except OSError as os_exc:
                        logging.warning('OSError: {} => turn voice OFF'.format(os_exc))
                        self.voice_path = None
                else:
                    logging.warning('voice file not found {}'.format(voice_file))
        else:
            logging.debug('picotalker turned off')


class PicoTalkerDisplay(DisplayMsg, threading.Thread):
    def __init__(self, user_voice, computer_voice):
        """
        Initialize a PicoTalkerDisplay with voices for the user and/or computer players.

        :param user_voice: The voice to use for the user (eg. en:al).
        :param computer_voice:  The voice to use for the computer (eg. en:christina).
        """
        super(PicoTalkerDisplay, self).__init__()
        self.user_picotalker = None
        self.computer_picotalker = None

        if user_voice:
            logging.debug('creating user voice: [%s]', str(user_voice))
            self.set_user(PicoTalker(user_voice))
        if computer_voice:
            logging.debug('creating computer voice: [%s]', str(computer_voice))
            self.set_computer(PicoTalker(computer_voice))

    def set_computer(self, picotalker):
        self.computer_picotalker = picotalker

    def set_user(self, picotalker):
        self.user_picotalker = picotalker

    def run(self):
        """
        Start listening for Messages on our queue and generate speech as appropriate.
        """
        previous_move = ''  # Ignore repeated broadcasts of a move.
        system_picotalker = self.system_voice()
        logging.info('msg_queue ready')
        while True:
            try:
                # Check if we have something to say.
                message = self.msg_queue.get()
                # if repr(message) != MessageApi.DGT_SERIAL_NR:
                #     logging.debug("received message from msg_queue: %s", message)

                for case in switch(message):
                    if case(MessageApi.ENGINE_FAIL):
                        logging.debug('announcing ENGINE_FAIL')
                        system_picotalker.talk(['error.ogg'])
                        break
                    if case(MessageApi.START_NEW_GAME):
                        if message.newgame:
                            logging.debug('announcing START_NEW_GAME')
                            system_picotalker.talk(['newgame.ogg'])
                        break
                    if case(MessageApi.COMPUTER_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.computer_picotalker is not None:
                            logging.debug('announcing COMPUTER_MOVE [%s]', message.move)
                            self.computer_picotalker.talk(self.say_move(message.move, message.game.fen(), message.game))
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.USER_MOVE_DONE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.user_picotalker is not None:
                            logging.debug('announcing USER_MOVE [%s]', message.move)
                            self.user_picotalker.talk(self.say_move(message.move, message.fen, message.game))
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.REVIEW_MOVE_DONE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.user_picotalker is not None:
                            logging.debug('announcing REVIEW_MOVE [%s]', message.move)
                            self.user_picotalker.talk(self.say_move(message.move, message.fen, message.game))
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.GAME_ENDS):
                        if message.result == GameResult.OUT_OF_TIME:
                            logging.debug('announcing GAME_ENDS/TIME_CONTROL')
                            wins = 'whitewins.ogg' if message.game.turn == chess.BLACK else 'blackwins.ogg'
                            system_picotalker.talk(['timelost.ogg', wins])
                        elif message.result == GameResult.INSUFFICIENT_MATERIAL:
                            logging.debug('announcing GAME_ENDS/INSUFFICIENT_MATERIAL')
                            system_picotalker.talk(['material.ogg', 'draw.ogg'])
                        elif message.result == GameResult.MATE:
                            logging.debug('announcing GAME_ENDS/MATE')
                            system_picotalker.talk(['checkmate.ogg'])
                        elif message.result == GameResult.STALEMATE:
                            logging.debug('announcing GAME_ENDS/STALEMATE')
                            system_picotalker.talk(['stalemate.ogg'])
                        elif message.result == GameResult.ABORT:
                            logging.debug('announcing GAME_ENDS/ABORT')
                            system_picotalker.talk(['abort.ogg'])
                        elif message.result == GameResult.DRAW:
                            logging.debug('announcing GAME_ENDS/DRAW')
                            system_picotalker.talk(['draw.ogg'])
                        elif message.result == GameResult.WIN_WHITE:
                            logging.debug('announcing GAME_ENDS/WHITE_WIN')
                            system_picotalker.talk(['whitewins.ogg'])
                        elif message.result == GameResult.WIN_BLACK:
                            logging.debug('announcing GAME_ENDS/BLACK_WIN')
                            system_picotalker.talk(['blackwins.ogg'])
                        elif message.result == GameResult.FIVEFOLD_REPETITION:
                            logging.debug('announcing GAME_ENDS/FIVEFOLD_REPETITION')
                            system_picotalker.talk(['repetition.ogg', 'draw.ogg'])
                        break
                    if case(MessageApi.TAKE_BACK):
                        logging.debug('announcing TAKE_BACK')
                        system_picotalker.talk(['takeback.ogg'])
                        break
                    if case(MessageApi.TIME_CONTROL):
                        logging.debug('announcing TIME_CONTROL')
                        system_picotalker.talk(['oktime.ogg'])
                        break
                    if case(MessageApi.INTERACTION_MODE):
                        logging.debug('announcing INTERACTION_MODE')
                        system_picotalker.talk(['okmode.ogg'])
                        break
                    if case(MessageApi.LEVEL):
                        if message.do_speak:
                            logging.debug('announcing LEVEL')
                            system_picotalker.talk(['oklevel.ogg'])
                        else:
                            logging.debug('dont announce LEVEL cause its also an engine message')
                        break
                    if case(MessageApi.OPENING_BOOK):
                        logging.debug('announcing OPENING_BOOK')
                        system_picotalker.talk(['okbook.ogg'])
                        break
                    if case(MessageApi.ENGINE_READY):
                        logging.debug('announcing ENGINE_READY')
                        system_picotalker.talk(['okengine.ogg'])
                        break
                    if case(MessageApi.PLAY_MODE):
                        logging.debug('announcing PLAY_MODE')
                        userplay = 'userblack.ogg' if message.play_mode == PlayMode.USER_BLACK else 'userwhite.ogg'
                        system_picotalker.talk([userplay])
                        break
                    if case(MessageApi.STARTUP_INFO):
                        logging.debug('announcing PICOCHESS')
                        system_picotalker.talk(['picoChess.ogg'])
                        break
                    if case(MessageApi.SYSTEM_SHUTDOWN):
                        logging.debug('announcing SHUTDOWN')
                        system_picotalker.talk(['goodbye.ogg'])
                        break
                    if case(MessageApi.SYSTEM_REBOOT):
                        logging.debug('announcing REBOOT')
                        system_picotalker.talk(['pleasewait.ogg'])
                        break
                    if case(MessageApi.SET_VOICE):
                        picotalker = PicoTalker(message.lang + ':' + message.speaker)
                        if message.type == VoiceType.USER_VOICE:
                            self.set_user(picotalker)
                        else:
                            self.set_computer(picotalker)
                        system_picotalker = self.system_voice()
                        break
                    if case():  # Default
                        # print(message)
                        pass
            except queue.Empty:
                pass

    def system_voice(self):
        """
        Return a voice object to use for system announcements (settings changes, etc).
        Attempts to return the computer voice first, otherwise returns the user voice.
        """
        if self.computer_picotalker:
            return self.computer_picotalker
        else:
            return self.user_picotalker

    @staticmethod
    def say_move(move, fen, game: chess.Board):
        """
        Take a chess.Move instance and a chess.BitBoard instance and speaks the move.
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
            for part in san_move:
                try:
                    sound_file = move_parts[part]
                except KeyError:
                    logging.warning('unknown char found in san: [{} : {}]'.format(san_move, part))
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
