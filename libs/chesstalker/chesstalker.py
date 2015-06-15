#!/usr/bin/env python3

# Copyright (C) 2013-2015 Jean-Francois Romang (jromang@posteo.de)
#                         Shivkumar Shivaji ()
#                         Charles Gamble ()
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

__author__ = "Charles Gamble"

__email__ = ""

__version__ = "0.1.0"

import sys
import os
import platform
import json
import glob
import subprocess
import threading
import logging
import chess
from utilities import *

SPOKEN_PIECE_SOUNDS = {
    "B": " Bishop ",
    "N": " Knight ",
    "R": " Rook ",
    "Q": " Queen ",
    "K": " King ",
    # "++": " Double Check ",
    "+": " ",
    "x": " captures "
}


class ChessTalker(Display, threading.Thread):
    def __init__(self, user_voice, computer_voice):
        """
        Initialize a ChessTalker with voices for the user and/or computer players.
        :param user_voice: The voice to use for the user (eg. en:Callie).
        :param computer_voice:  The voice to use for the computer (eg. en:Marvin).
        """
        super(ChessTalker, self).__init__()
        self.user_chesstalker_voice = None
        self.computer_chesstalker_voice = None
        try:
            if user_voice and user_voice.upper() != "NONE":
                logging.debug('ChessTalker: Creating user voice: [%s]', str(user_voice))
                self.user_chesstalker_voice = ChessTalkerVoice(user_voice)
                if len(self.user_chesstalker_voice.voice_vocabulary) == 0:
                    logging.error('ChessTalker: Failed to create user voice: [%s]', str(user_voice))
                    self.user_chesstalker_voice = None
            if computer_voice and computer_voice.upper() != "NONE":
                logging.debug('ChessTalker: Creating computer voice: [%s]', str(computer_voice))
                self.computer_chesstalker_voice = ChessTalkerVoice(computer_voice)
                if len(self.computer_chesstalker_voice.voice_vocabulary) == 0:
                    logging.error('ChessTalker: Failed to create computer voice: [%s]', str(computer_voice))
                    self.computer_chesstalker_voice = None
        except:
            logging.exception("Unexpected error")

    def run(self):
        """
        Start listening for Messages on our queue and generate speech as appropriate.
        """
        previous_move = ""  # Ignore repeated broadcasts of a move.
        # Only run if we have any voices configured for user/computer.
        while self.user_chesstalker_voice or self.computer_chesstalker_voice:
            try:
                # Check if we have something to say.
                message = self.message_queue.get()
                messageType = type(message).__name__
                logging.debug("Read message from queue: %s", message)
                system_voice = self.system_voice()

                if messageType == "Message":
                    if message == Message.START_NEW_GAME and system_voice:
                        logging.debug('Announcing START_NEW_GAME')
                        system_voice.say_new_game()
                    elif message == Message.COMPUTER_MOVE and message.move and message.game and str(message.move) != previous_move:
                        logging.debug('Announcing computer move [%s]', message.move)
                        self.computer_chesstalker_voice.say_move(message.move, message.game)
                        previous_move = str(message.move)
                    elif message == Message.USER_MOVE and message.move and message.game and str(message.move) != previous_move:
                        logging.debug('Announcing user move [%s]', message.move)
                        self.user_chesstalker_voice.say_move(message.move, message.game)
                        previous_move = str(message.move)
                    elif message == Message.GAME_ENDS and message.result == GameResult.TIME_CONTROL:
                        logging.debug('Announcing GAME_ENDS/TIME_CONTROL')
                        color = ChessTalkerVoice.COLOR_WHITE if message.color == chess.WHITE else ChessTalkerVoice.COLOR_BLACK
                        system_voice.say_out_of_time(color)
                    elif message == Message.GAME_ENDS and message.result == GameResult.INSUFFICIENT_MATERIAL:
                        pass
                        # logging.debug('Announcing GAME_ENDS/INSUFFICIENT_MATERIAL')
                        # system_voice.say_draw_insufficient_material()
                    elif message == Message.GAME_ENDS and message.result == GameResult.MATE:
                        pass
                        # logging.debug('Announcing GAME_ENDS/MATE')
                    elif message == Message.GAME_ENDS and message.result == GameResult.STALEMATE:
                        pass
                        # logging.debug('Announcing GAME_ENDS/STALEMATE')
                        # system_voice.say_stalemate()
                    elif message == Message.GAME_ENDS and message.result == GameResult.ABORT:
                        logging.debug('Announcing GAME_ENDS/ABORT')
                        system_voice.say_game_aborted()
                elif messageType == "Event":
                    if message == Event.LEVEL:
                        logging.debug('Announcing LEVEL')
                        system_voice.say_level(message.level)
                    elif message == Event.OPENING_BOOK:
                        logging.debug('Announcing OPENING_BOOK')
                        system_voice.say_opening_book(get_opening_books()[message.book_index][0])
                    elif message == Event.SET_MODE:
                        logging.debug('Announcing SET_MODE')
                        system_voice.say_mode(message.mode)
                    elif message == Event.SET_TIME_CONTROL:
                        logging.debug('Announcing SET_TIME_CONTROL')
                        if message.time_control_string.startswith("mov"):
                            time_control_value = int(message.time_control_string[3:].strip())
                            system_voice.say_time_control_fixed_time(time_control_value)
                        elif message.time_control_string.startswith("bl"):
                            time_control_value = int(message.time_control_string[2:].strip())
                            system_voice.say_time_control_blitz(time_control_value)
                        elif message.time_control_string.startswith("f"):
                            time_control_values = message.time_control_string[1:].strip().split()
                            # logging.debug('time_control_values: ' + str(time_control_values))
                            minutes_per_game = time_control_values[0]
                            fischer_increment = time_control_values[1]
                            # logging.debug('minutes_per_game: ' + str(minutes_per_game))
                            # logging.debug('fischer_increment: ' + str(fischer_increment))
                            system_voice.say_time_control_fischer(minutes_per_game, fischer_increment)
                    elif message == Event.SHUTDOWN:
                        logging.debug('Announcing SHUTDOWN')
                        system_voice.say_shutdown()
            except queue.Empty:
                pass
            except:
                logging.exception("Unexpected error")

    def system_voice(self):
        """
        Returns a voice object to use for system announcements (settings changes, etc).
        Attempts to return the computer voice first, otherwise returns the user voice.
        """
        if self.computer_chesstalker_voice:
            return self.computer_chesstalker_voice
        else:
            return self.user_chesstalker_voice

    def say_event(self, event):
        self.message_queue.put(event)

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


