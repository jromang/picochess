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

__author__ = "Jürgen Précour"
__email__ = "LocutusOfPenguin@posteo.de"
__version__ = "0.77"

import glob
import threading
import chess
from utilities import *

from pydub import AudioSegment
from pydub.playback import *
import pyaudio
import sys
from pathlib import Path


class PicoTalkerDisplay(DisplayMsg, threading.Thread):
    def __init__(self, user_voice, computer_voice):
        """
        Initialize a PicoTalkerDisplay with voices for the user and/or computer players.
        :param user_voice: The voice to use for the user (eg. en:Callie).
        :param computer_voice:  The voice to use for the computer (eg. en:Marvin).
        """
        super(PicoTalkerDisplay, self).__init__()
        self.user_picotalker = None
        self.computer_picotalker = None

        # Hide errors
        devnull = os.open(os.devnull, os.O_WRONLY)
        old_stderr = os.dup(2)
        sys.stderr.flush()
        os.dup2(devnull, 2)
        os.close(devnull)

        self.pyaudio = pyaudio.PyAudio()
        # Enable errors
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

        if user_voice:
            logging.debug('creating user voice: [%s]', str(user_voice))
            self.user_picotalker = PicoTalker(self.pyaudio, user_voice)
        if computer_voice:
            logging.debug('creating computer voice: [%s]', str(computer_voice))
            self.computer_picotalker = PicoTalker(self.pyaudio, computer_voice)

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
                            logging.debug('Announcing START_NEW_GAME')
                            system_picotalker.say_new_game()
                        break
                    if case(MessageApi.COMPUTER_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.computer_picotalker is not None:
                            logging.debug('Announcing COMPUTER_MOVE [%s]', message.move)
                            self.computer_picotalker.say_move(message.move, message.fen, message.game.copy())
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.USER_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.user_picotalker is not None:
                            logging.debug('Announcing USER_MOVE [%s]', message.move)
                            self.user_picotalker.say_move(message.move, message.fen, message.game.copy())
                            previous_move = str(message.move)
                        break
                    if case(MessageApi.REVIEW_MOVE):
                        if message.move and message.game and str(message.move) != previous_move \
                                and self.user_picotalker is not None:
                            logging.debug('Announcing REVIEW_MOVE [%s]', message.move)
                            self.user_picotalker.say_move(message.move, message.fen, message.game.copy())
                            previous_move = str(message.move)
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

    def say_event(self, event):
        self.msg_queue.put(event)

    @staticmethod
    def localisations():
        """
        Returns a list of localisations found inside the voices directory.
        Examples:
            en:English
            ru:Russian
        """
        localisations = []
        voice_files = glob.glob(os.path.join(os.path.dirname(__file__), "voices", "*.json"))
        for voice_filepath in voice_files:
            with open(voice_filepath, "r") as fp:
                localisation_json = json.load(fp)
                if localisation_json:
                    localisation_id = localisation_json["identifier"]
                    localisation_language = localisation_json["language"]
                    if localisation_id and localisation_language:
                        localisations.append(localisation_id + ":" + localisation_language)
        return localisations

    @staticmethod
    def voices(localisation):
        """
        Returns a list of voices defined for the given localisation.
        Only returns voices if they are supported on the current platform type (Linux, Darwin).
        """
        voices = []
        try:
            localisation_id = localisation.split(":")[0]
            voice_filepath = os.path.join(os.path.dirname(__file__), "voices", localisation_id + ".json")
            with open(voice_filepath, "r") as fp:
                localisation_json = json.load(fp)
                if localisation_json:
                    voices_json = localisation_json["voices"]
                    for voice_json in voices_json:
                        voice_name = voice_json["name"]
                        voice_platforms = voice_json["platforms"]
                        if voice_name and voice_platforms.count(platform.system()) > 0:
                            voices.append(voice_name)
        except:
            logging.exception("Unexpected error")
        return voices


class PicoTalker():

    def __init__(self, audio, localisation_id_voice=None):
        self.localisation_id = None
        self.voice_name = None
        self.audio = audio

        try:
            (self.localisation_id, self.voice_name) = localisation_id_voice.split(':')
            voice_path = 'picotalker/voices/' + self.localisation_id + '/' + self.voice_name
            if not Path(voice_path).exists():
                logging.exception('voice path doesnt exist')
        except ValueError:
            logging.exception('not valid voice parameter')

    def play_sounds(self, sounds):
        sound = AudioSegment.empty()
        for part in sounds:
            voice_file = 'picotalker/voices/' + self.localisation_id + '/' + self.voice_name + '/' + part
            if Path(voice_file).is_file():
                sound += AudioSegment.from_ogg(voice_file)
            else:
                logging.warning('voice file not found {}', format(voice_file))

        p = self.audio
        stream = p.open(format=p.get_format_from_width(sound.sample_width), channels=sound.channels,
                        rate=sound.frame_rate,
                        output=True)

        # break audio into half-second chunks (to allows keyboard interrupts)
        for chunk in make_chunks(sound, 500):
            stream.write(chunk._data)

        stream.stop_stream()
        stream.close()

    def vocabulary_color(self, color):
        if color.lower() == PicoTalker.COLOR_WHITE:
            return self.vocabulary_white()
        else:
            return self.vocabulary_black()

    def vocabulary_piece(self, piece):
        if piece.upper() == PicoTalker.PIECE_KING:
            return self.vocabulary_king()
        elif piece.upper() == PicoTalker.PIECE_QUEEN:
            return self.vocabulary_queen()
        elif piece.upper() == PicoTalker.PIECE_BISHOP:
            return self.vocabulary_bishop()
        elif piece.upper() == PicoTalker.PIECE_KNIGHT:
            return self.vocabulary_knight()
        elif piece.upper() == PicoTalker.PIECE_ROOK:
            return self.vocabulary_rook()
        else:
            return self.vocabulary_pawn()

    def vocabulary_white(self):
        return self.voice_vocabulary[PicoTalker.VOCAB_WHITE]

    def vocabulary_black(self):
        return self.voice_vocabulary[PicoTalker.VOCAB_BLACK]

    def vocabulary_pawn(self):
        return self.voice_vocabulary[PicoTalker.VOCAB_PAWN]

    def vocabulary_rook(self):
        return self.voice_vocabulary[PicoTalker.VOCAB_ROOK]

    def vocabulary_knight(self):
        return self.voice_vocabulary[PicoTalker.VOCAB_KNIGHT]

    def vocabulary_bishop(self):
        return self.voice_vocabulary[PicoTalker.VOCAB_BISHOP]

    def vocabulary_queen(self):
        return self.voice_vocabulary[PicoTalker.VOCAB_QUEEN]

    def vocabulary_king(self):
        return self.voice_vocabulary[PicoTalker.VOCAB_KING]

    def say_castles_kingside(self):
        self.play_sounds(['castlekingside'])

    def say_castles_queenside(self):
        self.play_sounds(['castlequeenside'])

    def say_captures(self, attacking_piece, captured_piece):
        text = self.voice_vocabulary[PicoTalker.VOCAB_CAPTURES].replace("$(ATTACKING_PIECE)",
                                                                        self.vocabulary_piece(
                                                                                  attacking_piece)).replace(
            "$(CAPTURED_PIECE)", self.vocabulary_piece(captured_piece))
        return self.say_text(text)

    def say_check(self):
        self.play_sounds(['check'])

    def say_promotion(self, piece):
        text = self.voice_vocabulary[PicoTalker.VOCAB_PROMOTION_TO].replace("$(PIECE)",
                                                                            self.vocabulary_piece(piece))
        return self.say_text(text)

    def say_checkmate(self):
        self.play_sounds(['checkmate'])

    def say_stalemate(self):
        self.play_sounds(['stalemate'])

    def say_draw(self):
        self.play_sounds(['draw.ogg'])

    def say_draw_seventyfive_moves(self):
        self.play_sounds(['75moves.ogg', 'draw.ogg'])

    def say_draw_insufficient_material(self):
        self.play_sounds(['material.ogg', 'draw.ogg'])

    def say_draw_fivefold_repetition(self):
        self.play_sounds(['repetition.ogg', 'draw.ogg'])

    def say_winner(self, color):
        wins = 'whitewins.ogg' if color == chess.WHITE else 'blackwins.ogg'
        self.play_sounds([wins])

    def say_out_of_time(self, color):
        wins = 'whitewins.ogg' if color == chess.WHITE else 'blackwins.ogg'
        self.play_sounds(['timelost.ogg', wins])

    def say_new_game(self):
        """Announce a new game"""
        self.play_sounds(['newgame.ogg'])

    def say_game_aborted(self):
        """Announce game aborted"""
        self.play_sounds(['abort.ogg'])

    def say_shutdown(self):
        """Announce system shutdown"""
        self.play_sounds(['goodbye.ogg'])

    def say_position(self, position):
        """Say a square position, eg. a3"""
        # logging.debug("Saying position [%s]", position)
        if len(position) == 2:
            pos_file = position[0].lower()
            pos_rank = position[1]
            if pos_file >= "a" and pos_file <= "h" and pos_rank >= "1" and pos_rank <= "8":
                text = ""
                if pos_file == "a":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_FILE_A]
                if pos_file == "b":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_FILE_B]
                if pos_file == "c":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_FILE_C]
                if pos_file == "d":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_FILE_D]
                if pos_file == "e":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_FILE_E]
                if pos_file == "f":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_FILE_F]
                if pos_file == "g":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_FILE_G]
                if pos_file == "h":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_FILE_H]
                if pos_rank == "1":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_RANK_1]
                if pos_rank == "2":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_RANK_2]
                if pos_rank == "3":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_RANK_3]
                if pos_rank == "4":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_RANK_4]
                if pos_rank == "5":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_RANK_5]
                if pos_rank == "6":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_RANK_6]
                if pos_rank == "7":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_RANK_7]
                if pos_rank == "8":
                    text = text + self.voice_vocabulary[PicoTalker.VOCAB_RANK_8]
                return self.say_text(text)
        return -1  # Error - Unrecognised board position

    def say_text(self, text):
        """Feed the given text as-is into the TTS engine"""
        cmd = self.voice_command.replace("$(TEXT)", "\"" + text + "\"")
        # print("cmd=[" + cmd + "]")
        return subprocess.call(cmd, shell=True)

    def say_move(self, move, fen, game):
        """
        Takes a chess.Move instance and a chess.BitBoard instance and speaks the move.
        """

        # JP!
        SPOKEN_PIECE_SOUNDS = {
            'K': 'king.ogg',
            'B': 'bishop.ogg',
            'N': 'knight.ogg',
            'R': 'rook.ogg',
            'Q': 'queen.ogg',
            '+': 'check.ogg',
            '#': '',
            'x': 'takes.ogg',
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
        moveTextSAN = bit_board.san(move)

        is_check = game.is_check()
        is_checkmate = game.is_checkmate()
        is_stalemate = game.is_stalemate()
        is_game_over = game.is_game_over()
        is_insufficient_material = game.is_insufficient_material()
        is_seventyfive_moves = game.is_seventyfive_moves()
        is_fivefold_repetition = game.is_fivefold_repetition()

        if moveTextSAN.startswith('O-O-O'):
            self.say_castles_queenside()
        elif moveTextSAN.startswith('O-O'):
            self.say_castles_kingside()
        else:
            spoken_san = []
            for c in moveTextSAN:
                spoken_san.append(SPOKEN_PIECE_SOUNDS[c])
            self.play_sounds(spoken_san)

        if move.promotion:
            print('Promotion!!')
            # self.say_promotion(moveText[4])

        if is_game_over:
            if is_checkmate:
                self.say_checkmate()
                # self.say_winner(color_moved)
            elif is_stalemate:
                self.say_stalemate()
            else:
                if is_seventyfive_moves:
                    self.say_draw_seventyfive_moves()
                elif is_insufficient_material:
                    self.say_draw_insufficient_material()
                elif is_fivefold_repetition:
                    self.say_draw_fivefold_repetition()
                else:
                    self.say_draw()
        elif is_check:
            self.say_check()
