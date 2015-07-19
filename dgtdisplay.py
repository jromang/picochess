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


class DGTDisplay(Observable, Display, threading.Thread):

    def __init__(self, enable_board_leds=False, enable_dgt_3000=False, enable_dgt_clock_beep=True):
        super(DGTDisplay, self).__init__()
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
            Display.show(Dgt.DISPLAY_MOVE, move=self.last_move, fen=self.last_fen, beep=self.enable_dgt_clock_beep)

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_to_move = chess.WHITE if self.setup_to_move == chess.BLACK else chess.BLACK
            to_move = PlayMode.PLAY_WHITE if self.setup_to_move == chess.WHITE else PlayMode.PLAY_BLACK
            Display.show(Dgt.DISPLAY_TEXT, text=to_move.value, xl=None, beep=True)

    def process_button1(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            if self.display_move:
                if bool(self.hint_move):
                    Display.show(Dgt.DISPLAY_MOVE, move=self.hint_move, fen=self.hint_fen, beep=self.enable_dgt_clock_beep)
                else:
                    Display.show(Dgt.DISPLAY_TEXT, text="none", xl=None, beep=False)
            else:
                if self.mate is None:
                    sc = 'none' if self.score is None else str(self.score).rjust(6)
                else:
                    sc = 'm ' + str(self.mate)
                Display.show(Dgt.DISPLAY_TEXT, text=sc, xl=None, beep=True)
            self.display_move = not self.display_move

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_reverse_orientation = not self.setup_reverse_orientation
            orientation_xl = "b    w" if self.setup_reverse_orientation else "w    b"
            orientation = " b     w" if self.setup_reverse_orientation else " w     b"
            Display.show(Dgt.DISPLAY_TEXT, text=orientation, xl=orientation_xl, beep=True)

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
            if self.engine_status == EngineStatus.THINK and self.mode == Mode.GAME:
                self.fire(Event.STOP_SEARCH)
            else:
                self.fire(Event.CHANGE_PLAYMODE)

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            Display.show(Dgt.DISPLAY_TEXT, text="scan", xl=None, beep=True)
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
                Display.show(Dgt.DISPLAY_TEXT, text="bad pos", xl="badpos", beep=True)

    def process_button3(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            mode_list = list(iter(Mode))
            self.mode_index += 1
            if self.mode_index >= len(mode_list):
                self.mode_index = 0
            mode_new = mode_list[self.mode_index]
            self.fire(Event.SET_MODE, mode=mode_new)

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            Display.show(Dgt.DISPLAY_TEXT, text="reboot", xl=None, beep=True)
            subprocess.Popen(["sudo", "reboot"])

    def process_button4(self):
        # self.dgt_clock_menu = Menu.self.dgt_clock_menu.value+1
        # print(self.dgt_clock_menu)
        # print(self.dgt_clock_menu.value)
        try:
            self.dgt_clock_menu = Menu(self.dgt_clock_menu.value+1)
        except ValueError:
            self.dgt_clock_menu = Menu(1)

        msg = 'error'
        if self.dgt_clock_menu == Menu.GAME_MENU:
            msg = 'game'
        elif self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            msg = 'position'
        elif self.dgt_clock_menu == Menu.ENGINE_MENU:
            msg = 'engine'
        elif self.dgt_clock_menu == Menu.SETTINGS_MENU:
            msg = 'system'
        Display.show(Dgt.DISPLAY_TEXT, text=msg, xl=msg[:6], beep=True)

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
                        # Display the move
                        Display.show(Dgt.DISPLAY_MOVE, move=message.move, fen=message.fen, beep=self.enable_dgt_clock_beep)
                        Display.show(Dgt.LIGHT_SQUARES, squares=(uci_move[0:2], uci_move[2:4]), enable_board_leds=self.enable_board_leds)
                        break
                    if case(Message.START_NEW_GAME):
                        Display.show(Dgt.DISPLAY_TEXT, text="new game", xl="newgam", beep=self.enable_dgt_clock_beep)
                        Display.show(Dgt.LIGHT_CLEAR, enable_board_leds=self.enable_board_leds)
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
                        Display.show(Dgt.DISPLAY_TEXT, text="ok", xl=None, beep=self.enable_dgt_clock_beep)
                        Display.show(Dgt.LIGHT_CLEAR, enable_board_leds=self.enable_board_leds)
                        self.display_move = False
                        break
                    if case(Message.USER_MOVE):
                        self.display_move = False
                        Display.show(Dgt.DISPLAY_TEXT, text="ok", xl=None, beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.REVIEW_MODE_MOVE):
                        self.last_move = message.move
                        self.last_fen = message.fen
                        self.display_move = False
                        Display.show(Dgt.DISPLAY_TEXT, text="ok", xl=None, beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.LEVEL):
                        level = str(message.level)
                        Display.show(Dgt.DISPLAY_TEXT, text="level " + level, xl="lvl " + level, beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.TIME_CONTROL):
                        Display.show(Dgt.DISPLAY_TEXT, text=message.time_control_string, xl=None, beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.OPENING_BOOK):
                        book_name = message.book[0]
                        Display.show(Dgt.DISPLAY_TEXT, text=book_name, xl=None, beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.USER_TAKE_BACK):
                        Display.show(Dgt.DISPLAY_TEXT, text="takeback", xl="takbak", beep=self.enable_dgt_clock_beep)
                        self.display_move = False
                        break
                    if case(Message.GAME_ENDS):
                        # time.sleep(3)  # Let the move displayed on clock
                        Display.show(Dgt.DISPLAY_TEXT, text=message.result.value, xl=None, beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.INTERACTION_MODE):
                        self.mode = message.mode
                        Display.show(Dgt.DISPLAY_TEXT, text=message.mode.value, xl=None, beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.PLAY_MODE):
                        pm = message.play_mode.value
                        Display.show(Dgt.DISPLAY_TEXT, text=pm, xl=pm[:6], beep=self.enable_dgt_clock_beep)
                        break
                    if case(Message.SCORE):
                        self.score = message.score
                        self.mate = message.mate
                        if message.interaction_mode == Mode.KIBITZ:
                            Display.show(Dgt.DISPLAY_TEXT, text=str(self.score).rjust(6), xl=None, beep=False)
                        break
                    if case(Message.BOOK_MOVE):
                        self.score = None
                        self.mate = None
                        self.display_move = False
                        Display.show(Dgt.DISPLAY_TEXT, text="book", xl=None, beep=False)
                        break
                    if case(Message.NEW_PV):
                        self.hint_move = message.pv[0]
                        self.hint_fen = message.fen
                        if message.interaction_mode == Mode.ANALYSIS:
                            Display.show(Dgt.DISPLAY_MOVE, move=self.hint_move, fen=self.hint_fen, beep=False)
                        break
                    if case(Message.SEARCH_STARTED):
                        text = 'Search think started' if message.engine_status == EngineStatus.THINK else 'Search ponder started'
                        self.engine_status = message.engine_status
                        logging.info(text)
                        break
                    if case(Message.SEARCH_STOPPED):
                        text = 'Search already stopped' if self.engine_status == EngineStatus.WAIT else 'Search stopped'
                        self.engine_status = EngineStatus.WAIT
                        logging.info(text)
                        break
                    if case(Message.RUN_CLOCK):
                        # @todo Make this code independent from DGT Hex codes => more abstract
                        tc = message.time_control
                        time_left = int(tc.clock_time[chess.WHITE])
                        time_right = int(tc.clock_time[chess.BLACK])
                        side = 0x01 if (message.turn == chess.WHITE) != self.flip_board else 0x02
                        if tc.mode == ClockMode.FIXED_TIME:
                            side = 0x02
                            time_right = tc.seconds_per_move
                        if self.flip_board:
                            time_left, time_right = time_right, time_left
                        Display.show(Dgt.CLOCK_START, time_left=time_left, time_right=time_right, side=side)
                        break
                    if case(Message.STOP_CLOCK):
                        Display.show(Dgt.CLOCK_STOP)
                        break
                    if case(Message.BUTTON_PRESSED):
                        button = int(message.button)
                        if button == 0:
                            self.process_button0()
                        elif button == 1:
                            self.process_button1()
                        elif button == 2:
                            self.process_button2()
                        elif button == 3:
                            self.process_button3()
                        elif button == 4:
                            self.process_button4()
                        break
                    if case(Message.DGT_FEN):
                        fen = message.fen
                        if self.flip_board:  # Flip the board if needed
                            fen = fen[::-1]
                        if fen == "RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr":  # Check if we have to flip the board
                            logging.debug('Flipping the board')
                            # Flip the board
                            self.flip_board = not self.flip_board
                            # set standard for setup orientation too
                            self.setup_reverse_orientation = self.flip_board
                            fen = fen[::-1]
                        logging.debug("DGT-Fen: " + fen)
                        self.dgt_fen = fen

                        # Fire the appropriate event
                        if fen in level_map:  # User sets level
                            level = level_map.index(fen)
                            self.fire(Event.LEVEL, level=level)
                        elif fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR":  # New game
                            logging.debug("New game")
                            self.fire(Event.NEW_GAME)
                        elif fen in book_map:  # Choose opening book
                            book_index = book_map.index(fen)
                            logging.debug("Opening book [%s]", get_opening_books()[book_index])
                            self.fire(Event.OPENING_BOOK, book=get_opening_books()[book_index])
                        elif fen in mode_map:  # Set interaction mode
                            logging.debug("Interaction mode [%s]", mode_map[fen])
                            self.fire(Event.SET_MODE, mode=mode_map[fen])
                        elif fen in time_control_map:
                            logging.debug("Time control [%s]", time_control_map[fen].mode)
                            self.fire(Event.SET_TIME_CONTROL, time_control=time_control_map[fen],
                                      time_control_string=dgt_xl_time_control_list[list(time_control_map.keys()).index(fen)])
                        elif fen in shutdown_map:
                            self.fire(Event.SHUTDOWN)
                            Display.show(Dgt.DISPLAY_TEXT, text="poweroff", xl="powoff", beep=self.enable_dgt_clock_beep)
                        else:
                            logging.debug("Fire Event.Fen with " + fen)
                            self.fire(Event.FEN, fen=fen)
                    if case():  # Default
                        pass
            except queue.Empty:
                pass