class ChessTalkerVoice():
    COLOR_BLACK = "b"
    COLOR_WHITE = "w"
    PIECE_PAWN = "P"
    PIECE_ROOK = "R"
    PIECE_KNIGHT = "N"
    PIECE_BISHOP = "B"
    PIECE_QUEEN = "Q"
    PIECE_KING = "K"
    VOCAB_WHITE = "WHITE"
    VOCAB_BLACK = "BLACK"
    VOCAB_KING = "KING"
    VOCAB_QUEEN = "QUEEN"
    VOCAB_BISHOP = "BISHOP"
    VOCAB_KNIGHT = "KNIGHT"
    VOCAB_ROOK = "ROOK"
    VOCAB_PAWN = "PAWN"
    VOCAB_FILE_A = "FILE_A"
    VOCAB_FILE_B = "FILE_B"
    VOCAB_FILE_C = "FILE_C"
    VOCAB_FILE_D = "FILE_D"
    VOCAB_FILE_E = "FILE_E"
    VOCAB_FILE_F = "FILE_F"
    VOCAB_FILE_G = "FILE_G"
    VOCAB_FILE_H = "FILE_H"
    VOCAB_RANK_1 = "RANK_1"
    VOCAB_RANK_2 = "RANK_2"
    VOCAB_RANK_3 = "RANK_3"
    VOCAB_RANK_4 = "RANK_4"
    VOCAB_RANK_5 = "RANK_5"
    VOCAB_RANK_6 = "RANK_6"
    VOCAB_RANK_7 = "RANK_7"
    VOCAB_RANK_8 = "RANK_8"
    VOCAB_CASTLES_KINGSIDE = "CASTLES_KINGSIDE"
    VOCAB_CASTLES_QUEENSIDE = "CASTLES_QUEENSIDE"
    VOCAB_CAPTURES = "CAPTURES"
    VOCAB_CHECK = "CHECK"
    VOCAB_PROMOTION_TO = "PROMOTION_TO"
    VOCAB_RESULT_CHECKMATE = "RESULT_CHECKMATE"
    VOCAB_RESULT_STALEMATE = "RESULT_STALEMATE"
    VOCAB_RESULT_DRAW = "RESULT_DRAW"
    VOCAB_RESULT_TIME_CONTROL = "RESULT_TIME_CONTROL"
    VOCAB_RESULT_INSUFFICIENT_MATERIAL = "RESULT_INSUFFICIENT_MATERIAL"
    VOCAB_RESULT_SEVENTYFIVE_MOVES = "RESULT_SEVENTYFIVE_MOVES"
    VOCAB_RESULT_FIVEFOLD_REPETITION = "RESULT_FIVEFOLD_REPETITION"
    VOCAB_RESULT_WINNER = "RESULT_WINNER"
    VOCAB_RESULT_ABORT = "RESULT_ABORT"
    VOCAB_NEW_GAME = "NEW_GAME"
    VOCAB_LEVEL = "LEVEL"
    VOCAB_OPENING_BOOK = "OPENING_BOOK"
    VOCAB_MODE = "MODE"
    VOCAB_MODE_GAME = "MODE_GAME"
    VOCAB_MODE_ANALYSIS = "MODE_ANALYSIS"
    VOCAB_MODE_KIBITZ = "MODE_KIBITZ"
    VOCAB_MODE_OBSERVE = "MODE_OBSERVE"
    VOCAB_MODE_REMOTE = "MODE_REMOTE"
    VOCAB_MODE_PLAY_BLACK = "MODE_PLAY_BLACK"
    VOCAB_MODE_PLAY_WHITE = "MODE_PLAY_WHITE"
    VOCAB_TIME_CONTROL_FIXED_TIME = "TIME_CONTROL_FIXED_TIME"
    VOCAB_TIME_CONTROL_BLITZ = "TIME_CONTROL_BLITZ"
    VOCAB_TIME_CONTROL_FISCHER = "TIME_CONTROL_FISCHER"
    VOCAB_SHUTDOWN = "SHUTDOWN"

    def __init__(self, localisation_id_voice=None):
        self.localisation_id = None
        self.voice_name = None
        self.voice_description = None
        self.voice_platforms = []
        self.voice_command = None
        self.voice_vocabulary = {}
        # Load voice config from JSON file.
        try:
            (localisation_id, voice) = localisation_id_voice.split(":")
            voice_filepath = os.path.join(os.path.dirname(__file__), "voices", localisation_id + ".json")
            logging.debug("Loading voice file [%s]", voice_filepath)
            with open(voice_filepath, "r") as fp:
                localisation_json = json.load(fp)
                if localisation_json:
                    voices_json = localisation_json["voices"]
                    for voice_json in voices_json:
                        voice_name = voice_json["name"]
                        voice_platforms = voice_json["platforms"]
                        if voice_name and voice_name==voice and voice_platforms.count(platform.system()) > 0:
                            self.localisation_id = localisation_id
                            self.voice_name = voice
                            self.voice_description = voice_json["description"]
                            self.voice_platforms = voice_json["platforms"]
                            self.voice_command = voice_json["command"]
                            self.voice_vocabulary = voice_json["vocabulary"]
        except:
            logging.exception("Unexpected error")

    def vocabulary_color(self, color):
        if color.lower() == ChessTalkerVoice.COLOR_WHITE:
            return self.vocabulary_white()
        else:
            return self.vocabulary_black()

    def vocabulary_piece(self, piece):
        if piece.upper() == ChessTalkerVoice.PIECE_KING:
            return self.vocabulary_king()
        elif piece.upper() == ChessTalkerVoice.PIECE_QUEEN:
            return self.vocabulary_queen()
        elif piece.upper() == ChessTalkerVoice.PIECE_BISHOP:
            return self.vocabulary_bishop()
        elif piece.upper() == ChessTalkerVoice.PIECE_KNIGHT:
            return self.vocabulary_knight()
        elif piece.upper() == ChessTalkerVoice.PIECE_ROOK:
            return self.vocabulary_rook()
        else:
            return self.vocabulary_pawn()

    def vocabulary_white(self):
        return self.voice_vocabulary[ChessTalkerVoice.VOCAB_WHITE]

    def vocabulary_black(self):
        return self.voice_vocabulary[ChessTalkerVoice.VOCAB_BLACK]

    def vocabulary_pawn(self):
        return self.voice_vocabulary[ChessTalkerVoice.VOCAB_PAWN]

    def vocabulary_rook(self):
        return self.voice_vocabulary[ChessTalkerVoice.VOCAB_ROOK]

    def vocabulary_knight(self):
        return self.voice_vocabulary[ChessTalkerVoice.VOCAB_KNIGHT]

    def vocabulary_bishop(self):
        return self.voice_vocabulary[ChessTalkerVoice.VOCAB_BISHOP]

    def vocabulary_queen(self):
        return self.voice_vocabulary[ChessTalkerVoice.VOCAB_QUEEN]

    def vocabulary_king(self):
        return self.voice_vocabulary[ChessTalkerVoice.VOCAB_KING]

    def say_castles_kingside(self, color):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_CASTLES_KINGSIDE].replace("$(COLOR)", self.vocabulary_color(color))
        return self.say_text(text)

    def say_castles_queenside(self, color):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_CASTLES_QUEENSIDE].replace("$(COLOR)", self.vocabulary_color(color))
        return self.say_text(text)

    def say_captures(self, attacking_piece, captured_piece):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_CAPTURES].replace("$(ATTACKING_PIECE)", self.vocabulary_piece(attacking_piece)).replace("$(CAPTURED_PIECE)", self.vocabulary_piece(captured_piece))
        return self.say_text(text)

    def say_check(self):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_CHECK]
        return self.say_text(text)

    def say_promotion(self, piece):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_PROMOTION_TO].replace("$(PIECE)", self.vocabulary_piece(piece))
        return self.say_text(text)

    def say_checkmate(self):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_RESULT_CHECKMATE]
        return self.say_text(text)

    def say_stalemate(self):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_RESULT_STALEMATE]
        return self.say_text(text)

    def say_draw(self):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_RESULT_DRAW]
        return self.say_text(text)

    def say_draw_seventyfive_moves(self):
        self.say_draw()
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_RESULT_SEVENTYFIVE_MOVES]
        return self.say_text(text)

    def say_draw_insufficient_material(self):
        self.say_draw()
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_RESULT_INSUFFICIENT_MATERIAL]
        return self.say_text(text)

    def say_draw_fivefold_repetition(self):
        self.say_draw()
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_RESULT_FIVEFOLD_REPETITION]
        return self.say_text(text)

    def say_winner(self, color):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_RESULT_WINNER].replace("$(COLOR)", self.vocabulary_color(color))
        return self.say_text(text)

    def say_time_control_fixed_time(self, seconds_per_move):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_TIME_CONTROL_FIXED_TIME].replace("$(SECONDS_PER_MOVE)", str(seconds_per_move))
        return self.say_text(text)

    def say_time_control_blitz(self, minutes_per_game):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_TIME_CONTROL_BLITZ].replace("$(MINUTES_PER_GAME)", str(minutes_per_game))
        return self.say_text(text)

    def say_time_control_fischer(self, minutes_per_game, fischer_increment):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_TIME_CONTROL_FISCHER].replace("$(MINUTES_PER_GAME)", str(minutes_per_game)).replace("$(FISCHER_INCREMENT)", str(fischer_increment))
        return self.say_text(text)

    def say_out_of_time(self, color):
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_RESULT_TIME_CONTROL].replace("$(COLOR)", self.vocabulary_color(color))
        return self.say_text(text)

    def say_new_game(self):
        """Announce a new game"""
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_NEW_GAME]
        return self.say_text(text)

    def say_game_aborted(self):
        """Announce game aborted"""
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_RESULT_ABORT]
        return self.say_text(text)

    def say_level(self, level):
        """Announce a level setting, eg. Level 5"""
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_LEVEL].replace("$(LEVEL)", str(level))
        return self.say_text(text)

    def say_opening_book(self, book):
        """Announce an opening book setting"""
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_OPENING_BOOK].replace("$(BOOK)", book)
        return self.say_text(text)

    def say_mode(self, mode):
        """Announce an mode setting"""
        modeVocab = None
        if mode == Mode.GAME:
            modeVocab = self.voice_vocabulary[ChessTalkerVoice.VOCAB_MODE_GAME]
        elif mode == Mode.ANALYSIS:
            modeVocab = self.voice_vocabulary[ChessTalkerVoice.VOCAB_MODE_ANALYSIS]
        elif mode == Mode.KIBITZ:
            modeVocab = self.voice_vocabulary[ChessTalkerVoice.VOCAB_MODE_KIBITZ]
        elif mode == Mode.OBSERVE:
            modeVocab = self.voice_vocabulary[ChessTalkerVoice.VOCAB_MODE_OBSERVE]
        elif mode == Mode.REMOTE:
            modeVocab = self.voice_vocabulary[ChessTalkerVoice.VOCAB_MODE_REMOTE]
        elif mode == GameMode.PLAY_BLACK:
            modeVocab = self.voice_vocabulary[ChessTalkerVoice.VOCAB_MODE_PLAY_BLACK]
        elif mode == GameMode.PLAY_WHITE:
            modeVocab = self.voice_vocabulary[ChessTalkerVoice.VOCAB_MODE_PLAY_WHITE]

        if modeVocab:
            text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_MODE].replace("$(MODE)", modeVocab)
            return self.say_text(text)

        return None

    def say_shutdown(self):
        """Announce system shutdown"""
        text = self.voice_vocabulary[ChessTalkerVoice.VOCAB_SHUTDOWN]
        return self.say_text(text)

    def say_position(self, position):
        """Say a square position, eg. a3"""
        # logging.debug("Saying position [%s]", position)
        if len(position) == 2:
            pos_file = position[0].lower()
            pos_rank = position[1]
            if pos_file >= "a" and pos_file <= "h" and pos_rank >= "1" and pos_rank <= "8":
                text = ""
                if pos_file == "a":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_FILE_A]
                if pos_file == "b":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_FILE_B]
                if pos_file == "c":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_FILE_C]
                if pos_file == "d":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_FILE_D]
                if pos_file == "e":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_FILE_E]
                if pos_file == "f":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_FILE_F]
                if pos_file == "g":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_FILE_G]
                if pos_file == "h":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_FILE_H]
                if pos_rank == "1":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_RANK_1]
                if pos_rank == "2":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_RANK_2]
                if pos_rank == "3":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_RANK_3]
                if pos_rank == "4":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_RANK_4]
                if pos_rank == "5":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_RANK_5]
                if pos_rank == "6":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_RANK_6]
                if pos_rank == "7":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_RANK_7]
                if pos_rank == "8":
                    text = text + self.voice_vocabulary[ChessTalkerVoice.VOCAB_RANK_8]
                return self.say_text(text)
        return -1  # Error - Unrecognised board position

    def say_text(self, text):
        """Feed the given text as-is into the TTS engine"""
        cmd = self.voice_command.replace("$(TEXT)", "\"" + text + "\"")
        # print("cmd=[" + cmd + "]")
        return subprocess.call(cmd, shell=True)

    def say_move(self, move, game):
        """
        Takes a chess.Move instance and a chess.BitBoard instance and speaks the move.
        """
        moveText = move.uci()
        from_square = moveText[0:2]
        to_square = moveText[2:4]
        logging.debug("say_move: Saying move [%s]", moveText)

        # Game board is currently in the POST-move state - get anything we need from this state before we look at the previous state.
        is_check = game.is_check()
        is_checkmate = game.is_checkmate()
        is_stalemate = game.is_stalemate()
        is_game_over = game.is_game_over()
        is_insufficient_material = game.is_insufficient_material()
        is_seventyfive_moves = game.is_seventyfive_moves()
        is_fivefold_repetition = game.is_fivefold_repetition()
        # logging.debug("say_move: POST-move game state: %s", str(game))
        # Pop to the previous game state, so we can determine the pieces on the from/to squares.
        game.pop()
        color_moved = ChessTalkerVoice.COLOR_WHITE if game.turn == chess.WHITE else ChessTalkerVoice.COLOR_BLACK
        moveTextSAN = game.san(move)
        # logging.debug("say_move: PRE-move game state: %s", str(game))
        # Find the Piece on the from-square.
        from_square_idx = chess.SQUARE_NAMES.index(from_square)
        from_square_piece = game.piece_at(from_square_idx)
        # Find the Piece on the to-square (if any).
        to_square_idx = chess.SQUARE_NAMES.index(to_square)
        to_square_piece = game.piece_at(to_square_idx)

        if moveTextSAN.startswith("O-O-O"):
            self.say_castles_queenside(color_moved)
        elif moveTextSAN.startswith("O-O"):
            self.say_castles_kingside(color_moved)
        else:
            # Short notation speech
            spoken_san = moveTextSAN
            for k, v in SPOKEN_PIECE_SOUNDS.items():
                spoken_san = spoken_san.replace(k, v)
            self.say_text(spoken_san)

            # Commented out code announces move in longer form
            # if from_square_piece and to_square_piece:
            #     # Announce capture.
            #     self.say_captures(str(from_square_piece), str(to_square_piece))
            # else:
            #     # Announce piece moved.
            #     self.say_text(self.vocabulary_piece(str(from_square_piece)))
            # # Announce the move itself.
            # self.say_position(from_square)
            # self.say_position(to_square)

            # Announce promotion if necessary.
            if move.promotion:
                self.say_promotion(moveText[4])

        if is_game_over:
            if is_checkmate:
                self.say_checkmate()
                self.say_winner(color_moved)
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
            # Announce check if necessary.
            self.say_check()


