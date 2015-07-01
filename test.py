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
import queue
import chess
import time

from timecontrol import *
from collections import OrderedDict
from utilities import *


level_map = ("rnbqkbnr/pppppppp/q7/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/1q6/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/2q5/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/3q4/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/4q3/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/5q2/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/6q1/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/7q/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/q7/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/1q6/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/2q5/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/3q4/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/4q3/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/5q2/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/6q1/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/7q/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/q7/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/1q6/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/2q5/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/3q4/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/8/4q3/8/PPPPPPPP/RNBQKBNR")

book_map = ("rnbqkbnr/pppppppp/8/8/8/q7/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/1q6/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/2q5/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/3q4/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/4q3/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/5q2/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/6q1/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/7q/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/7q/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/6q1/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/5q2/8/PPPPPPPP/RNBQKBNR")

shutdown_map = ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQQBNR", "8/8/8/8/8/8/8/3QQ3", "3QQ3/8/8/8/8/8/8/8")

mode_map = {"rnbqkbnr/pppppppp/8/Q7/8/8/PPPPPPPP/RNBQKBNR": Mode.GAME,
            "rnbqkbnr/pppppppp/8/1Q6/8/8/PPPPPPPP/RNBQKBNR": Mode.ANALYSIS,
            "rnbqkbnr/pppppppp/8/2Q5/8/8/PPPPPPPP/RNBQKBNR": Mode.KIBITZ,
            "rnbqkbnr/pppppppp/8/3Q4/8/8/PPPPPPPP/RNBQKBNR": Mode.OBSERVE,
            "rnbqkbnr/pppppppp/8/4Q3/8/8/PPPPPPPP/RNBQKBNR": Mode.REMOTE}

play_map = {
            "rnbq1bnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": PlayMode.PLAY_BLACK,  # Player plays black
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQ1BNR": PlayMode.PLAY_WHITE,  # Player plays white
            "RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbq1bnr": PlayMode.PLAY_BLACK,  # Player plays black (reversed board)
            "RNBQ1BNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr": PlayMode.PLAY_WHITE}  # Player plays white (reversed board)

