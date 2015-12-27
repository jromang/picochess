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

from dgtinterface import *
import threading

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

remote_map = ("rnbqkbnr/pppppppp/8/4Q3/8/8/PPPPPPPP/RNBQKBNR")

mode_map = {"rnbqkbnr/pppppppp/8/Q7/8/8/PPPPPPPP/RNBQKBNR": Mode.GAME,
            "rnbqkbnr/pppppppp/8/1Q6/8/8/PPPPPPPP/RNBQKBNR": Mode.ANALYSIS,
            "rnbqkbnr/pppppppp/8/2Q5/8/8/PPPPPPPP/RNBQKBNR": Mode.KIBITZ,
            "rnbqkbnr/pppppppp/8/3Q4/8/8/PPPPPPPP/RNBQKBNR": Mode.OBSERVE,
            "rnbqkbnr/pppppppp/8/4Q3/8/8/PPPPPPPP/RNBQKBNR": Mode.REMOTE}

drawresign_map = OrderedDict([
    ("8/8/8/3k4/4K3/8/8/8", GameResult.RESIGN_WHITE),
    ("8/8/8/3K4/4k3/8/8/8", GameResult.RESIGN_WHITE),
    ("8/8/8/4k3/3K4/8/8/8", GameResult.RESIGN_BLACK),
    ("8/8/8/4K3/3k4/8/8/8", GameResult.RESIGN_BLACK),
    ("8/8/8/3kK3/8/8/8/8", GameResult.DRAW),
    ("8/8/8/3Kk3/8/8/8/8", GameResult.DRAW),
    ("8/8/8/8/3kK3/8/8/8", GameResult.DRAW),
    ("8/8/8/8/3Kk3/8/8/8", GameResult.DRAW)
])

time_controls = {ClockMode.FIXED_TIME: "Fixed",
                 ClockMode.BLITZ: "Blitz",
                 ClockMode.FISCHER: "Fischer"}

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