def usage():
    print("python __init__.py [--localisations] [--voices] [--test]")
    print("    --localisations     Display a list of all localisations available")
    print("    --voices            Display a list of all voices available for the current platform")
    print("    --test              Test the chess vocabulary of all voices available for the current platform")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "--test":
            # Test all voices in all 'voices/*.json' config files.
            localisations = ChessTalker.localisations()
            for localisation in localisations:
                localisation_id = localisation.split(":")[0]
                print("Testing localisation: " + localisation)
                voices = ChessTalker.voices(localisation_id)
                for voice in voices:
                    print("    Testing voice: " + voice)
                    # Create a ChessTalkerVoice instance and test all vocabulary.
                    chesstalker = ChessTalkerVoice(localisation_id + ":" + voice)
                    chesstalker.say_text("Hello chess-lovers")
                    chesstalker.say_position("a1")
                    chesstalker.say_position("b2")
                    chesstalker.say_position("c3")
                    chesstalker.say_position("d4")
                    chesstalker.say_position("e5")
                    chesstalker.say_position("f6")
                    chesstalker.say_position("g7")
                    chesstalker.say_position("h8")
                    chesstalker.say_new_game()
                    chesstalker.say_castles_kingside(ChessTalkerVoice.COLOR_WHITE)
                    chesstalker.say_castles_kingside(ChessTalkerVoice.COLOR_BLACK)
                    chesstalker.say_castles_queenside(ChessTalkerVoice.COLOR_WHITE)
                    chesstalker.say_castles_queenside(ChessTalkerVoice.COLOR_BLACK)
                    chesstalker.say_captures(ChessTalkerVoice.PIECE_QUEEN, ChessTalkerVoice.PIECE_KNIGHT)
                    chesstalker.say_captures(ChessTalkerVoice.PIECE_KING, ChessTalkerVoice.PIECE_PAWN)
                    chesstalker.say_check()
                    chesstalker.say_promotion(ChessTalkerVoice.PIECE_ROOK)
                    chesstalker.say_promotion(ChessTalkerVoice.PIECE_KNIGHT)
                    chesstalker.say_promotion(ChessTalkerVoice.PIECE_BISHOP)
                    chesstalker.say_promotion(ChessTalkerVoice.PIECE_QUEEN)
                    chesstalker.say_checkmate()
                    chesstalker.say_stalemate()
                    chesstalker.say_draw()
                    chesstalker.say_draw_fivefold_repetition()
                    chesstalker.say_draw_insufficient_material()
                    chesstalker.say_draw_seventyfive_moves()
                    chesstalker.say_level(0)
                    chesstalker.say_level(1)
                    chesstalker.say_level(2)
                    chesstalker.say_level(3)
                    chesstalker.say_level(4)
                    chesstalker.say_level(5)
                    chesstalker.say_level(6)
                    chesstalker.say_level(7)
                    chesstalker.say_level(8)
                    chesstalker.say_level(9)
                    chesstalker.say_level(10)
                    chesstalker.say_level(11)
                    chesstalker.say_level(12)
                    chesstalker.say_level(13)
                    chesstalker.say_level(14)
                    chesstalker.say_level(15)
                    chesstalker.say_level(16)
                    chesstalker.say_level(17)
                    chesstalker.say_level(18)
                    chesstalker.say_level(19)
                    chesstalker.say_level(20)
                    chesstalker.say_opening_book("fun")
                    chesstalker.say_opening_book("anand")
                    chesstalker.say_mode(Mode.GAME)
                    chesstalker.say_mode(Mode.ANALYSIS)
                    chesstalker.say_mode(Mode.OBSERVE)
                    chesstalker.say_mode(Mode.REMOTE)
                    chesstalker.say_mode(Mode.KIBITZ)
                    chesstalker.say_mode(GameMode.PLAY_WHITE)
                    chesstalker.say_mode(GameMode.PLAY_BLACK)
                    chesstalker.say_time_control_fixed_time(1)
                    chesstalker.say_time_control_fixed_time(3)
                    chesstalker.say_time_control_blitz(1)
                    chesstalker.say_time_control_blitz(3)
                    chesstalker.say_time_control_fischer(1, 1)
                    chesstalker.say_time_control_fischer(3, 1)
                    chesstalker.say_game_aborted()
                    chesstalker.say_out_of_time(ChessTalkerVoice.COLOR_BLACK)
                    chesstalker.say_out_of_time(ChessTalkerVoice.COLOR_WHITE)
                    chesstalker.say_shutdown()
        elif sys.argv[1] == "--localisations":
            # List all localisations found in the voices directory.
            print("Showing available localisations")
            localisations = ChessTalker.localisations()
            for localisation in localisations:
                print(localisation)
        elif sys.argv[1] == "--voices":
            # List voices for each localisation, and the platforms supported.
            print("Showing available voices for platform: " + platform.system())
            localisations = ChessTalker.localisations()
            for localisation in localisations:
                (localisation_id, localisation_language) = localisation.split(":")
                voices = ChessTalker.voices(localisation_id)
                for voice in voices:
                    print(localisation_id + ":" + voice)
        else:
            print("Error: Unrecognised option!")
            usage()
    else:
        usage()