time_control_map = OrderedDict([
("rnbqkbnr/pppppppp/Q7/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=1)),
("rnbqkbnr/pppppppp/1Q6/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=3)),
("rnbqkbnr/pppppppp/2Q5/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=5)),
("rnbqkbnr/pppppppp/3Q4/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=10)),
("rnbqkbnr/pppppppp/4Q3/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=15)),
("rnbqkbnr/pppppppp/5Q2/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=30)),
("rnbqkbnr/pppppppp/6Q1/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=60)),
("rnbqkbnr/pppppppp/7Q/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FIXED_TIME, seconds_per_move=120)),
("rnbqkbnr/pppppppp/8/8/Q7/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=1)),
("rnbqkbnr/pppppppp/8/8/1Q6/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=3)),
("rnbqkbnr/pppppppp/8/8/2Q5/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=5)),
("rnbqkbnr/pppppppp/8/8/3Q4/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=10)),
("rnbqkbnr/pppppppp/8/8/4Q3/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=15)),
("rnbqkbnr/pppppppp/8/8/5Q2/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=30)),
("rnbqkbnr/pppppppp/8/8/6Q1/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=60)),
("rnbqkbnr/pppppppp/8/8/7Q/8/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.BLITZ, minutes_per_game=90)),
("rnbqkbnr/pppppppp/8/8/8/Q7/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=3, fischer_increment=2)),
("rnbqkbnr/pppppppp/8/8/8/1Q6/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=4, fischer_increment=2)),
("rnbqkbnr/pppppppp/8/8/8/2Q5/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=5, fischer_increment=3)),
("rnbqkbnr/pppppppp/8/8/8/3Q4/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=5, fischer_increment=5)),
("rnbqkbnr/pppppppp/8/8/8/5Q2/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=25, fischer_increment=5)),
("rnbqkbnr/pppppppp/8/8/8/4Q3/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=15, fischer_increment=5)),
("rnbqkbnr/pppppppp/8/8/8/6Q1/PPPPPPPP/RNBQKBNR", TimeControl(ClockMode.FISCHER, minutes_per_game=90, fischer_increment=30))
])

dgt_xl_time_control_list = ["mov  1", "mov  3", "mov  5", "mov 10", "mov 15", "mov 30", "mov 60", "mov120",
                            "bl   1", "bl   3", "bl   5", "bl  10", "bl  15", "bl  30", "bl  60", "bl  90",
                            "f 3  2", "f 4  2", "f 5  3", "f 5  5", "f25  5", "f15  5", "f90 30"]

class DGTBoard(Observable, Display, threading.Thread):

    def __init__(self, device, enable_board_leds=False, enable_dgt_3000=False, enable_dgt_clock_beep=True):
        super(DGTBoard, self).__init__()
        self.flip_board = False
        # self.flip_clock = None

        self.setup_to_move = chess.WHITE
        self.setup_reverse_orientation = False
        self.dgt_fen = None

        self.enable_board_leds = enable_board_leds
        self.enable_dgt_3000 = enable_dgt_3000
        self.enable_dgt_clock_beep = enable_dgt_clock_beep
        self.dgt_clock_menu = Menu.GAME_MENU
        self.last_move = None
        self.last_fen = None
        self.hint_move = chess.Move.null()
        self.hint_fen = None
        self.score = None
        self.mate = None
        self.display_move = False
        self.mode_index = 0
        self.mode = Mode.GAME
        self.engine_status = EngineStatus.WAIT

    def process_button0(self):
        if self.dgt_clock_menu == Menu.GAME_MENU and self.last_move:
            self.display_move_on_dgt(self.last_move, self.last_fen, self.enable_dgt_clock_beep)

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_to_move = chess.WHITE if self.setup_to_move == chess.BLACK else chess.BLACK
            to_move = PlayMode.PLAY_WHITE if self.setup_to_move == chess.WHITE else PlayMode.PLAY_BLACK
            self.display_on_dgt_clock(to_move.value, beep=True)

    def process_button1(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            if self.display_move:
                if self.hint_fen is None:
                    self.display_on_dgt_clock('none')
                else:
                    self.display_move_on_dgt(self.hint_move, self.hint_fen, self.enable_dgt_clock_beep)
            else:
                if self.mate is None:
                    sc = 'none' if self.score is None else str(self.score).rjust(6)
                else:
                    sc = 'm ' + str(self.mate)
                self.display_on_dgt_clock(sc, beep=True)
            self.display_move = not self.display_move

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_reverse_orientation = not self.setup_reverse_orientation
            orientation = "b    w" if self.setup_reverse_orientation else "w    b"
            self.display_on_dgt_xl(orientation, beep=True)
            orientation = "b      w" if self.setup_reverse_orientation else "w      b"
            self.display_on_dgt_3000(orientation, beep=True)

    def process_button2(self):

        def complete_dgt_fen(fen):
            # fen = str(self.setup_chessboard.fen())
            can_castle = False
            castling_fen = ''
            bit_board = chess.Board(fen)

            if bit_board.piece_at(chess.E1) == chess.Piece.from_symbol("K") and bit_board.piece_at(chess.H1) == chess.Piece.from_symbol("R"):
                can_castle = True
                castling_fen += 'K'

            if bit_board.piece_at(chess.E1) == chess.Piece.from_symbol("K") and bit_board.piece_at(chess.A1) == chess.Piece.from_symbol("R"):
                can_castle = True
                castling_fen += 'Q'

            if bit_board.piece_at(chess.E8) == chess.Piece.from_symbol("k") and bit_board.piece_at(chess.H8) == chess.Piece.from_symbol("r"):
                can_castle = True
                castling_fen += 'k'

            if bit_board.piece_at(chess.E8) == chess.Piece.from_symbol("k") and bit_board.piece_at(chess.A8) == chess.Piece.from_symbol("r"):
                can_castle = True
                castling_fen += 'q'

            if not can_castle:
                castling_fen = '-'

            # TODO: Support fen positions where castling is not possible even if king and rook are on right squares
            return fen.replace("KQkq", castling_fen)

        if self.dgt_clock_menu == Menu.GAME_MENU:
            # make that always true, cause the "stop search" (#99) doesn't work until now
            if True or (self.engine_status == EngineStatus.WAIT):
                self.fire(Event.CHANGE_PLAYMODE)
            else:
                if self.mode == Mode.GAME:
                    # missing: do we want "stop search" or "alternative move"?
                    # self.fire(Event.STOP_SEARCH)
                    pass
                else:
                    if self.mode == Mode.OBSERVE:
                        # missing: stop/start the clock
                        pass

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.display_on_dgt_clock("scan", beep=True)
            to_move = 'w' if self.setup_to_move == chess.WHITE else 'b'
            fen = self.dgt_fen
            if self.flip_board != self.setup_reverse_orientation:
                logging.debug('Flipping the board')
                fen = fen[::-1]
            fen += " {0} KQkq - 0 1".format(to_move)
            fen = complete_dgt_fen(fen)

            if chess.Board(fen).is_valid(False):
                self.flip_board = self.setup_reverse_orientation
                self.fire(Event.SETUP_POSITION, fen=fen)
            else:
                self.display_on_dgt_clock("badpos", beep=True)

    def process_button3(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            mode_list = list(iter(Mode))
            self.mode_index += 1
            if self.mode_index >= len(mode_list):
                self.mode_index = 0
            mode_new = mode_list[self.mode_index]
            self.fire(Event.SET_MODE, mode=mode_new)

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            self.display_on_dgt_clock("reboot")
            subprocess.Popen(["sudo", "reboot"])

    def process_button4(self):
        # self.dgt_clock_menu = Menu.self.dgt_clock_menu.value+1
        # print(self.dgt_clock_menu)
        # print(self.dgt_clock_menu.value)
        try:
            self.dgt_clock_menu = Menu(self.dgt_clock_menu.value+1)
        except ValueError:
            self.dgt_clock_menu = Menu(1)

        if self.dgt_clock_menu == Menu.GAME_MENU:
            msg = 'game'
        elif self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            msg = 'position'
        elif self.dgt_clock_menu == Menu.ENGINE_MENU:
            msg = 'engine'
        elif self.dgt_clock_menu == Menu.SETTINGS_MENU:
            msg = 'system'
        self.display_on_dgt_clock(msg, beep=True)

    def run(self):
        while True:
            # Check if we have something to display
            try:
                message = self.message_queue.get_nowait()
                for case in switch(message):
                    if case(Message.COMPUTER_MOVE):
                        uci_move = message.move.uci()
                        self.last_move = message.move
                        self.hint_move = chess.Move.null() if message.ponder is None else message.ponder
                        self.hint_fen = message.game.fen()
                        # @todo LocutusOfPenguin: getting a wrong game somehow...check it!
                        # self.hint_fen = message.fen_new # game.fen() & message_fen_new should be SAME!
                        self.last_fen = message.fen
                        self.display_move = False
                        logging.info("DGT SEND BEST MOVE:"+uci_move)
                        # Stop the clock before displaying a move
                        self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
                                   0, 0, 0, 0, 0, 0,
                                   0x04 | 0x01, Clock.DGT_CMD_CLOCK_END_MESSAGE])
                        # Display the move
                        self.display_move_on_dgt(message.move, message.fen, self.enable_dgt_clock_beep)
                        self.light_squares_revelation_board((uci_move[0:2], uci_move[2:4]))
                        break
                    if case(Message.START_NEW_GAME):
                        self.display_on_dgt_xl('newgam', self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000('new game', self.enable_dgt_clock_beep)
                        self.clear_light_revelation_board()
                        self.last_move = None
                        self.hint_move = chess.Move.null()
                        self.hint_fen = None
                        self.score = None
                        self.mate = None
                        self.display_move = False
                        self.mode = Mode.GAME
                        self.dgt_clock_menu = Menu.GAME_MENU
                        self.engine_status = EngineStatus.WAIT
                        break
                    if case(Message.COMPUTER_MOVE_DONE_ON_BOARD):
                        self.display_on_dgt_clock('ok', self.enable_dgt_clock_beep)
                        self.clear_light_revelation_board()
                        self.display_move = False
                        break
                    if case(Message.USER_MOVE):
                        self.display_move = False
                        self.display_on_dgt_clock('ok', self.enable_dgt_clock_beep)
                        break
                    if case(Message.REVIEW_MODE_MOVE):
                        self.last_move = message.move
                        self.last_fen = message.fen
                        self.display_move = False
                        self.display_on_dgt_clock('ok', self.enable_dgt_clock_beep)
                        break
                    if case(Message.LEVEL):
                        level = message.level
                        self.display_on_dgt_xl('lvl ' + str(level), self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000('level '+ str(level), self.enable_dgt_clock_beep)
                        break
                    if case(Message.TIME_CONTROL):
                        self.display_on_dgt_clock(message.time_control_string)
                        break
                    if case(Message.OPENING_BOOK):
                        book_name = message.book[0]
                        self.display_on_dgt_clock(book_name, self.enable_dgt_clock_beep)
                        break
                    if case(Message.USER_TAKE_BACK):
                        self.display_on_dgt_xl('takbak', self.enable_dgt_clock_beep)
                        self.display_on_dgt_3000('takeback', self.enable_dgt_clock_beep)
                        self.display_move = False
                        break
                    if case(Message.RUN_CLOCK):
                        tc = message.time_control
                        w_hms = hours_minutes_seconds(int(tc.clock_time[chess.WHITE]))
                        b_hms = hours_minutes_seconds(int(tc.clock_time[chess.BLACK]))
                        side = 0x01 if (message.turn == chess.WHITE) != self.flip_board else 0x02
                        if tc.mode == ClockMode.FIXED_TIME:
                            side = 0x02
                            b_hms = hours_minutes_seconds(tc.seconds_per_move)
                        if self.flip_board:
                            w_hms, b_hms = b_hms, w_hms
                        self.write([Commands.DGT_CLOCK_MESSAGE, 0x0a, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_SETNRUN,
                                   w_hms[0], w_hms[1], w_hms[2], b_hms[0], b_hms[1], b_hms[2],
                                   side, Clock.DGT_CMD_CLOCK_END_MESSAGE])
                        self.write([Commands.DGT_CLOCK_MESSAGE, 0x03, Clock.DGT_CMD_CLOCK_START_MESSAGE, Clock.DGT_CMD_CLOCK_END, Clock.DGT_CMD_CLOCK_END_MESSAGE])
                        break
                    if case(Message.GAME_ENDS):
                        # time.sleep(3)  # Let the move displayed on clock
                        self.display_on_dgt_clock(message.result.value, self.enable_dgt_clock_beep)
                        break
                    if case(Message.INTERACTION_MODE):
                        self.engine_status = message.engine_status
                        self.mode = message.mode
                        self.display_on_dgt_clock(message.mode.value, self.enable_dgt_clock_beep)
                        break
                    if case(Message.PLAY_MODE):
                        self.display_on_dgt_clock(message.play_mode.value, self.enable_dgt_clock_beep)
                        break
                    if case(Message.SCORE):
                        self.score = message.score
                        self.mate = message.mate
                        if message.interaction_mode == Mode.KIBITZ:
                            self.display_on_dgt_clock(str(self.score).rjust(6), beep=False)
                        break
                    if case(Message.BOOK_MOVE):
                        self.score = None
                        self.mate = None
                        self.display_move = False
                        self.display_on_dgt_clock('book', beep=False)
                        break
                    if case(Message.NEW_PV):
                        self.hint_move = message.pv[0]
                        self.hint_fen = message.fen
                        if message.interaction_mode == Mode.ANALYSIS:
                            self.display_move_on_dgt(self.hint_move, self.hint_fen, False)
                        break
                    if case(Message.SEARCH_STARTED):
                        self.engine_status = message.engine_status
                        # logging.info('Search started')
                        break
                    if case(Message.SEARCH_STOPPED):
                        self.engine_status = message.engine_status
                        # logging.info('Search stopped')
                        break
                    if case():  # Default
                        pass
            except queue.Empty:
                pass