class DGTDisplay(Observable, Display, HardwareDisplay, threading.Thread):
    def __init__(self, ok_move_messages):
        super(DGTDisplay, self).__init__()
        self.ok_moves_messages = ok_move_messages

        self.setup_to_move = chess.WHITE
        self.setup_reverse_orientation = False
        self.setup_uci960 = False
        self.flip_board = False
        self.dgt_fen = None
        self.alternative = False
        self.ip = '?'  # the last two parts of the IP
        self.drawresign_fen = None
        self.draw_setup_pieces = True

        self.dgt_clock_menu = Menu.GAME_MENU
        self.last_move = chess.Move.null()
        self.last_fen = None
        self.reset_hint_and_score()
        self.mode_index = 0
        self.mode = Mode.GAME
        self.awaiting_confirm = PowerMenu.CONFIRM_NONE

        self.engine_level = 20  # Default level is 20
        self.engine_level_menu = self.engine_level
        self.n_levels = 21  # Default engine (Stockfish) has 21 playing levels
        self.engine_has_levels = False  # Not all engines support levels - assume not
        self.engine_restart = False
        self.engine_index = 0  # Dummy values .. set later
        self.engine_menu_index = 0
        self.installed_engines = None
        self.n_engines = 0

        self.book_index = 7  # Default book is 7 - book 'h'
        self.book_menu_index = 7  # Sync with above
        self.all_books = get_opening_books()
        self.n_books = len(self.all_books)
        self.book_from_fen = False

        self.time_control_mode = ClockMode.BLITZ
        self.time_control_fen_map = None
        self.build_time_control_fens()
        self.time_control_index = 10  # index for selecting new time control
        self.time_control_menu_index = 2  # index for selecting new time control
        self.time_control_fen = list(time_control_map.keys())[self.time_control_index]  # Default time control: Blitz, 5min

    def power_off(self):
        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="good bye", xl="bye", beep=BeepLevel.CONFIG, duration=0)
        self.engine_restart = True
        self.fire(Event.SHUTDOWN)

    def reboot(self):
        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="pls wait", xl="wait", beep=BeepLevel.CONFIG, duration=0)
        self.engine_restart = True
        reboot_thread = threading.Timer(3, subprocess.Popen(["sudo", "reboot"]))
        reboot_thread.start()

    def build_time_control_fens(self):
        # Build the fen map for menu selection - faster to process than full map
        self.time_control_fen_map = list(time_control_map.keys())
        fens_dirty = True
        while fens_dirty:
            fens_dirty = False
            for key in self.time_control_fen_map:
                if self.time_control_mode != time_control_map[key].mode:
                    self.time_control_fen_map.remove(key)
                    fens_dirty = True
                    break

    def reset_hint_and_score(self):
        self.hint_move = chess.Move.null()
        self.hint_fen = None
        self.score = None
        self.mate = None
        self.display_move = False

    def process_button0(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            if self.last_move:
                HardwareDisplay.show(Dgt.DISPLAY_MOVE, move=self.last_move, fen=self.last_fen, beep=BeepLevel.CONFIG, duration=1)
            else:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="no move", xl="nomove", beep=BeepLevel.CONFIG, duration=1)

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_to_move = chess.WHITE if self.setup_to_move == chess.BLACK else chess.BLACK
            to_move = PlayMode.PLAY_WHITE if self.setup_to_move == chess.WHITE else PlayMode.PLAY_BLACK
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=to_move.value, xl=None, beep=BeepLevel.YES, duration=0)

        if self.dgt_clock_menu == Menu.LEVEL_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            elif self.engine_has_levels:
                # Display current level
                level = str(self.engine_level)
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="level " + level, xl="lvl " + level, beep=BeepLevel.CONFIG, duration=0)
            else:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="no level", xl="no lvl", beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text='pico ' + version, xl='pic ' + version, beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.ENGINE_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            else:
                # Display current engine
                msg = (self.installed_engines[self.engine_index])[1]
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=msg, xl=msg[:6], beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.BOOK_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            else:
                # Display current book
                msg = (self.all_books[self.book_index])[0]
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=msg, xl=msg[:6], beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.TIME_MENU:
            # Select a time control mode
            try:
                self.time_control_mode = ClockMode(self.time_control_mode.value + 1)
            except ValueError:
                self.time_control_mode = ClockMode(1)
            self.build_time_control_fens()
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=time_controls[self.time_control_mode], xl=None, beep=BeepLevel.CONFIG, duration=0)
            self.time_control_index = 0
            self.time_control_menu_index = self.time_control_index
            self.time_control_fen = self.time_control_fen_map[self.time_control_index]

    def process_button1(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            if self.display_move:
                if bool(self.hint_move):
                    HardwareDisplay.show(Dgt.DISPLAY_MOVE, move=self.hint_move, fen=self.hint_fen,
                                         beep=BeepLevel.CONFIG, duration=1)
                else:
                    HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="no move", xl="nomove", beep=BeepLevel.NO, duration=1)
            else:
                if self.mate is None:
                    sc = 'no scr' if self.score is None else str(self.score).rjust(6)
                else:
                    sc = 'm ' + str(self.mate)
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=sc, xl=None, beep=BeepLevel.YES, duration=1)
            self.display_move = not self.display_move

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_reverse_orientation = not self.setup_reverse_orientation
            orientation_xl = "b    w" if self.setup_reverse_orientation else "w    b"
            orientation = " b     w" if self.setup_reverse_orientation else " w     b"
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=orientation, xl=orientation_xl, beep=BeepLevel.YES, duration=0)

        if self.dgt_clock_menu == Menu.LEVEL_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            elif self.engine_has_levels:
                self.engine_level_menu = ((self.engine_level_menu-1)%self.n_levels)
                level = str(self.engine_level_menu)
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="level " + level, xl="lvl " + level, beep=BeepLevel.CONFIG, duration=0)
            else:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="no level", xl="no lvl", beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=self.ip, xl=None, beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.ENGINE_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            elif self.installed_engines:
                self.engine_menu_index = ((self.engine_menu_index-1) % self.n_engines)
                msg = (self.installed_engines[self.engine_menu_index])[1]
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=msg, xl=msg[:6], beep=BeepLevel.CONFIG, duration=0)
            else:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text='error', xl=None, beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.BOOK_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            else:
                self.book_menu_index = ((self.book_menu_index-1) % self.n_books)
                msg = (self.all_books[self.book_menu_index])[0]
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=msg, xl=msg[:6], beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.TIME_MENU:
            self.time_control_menu_index -= 1
            if self.time_control_menu_index < 0:
                self.time_control_menu_index = len(self.time_control_fen_map) - 1
            msg = dgt_xl_time_control_list[list(time_control_map.keys()).index(self.time_control_fen_map[self.time_control_menu_index])]
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=msg, xl=msg, beep=BeepLevel.CONFIG, duration=0)

    def process_button2(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            if self.mode == Mode.GAME:
                if self.alternative:
                    self.fire(Event.ALTERNATIVE_MOVE)
                else:
                    self.fire(Event.STARTSTOP_THINK)
            if self.mode == Mode.REMOTE:
                self.fire(Event.STARTSTOP_THINK)
            if self.mode == Mode.OBSERVE:
                self.fire(Event.STARTSTOP_CLOCK)
            if self.mode == Mode.ANALYSIS or self.mode == Mode.KIBITZ:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="error", xl=None, beep=BeepLevel.YES, duration=0)

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="scan", xl=None, beep=BeepLevel.YES, duration=0)
            to_move = 'w' if self.setup_to_move == chess.WHITE else 'b'
            fen = self.dgt_fen
            if self.flip_board != self.setup_reverse_orientation:
                logging.debug('Flipping the board')
                fen = fen[::-1]
            fen += " {0} KQkq - 0 1".format(to_move)
            bit_board = chess.Board(fen, self.setup_uci960)
            # ask python-chess to correct the castling string
            bit_board.set_fen(bit_board.fen())
            if bit_board.is_valid():
                self.flip_board = self.setup_reverse_orientation
                self.fire(Event.SETUP_POSITION, fen=bit_board.fen(), uci960=self.setup_uci960)
            else:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="bad pos", xl="badpos", beep=BeepLevel.YES, duration=0)

        if self.dgt_clock_menu == Menu.LEVEL_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            elif self.engine_has_levels:
                if self.engine_level != self.engine_level_menu:
                    self.fire(Event.LEVEL, level=self.engine_level_menu)
                    HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="ok level", xl="ok lvl", beep=BeepLevel.CONFIG, duration=0)
            else:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="no level", xl="no lvl", beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="pwroff ?", xl="-off-", beep=BeepLevel.YES, duration=0)
            self.awaiting_confirm = PowerMenu.CONFIRM_PWR

        if self.dgt_clock_menu == Menu.ENGINE_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            elif self.installed_engines:
                # Reset level selections
                self.engine_level_menu = self.engine_level
                self.engine_has_levels = False
                # This is a handshake change so index values changed and sync'd in the response below
                self.fire(Event.NEW_ENGINE, eng=self.installed_engines[self.engine_menu_index])
                self.engine_restart = True
            else:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text='error', xl=None, beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.BOOK_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            elif self.book_index != self.book_menu_index:
                self.fire(Event.OPENING_BOOK, book=self.all_books[self.book_menu_index])

        if self.dgt_clock_menu == Menu.TIME_MENU: 
            if self.time_control_index != self.time_control_menu_index:
                self.time_control_index = self.time_control_menu_index
                self.time_control_fen = self.time_control_fen_map[self.time_control_index]
                self.fire(Event.SET_TIME_CONTROL, time_control=time_control_map[self.time_control_fen], time_control_string='ok time')

    def process_button3(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            mode_list = list(iter(Mode))
            self.mode_index += 1
            if self.mode_index >= len(mode_list):
                self.mode_index = 0
            mode_new = mode_list[self.mode_index]
            self.fire(Event.SET_MODE, mode=mode_new)

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_uci960 = not self.setup_uci960
            text = '960 yes' if self.setup_uci960 else '960 no'
            text_xl = '960yes' if self.setup_uci960 else '960 no'
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=text, xl=text_xl, beep=BeepLevel.YES, duration=0)

        if self.dgt_clock_menu == Menu.LEVEL_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            elif self.engine_has_levels:
                self.engine_level_menu = ((self.engine_level_menu+1) % self.n_levels)
                level = str(self.engine_level_menu)
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="level " + level, xl="lvl " + level, beep=BeepLevel.CONFIG, duration=0)
            else:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="no level", xl="no lvl", beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="reboot ?", xl="-boot-", beep=BeepLevel.YES, duration=0)
            self.awaiting_confirm = PowerMenu.CONFIRM_RBT

        if self.dgt_clock_menu == Menu.ENGINE_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            elif self.installed_engines:
                self.engine_menu_index = ((self.engine_menu_index+1) % self.n_engines)
                msg = (self.installed_engines[self.engine_menu_index])[1]
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=msg, xl=msg[:6], beep=BeepLevel.CONFIG, duration=0)
            else:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text='error', xl=None, beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.BOOK_MENU:
            if self.mode == Mode.REMOTE:
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=Mode.REMOTE.value, xl=None, beep=BeepLevel.CONFIG, duration=0)
            else:
                self.book_menu_index = ((self.book_menu_index+1) % self.n_books)
                msg = (self.all_books[self.book_menu_index])[0]
                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=msg, xl=msg[:6], beep=BeepLevel.CONFIG, duration=0)

        if self.dgt_clock_menu == Menu.TIME_MENU:
            self.time_control_menu_index += 1
            if self.time_control_menu_index >= len(self.time_control_fen_map):
                self.time_control_menu_index = 0
            msg = dgt_xl_time_control_list[list(time_control_map.keys()).index(self.time_control_fen_map[self.time_control_menu_index])]
            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=msg, xl=None, beep=BeepLevel.CONFIG, duration=0)

    def process_button4(self):
        # self.dgt_clock_menu = Menu.self.dgt_clock_menu.value+1
        # print(self.dgt_clock_menu)
        # print(self.dgt_clock_menu.value)
        try:
            self.dgt_clock_menu = Menu(self.dgt_clock_menu.value + 1)
        except ValueError:
            self.dgt_clock_menu = Menu(1)

        msg = 'error'
        if self.dgt_clock_menu == Menu.GAME_MENU:
            msg = 'game'
        elif self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            msg = 'position'
        elif self.dgt_clock_menu == Menu.ENGINE_MENU:
            msg = 'engine'
        elif self.dgt_clock_menu == Menu.LEVEL_MENU:
            msg = 'level'
        elif self.dgt_clock_menu == Menu.BOOK_MENU:
            msg = 'book'
        elif self.dgt_clock_menu == Menu.TIME_MENU:
            msg = "time"
        elif self.dgt_clock_menu == Menu.SETTINGS_MENU:
            msg = 'system'
        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=msg, xl=msg[:6], beep=BeepLevel.YES, duration=0)
        # Reset time control fen to match current time control
        self.time_control_mode = time_control_map[self.time_control_fen].mode
        self.time_control_selected_index = 0
        # Reset menu selections
        self.book_menu_index = self.book_index
        self.engine_menu_index = self.engine_index

    def drawresign(self):
        rnk_8, rnk_7, rnk_6, rnk_5, rnk_4, rnk_3, rnk_2, rnk_1 = self.dgt_fen.split("/")
        self.drawresign_fen = "8/8/8/" + rnk_5 + "/" + rnk_4 + "/8/8/8"

    def run(self):
        while True:
            # Check if we have something to display
            try:
                message = self.message_queue.get()
                if type(message).__name__ == 'Message':
                    logging.debug("Read message from queue: %s", message)
                for case in switch(message):
                    if case(Message.ENGINE_READY):
                        self.engine_index = self.installed_engines.index(message.eng)
                        self.engine_menu_index = self.engine_index
                        self.engine_has_levels = message.has_levels
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text='ok engin', xl="ok eng", beep=BeepLevel.CONFIG, duration=1)
                        self.engine_restart = False
                        break
                    if case(Message.ENGINE_START):
                        if message.path:
                            self.installed_engines = get_installed_engines(message.path)
                            self.n_engines = len(self.installed_engines)
                            for index in range(0, self.n_engines):
                                full_path, short = self.installed_engines[index]
                                if full_path == message.path:
                                    self.engine_index = index
                                    self.engine_menu_index = self.engine_index
                                    self.engine_has_levels = message.has_levels
                        break
                    if case(Message.ENGINE_FAIL):
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text='error', xl=None, beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.COMPUTER_MOVE):
                        move = message.result.bestmove
                        ponder = message.result.ponder
                        self.alternative = True
                        self.last_move = move
                        self.hint_move = chess.Move.null() if ponder is None else ponder
                        self.hint_fen = message.game.fen()
                        self.last_fen = message.fen
                        self.display_move = False
                        # Display the move
                        uci_move = move.uci()
                        HardwareDisplay.show(Dgt.DISPLAY_MOVE, move=move, fen=message.fen, beep=BeepLevel.CONFIG, duration=0)
                        HardwareDisplay.show(Dgt.LIGHT_SQUARES, squares=(uci_move[0:2], uci_move[2:4]))
                        break
                    if case(Message.START_NEW_GAME):
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="new game", xl="newgam", beep=BeepLevel.CONFIG, duration=1)
                        HardwareDisplay.show(Dgt.LIGHT_CLEAR)
                        self.last_move = chess.Move.null()
                        self.reset_hint_and_score()
                        self.mode = Mode.GAME
                        self.dgt_clock_menu = Menu.GAME_MENU
                        self.alternative = False
                        break
                    if case(Message.WAIT_STATE):
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="you move", xl="you mv", beep=BeepLevel.CONFIG, duration=0)
                        break
                    if case(Message.COMPUTER_MOVE_DONE_ON_BOARD):
                        if self.ok_moves_messages:
                            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="ok pico", xl="okpico", beep=BeepLevel.CONFIG, duration=1)
                        HardwareDisplay.show(Dgt.LIGHT_CLEAR)
                        self.display_move = False
                        self.alternative = False
                        break
                    if case(Message.USER_MOVE):
                        self.display_move = False
                        self.alternative = False
                        if self.ok_moves_messages:
                            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="ok user", xl="okuser", beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.REVIEW_MODE_MOVE):
                        self.last_move = message.move
                        self.last_fen = message.fen
                        self.display_move = False
                        if self.ok_moves_messages:
                            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="ok move", xl="okmove", beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.ALTERNATIVE_MOVE):
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="alt move", xl="altmov", beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.LEVEL):
                        level = str(message.level)
                        if self.engine_restart:
                            pass
                        elif self.engine_level != self.engine_level_menu:
                            self.engine_level = self.engine_level_menu
                        else:
                            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="level " + level, xl="lvl " + level,
                                                 beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.TIME_CONTROL):
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=message.time_control_string, xl=None,
                                             beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.OPENING_BOOK):
                        book_name = message.book[0]
                        self.alternative = False
                        if self.book_from_fen:
                            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=book_name, xl=None, beep=BeepLevel.CONFIG, duration=1)
                            self.book_from_fen = False
                            self.book_menu_index = self.book_index  # Not necessary but cleaner
                        if self.book_index != self.book_menu_index:
                            self.book_index = self.book_menu_index
                            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="ok book", xl="okbook", beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.USER_TAKE_BACK):
                        self.reset_hint_and_score()
                        self.alternative = False
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="takeback", xl="takbak", beep=BeepLevel.CONFIG, duration=0)
                        break
                    if case(Message.GAME_ENDS):
                        ge = message.result.value
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=ge, xl=None, beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.INTERACTION_MODE):
                        self.mode = message.mode
                        self.alternative = False
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=message.mode.value, xl=None, beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.PLAY_MODE):
                        pm = message.play_mode.value
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=pm, xl=pm[:6], beep=BeepLevel.CONFIG, duration=1)
                        break
                    if case(Message.SCORE):
                        self.score = message.score
                        self.mate = message.mate
                        if message.mode == Mode.KIBITZ:
                            HardwareDisplay.show(Dgt.DISPLAY_TEXT, text=str(self.score).rjust(6), xl=None,
                                                 beep=BeepLevel.NO, duration=1)
                        break
                    if case(Message.BOOK_MOVE):
                        self.score = None
                        self.mate = None
                        self.display_move = False
                        HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="book", xl=None, beep=BeepLevel.NO, duration=1)
                        break
                    if case(Message.NEW_PV):
                        self.hint_move = message.pv[0]
                        self.hint_fen = message.fen
                        if message.mode == Mode.ANALYSIS:
                            HardwareDisplay.show(Dgt.DISPLAY_MOVE, move=self.hint_move, fen=self.hint_fen,
                                                 beep=BeepLevel.NO, duration=0)
                        break
                    if case(Message.SYSTEM_INFO):
                        self.ip = ' '.join(message.info["ip"].split('.')[2:])
                        break
                    if case(Message.STARTUP_INFO):
                        self.book_index = message.info["book_index"]
                        self.book_menu_index = self.book_index
                    if case(Message.SEARCH_STARTED):
                        logging.debug('Search started')
                        break
                    if case(Message.SEARCH_STOPPED):
                        logging.debug('Search stopped')
                        break
                    if case(Message.RUN_CLOCK):
                        # @todo Make this code independent from DGT Hex codes => more abstract
                        tc = message.time_control
                        time_left = int(tc.clock_time[chess.WHITE])
                        if time_left < 0:
                            time_left = 0
                        time_right = int(tc.clock_time[chess.BLACK])
                        if time_right < 0:
                            time_right = 0
                        side = 0x01 if (message.turn == chess.WHITE) != self.flip_board else 0x02
                        if tc.mode == ClockMode.FIXED_TIME:
                            time_left = time_right = tc.seconds_per_move
                        if self.flip_board:
                            time_left, time_right = time_right, time_left
                        HardwareDisplay.show(Dgt.CLOCK_START, time_left=time_left, time_right=time_right, side=side)
                        break
                    if case(Message.STOP_CLOCK):
                        HardwareDisplay.show(Dgt.CLOCK_STOP)
                        break
                    if case(Message.DGT_BUTTON):
                        button = int(message.button)
                        if not (self.awaiting_confirm == PowerMenu.CONFIRM_NONE):
                            if (self.awaiting_confirm == PowerMenu.CONFIRM_PWR) and (button == 2):
                                self.power_off()
                            if (self.awaiting_confirm == PowerMenu.CONFIRM_RBT) and (button == 3):
                                self.reboot()
                            else:  # Abort!
                                self.awaiting_confirm = PowerMenu.CONFIRM_NONE   
                        if not self.engine_restart and (self.awaiting_confirm == PowerMenu.CONFIRM_NONE):
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
                        if fen == self.dgt_fen:
                            logging.debug('Ignore same fen')
                            break
                        self.dgt_fen = fen
                        self.drawresign()
                        # Fire the appropriate event
                        if fen in level_map:  # User sets level
                            level = level_map.index(fen)
                            self.engine_level = level
                            self.engine_level_menu = level
                            logging.debug("Map-Fen: New level")
                            self.fire(Event.LEVEL, level=level)
                        elif fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR":  # New game
                            logging.debug("Map-Fen: New game")
                            self.draw_setup_pieces = False
                            self.fire(Event.NEW_GAME)
                        elif fen in remote_map:  # Remote play
                            logging.debug("Map-Fen: Remote")
                            mode_new = Mode.REMOTE
                            self.fire(Event.SET_MODE, mode=mode_new)
                        elif fen in book_map:  # Choose opening book
                            self.book_index = book_map.index(fen)
                            logging.debug("Map-Fen: Opening book [%s]", get_opening_books()[self.book_index])
                            self.fire(Event.OPENING_BOOK, book=get_opening_books()[self.book_index])
                            self.book_from_fen = True
                        elif fen in mode_map:  # Set interaction mode
                            logging.debug("Map-Fen: Interaction mode [%s]", mode_map[fen])
                            self.fire(Event.SET_MODE, mode=mode_map[fen])
                        elif fen in time_control_map:
                            logging.debug("Map-Fen: Time control [%s]", time_control_map[fen].mode)
                            self.fire(Event.SET_TIME_CONTROL, time_control=time_control_map[fen],
                                      time_control_string=dgt_xl_time_control_list[
                                          list(time_control_map.keys()).index(fen)])
                            self.time_control_mode = time_control_map[fen].mode
                            self.time_control_fen = fen
                        elif fen in shutdown_map:
                            logging.debug("Map-Fen: shutdown")
                            self.power_off()
                        elif self.drawresign_fen in drawresign_map:
                            logging.debug("Map-Fen: drawresign")
                            self.fire(Event.DRAWRESIGN, result=drawresign_map[self.drawresign_fen])
                        else:
                            if self.draw_setup_pieces:
                                HardwareDisplay.show(Dgt.DISPLAY_TEXT, text="setup piece", xl="setup", beep=BeepLevel.NO, duration=0)
                                self.draw_setup_pieces = False
                            self.fire(Event.FEN, fen=fen)
                        break
                    if case(Message.DGT_CLOCK_VERSION):
                        HardwareDisplay.show(Dgt.CLOCK_VERSION, main_version=message.main_version,
                                             sub_version=message.sub_version)
                        break
                    if case(Message.DGT_CLOCK_TIME):
                        HardwareDisplay.show(Dgt.CLOCK_TIME, time_left=message.time_left, time_right=message.time_right)
                        break
                    if case(Message.DGT_SERIALNR):
                        HardwareDisplay.show(Dgt.SERIALNR)
                    if case():  # Default
                        # print(message)
                        pass
            except queue.Empty:
                pass
