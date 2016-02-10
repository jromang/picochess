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

from dgtinterface import *
import threading

level_map = ("rnbqkbnr/pppppppp/8/q7/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/1q6/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/2q5/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/3q4/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/4q3/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/5q2/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/6q1/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/8/7q/8/8/PPPPPPPP/RNBQKBNR")

book_map = ("rnbqkbnr/pppppppp/8/8/8/q7/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/1q6/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/2q5/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/3q4/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/4q3/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/5q2/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/6q1/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/8/7q/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/q7/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/1q6/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/2q5/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/3q4/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/4q3/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/5q2/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/6q1/8/PPPPPPPP/RNBQKBNR",
            "rnbqkbnr/pppppppp/8/8/7q/8/PPPPPPPP/RNBQKBNR")

shutdown_map = ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQQBNR",
                "8/8/8/8/8/8/8/3QQ3",
                "3QQ3/8/8/8/8/8/8/8")

mode_map = {"rnbqkbnr/pppppppp/8/Q7/8/8/PPPPPPPP/RNBQKBNR": Mode.NORMAL,
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

text_goodbye = Dgt.DISPLAY_TEXT(l=None, m="good bye", s="bye", beep=BeepLevel.YES, duration=0)
text_pleasewait = Dgt.DISPLAY_TEXT(l="please wait", m="pls wait", s="wait", beep=BeepLevel.YES, duration=0)
text_nomove = Dgt.DISPLAY_TEXT(l=None, m="no move", s="nomove", beep=BeepLevel.YES, duration=1)
text_wb = Dgt.DISPLAY_TEXT(l=None, m=" w     b", s="w    b", beep=BeepLevel.BUTTON, duration=0)
text_bw = Dgt.DISPLAY_TEXT(l=None, m=" b     w", s="b    w", beep=BeepLevel.BUTTON, duration=0)
text_960no = Dgt.DISPLAY_TEXT(l=None, m='960 no', s='960 no', beep=BeepLevel.BUTTON, duration=0)
text_960yes =Dgt.DISPLAY_TEXT(l=None, m='960 yes', s='960yes', beep=BeepLevel.BUTTON, duration=0)
text_picochess = Dgt.DISPLAY_TEXT(l="picoChs " + version, m='pico ' + version, s='pic ' + version, beep=BeepLevel.BUTTON, duration=0)
text_nofunction = Dgt.DISPLAY_TEXT(l="no function", m="no funct", s="nofunc", beep=BeepLevel.BUTTON, duration=0)
text_erroreng = Dgt.DISPLAY_TEXT(l='error eng', m='error', s=None, beep=BeepLevel.YES, duration=0)
text_nolevel = Dgt.DISPLAY_TEXT(l=None, m="no level", s="no lvl", beep=BeepLevel.YES, duration=0)
text_errortop = Dgt.DISPLAY_TEXT(l='error top', m='errortop', s='errtop', beep=BeepLevel.BUTTON, duration=0)
text_sidewhite = Dgt.DISPLAY_TEXT(l='side move w', m='side w', s='side w', beep=BeepLevel.BUTTON, duration=0)
text_sideblack = Dgt.DISPLAY_TEXT(l='side move b', m='side b', s='side b', beep=BeepLevel.BUTTON, duration=0)
text_scanboard = Dgt.DISPLAY_TEXT(l="scan board", m="scan", s=None, beep=BeepLevel.BUTTON, duration=0)
text_illegalpos = Dgt.DISPLAY_TEXT(l="illegal pos", m="illegal", s="badpos", beep=BeepLevel.YES, duration=0)


class DgtDisplay(Observable, DisplayMsg, threading.Thread):
    def __init__(self, ok_move_messages):
        super(DgtDisplay, self).__init__()
        self.ok_moves_messages = ok_move_messages

        self.flip_board = False
        self.dgt_fen = None
        self.alternative = False
        self.ip = '?'  # the last two parts of the IP
        self.drawresign_fen = None
        self.draw_setup_pieces = True
        self.awaiting_confirm = PowerMenu.CONFIRM_NONE

        self.last_move = chess.Move.null()
        self.last_fen = None
        self.reset_hint_and_score()

        self.setup_whitetomove_index = None
        self.setup_whitetomove_result = None
        self.setup_reverse_index = None
        self.setup_reverse_result = None
        self.setup_uci960_index = None
        self.setup_uci960_result = None

        self.top_result = None
        self.top_index = None  # @todo
        self.mode_result = None
        self.mode_index = Mode.NORMAL

        self.engine_level_result = 20  # Default level is 20
        self.engine_level_index = self.engine_level_result
        self.n_levels = 21  # Default engine (Stockfish) has 21 playing levels
        self.engine_has_levels = False  # Not all engines support levels - assume not
        self.engine_restart = False
        self.engine_result = 0  # Dummy values .. set later
        self.engine_index = 0
        self.installed_engines = None
        self.n_engines = 0

        self.book_result = 7  # Default book is 7 - book 'h'
        self.book_index = 7  # Sync with above
        self.all_books = get_opening_books()
        self.n_books = len(self.all_books)

        self.system_index = Settings.VERSION

        self.time_mode_result = None
        self.time_mode_index = TimeMode.BLITZ

        self.time_control_fixed_index = 0
        self.time_control_blitz_index = 2  # Default time control: Blitz, 5min
        self.time_control_fisch_index = 0
        self.time_control_fixed_map = OrderedDict([
            ("rnbqkbnr/pppppppp/Q7/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FIXED, seconds_per_move=1)),
            ("rnbqkbnr/pppppppp/1Q6/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FIXED, seconds_per_move=3)),
            ("rnbqkbnr/pppppppp/2Q5/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FIXED, seconds_per_move=5)),
            ("rnbqkbnr/pppppppp/3Q4/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FIXED, seconds_per_move=10)),
            ("rnbqkbnr/pppppppp/4Q3/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FIXED, seconds_per_move=15)),
            ("rnbqkbnr/pppppppp/5Q2/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FIXED, seconds_per_move=30)),
            ("rnbqkbnr/pppppppp/6Q1/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FIXED, seconds_per_move=60)),
            ("rnbqkbnr/pppppppp/7Q/8/8/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FIXED, seconds_per_move=90))])
        self.time_control_blitz_map = OrderedDict([
            ("rnbqkbnr/pppppppp/8/8/Q7/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.BLITZ, minutes_per_game=1)),
            ("rnbqkbnr/pppppppp/8/8/1Q6/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.BLITZ, minutes_per_game=3)),
            ("rnbqkbnr/pppppppp/8/8/2Q5/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.BLITZ, minutes_per_game=5)),
            ("rnbqkbnr/pppppppp/8/8/3Q4/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.BLITZ, minutes_per_game=10)),
            ("rnbqkbnr/pppppppp/8/8/4Q3/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.BLITZ, minutes_per_game=15)),
            ("rnbqkbnr/pppppppp/8/8/5Q2/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.BLITZ, minutes_per_game=30)),
            ("rnbqkbnr/pppppppp/8/8/6Q1/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.BLITZ, minutes_per_game=60)),
            ("rnbqkbnr/pppppppp/8/8/7Q/8/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.BLITZ, minutes_per_game=90))])
        self.time_control_fisch_map = OrderedDict([
            ("rnbqkbnr/pppppppp/8/8/8/Q7/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FISCHER, minutes_per_game=1, fischer_increment=1)),
            ("rnbqkbnr/pppppppp/8/8/8/1Q6/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FISCHER, minutes_per_game=3, fischer_increment=2)),
            ("rnbqkbnr/pppppppp/8/8/8/2Q5/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FISCHER, minutes_per_game=4, fischer_increment=2)),
            ("rnbqkbnr/pppppppp/8/8/8/3Q4/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FISCHER, minutes_per_game=5, fischer_increment=3)),
            ("rnbqkbnr/pppppppp/8/8/8/4Q3/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FISCHER, minutes_per_game=10, fischer_increment=5)),
            ("rnbqkbnr/pppppppp/8/8/8/5Q2/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FISCHER, minutes_per_game=15, fischer_increment=10)),
            ("rnbqkbnr/pppppppp/8/8/8/6Q1/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FISCHER, minutes_per_game=30, fischer_increment=15)),
            ("rnbqkbnr/pppppppp/8/8/8/7Q/PPPPPPPP/RNBQKBNR", TimeControl(TimeMode.FISCHER, minutes_per_game=60, fischer_increment=30))])
        self.time_control_fixed_list = ["mov  1", "mov  3", "mov  5", "mov 10", "mov 15", "mov 30", "mov 60", "mov 90"]
        self.time_control_blitz_list = ["bl   1", "bl   3", "bl   5", "bl  10", "bl  15", "bl  30", "bl  60", "bl  90"]
        self.time_control_fisch_list = ["f 1  1", "f 3  2", "f 4  2", "f 5  3", "f10  5", "f15 10", "f30 15", "f60 30"]

    def power_off(self):
        DisplayDgt.show(text_goodbye)
        self.engine_restart = True
        self.fire(Event.SHUTDOWN())

    def reboot(self):
        DisplayDgt.show(text_pleasewait)
        self.engine_restart = True
        self.fire(Event.REBOOT())

    def reset_hint_and_score(self):
        self.hint_move = chess.Move.null()
        self.hint_fen = None
        self.score = None
        self.mate = None

    def process_button0(self):
        if self.top_result is None:
            if bool(self.hint_move):
                DisplayDgt.show(Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen, beep=BeepLevel.BUTTON, duration=1))
            else:
                DisplayDgt.show(text_nomove)

        if self.top_result == Menu.TOP_MENU:
            self.top_result = None
            self.top_index = None
            msg = 'play'
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.MODE_MENU:
            self.top_result = Menu.TOP_MENU
            msg = self.top_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.POSITION_MENU:
            if self.setup_uci960_result is None:
                if self.setup_reverse_result is None:
                    if self.setup_whitetomove_result is None:
                        self.top_result = Menu.TOP_MENU
                        msg = self.top_index.value
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))
                    else:
                        self.setup_whitetomove_result = None
                        if self.setup_whitetomove_index:
                            DisplayDgt.show(text_sidewhite)
                        else:
                            DisplayDgt.show(text_sideblack)
                else:
                    self.setup_reverse_result = None
                    if self.setup_reverse_index:
                        DisplayDgt.show(text_bw)
                    else:
                        DisplayDgt.show(text_wb)
            else:
                self.setup_uci960_result = None
                if self.setup_uci960_index:
                    DisplayDgt.show(text_960yes)
                else:
                    DisplayDgt.show(text_960no)

        elif self.top_result == Menu.LEVEL_MENU:
            self.top_result = Menu.TOP_MENU
            msg = self.top_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.SYSTEM_MENU:
            self.top_result = Menu.TOP_MENU
            msg = self.top_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.ENGINE_MENU:
            self.top_result = Menu.TOP_MENU
            msg = self.top_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.BOOK_MENU:
            self.top_result = Menu.TOP_MENU
            msg = self.top_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.TIME_MENU:
            if self.time_mode_result is None:
                self.top_result = Menu.TOP_MENU
                msg = self.top_index.value
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))
            else:
                msg = self.time_mode_result.value
                self.time_mode_result = None
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

    def process_button1(self):
        if self.top_result is None:
            if self.mate is None:
                sc_xl = 'no scr' if self.score is None else str(self.score).rjust(6)
                sc_3k = 'no score' if self.score is None else str(self.score).rjust(8)
            else:
                sc_xl = 'm ' + str(self.mate)
                sc_3k = 'mate ' + str(self.mate)
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m=sc_3k, s=sc_xl, beep=BeepLevel.BUTTON, duration=1))

        if self.top_result == Menu.TOP_MENU:
            self.top_index = MenuLoop.prev(self.top_index)
            msg = self.top_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.MODE_MENU:
            self.mode_index = ModeLoop.prev(self.mode_index)
            msg = self.mode_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.POSITION_MENU:
            if self.setup_uci960_result is None:
                if self.setup_reverse_result is None:
                    if self.setup_whitetomove_result is None:
                        self.setup_whitetomove_index = not self.setup_whitetomove_index
                        if self.setup_whitetomove_index:
                            DisplayDgt.show(text_sidewhite)
                        else:
                            DisplayDgt.show(text_sideblack)
                    else:
                        self.setup_reverse_index = not self.setup_reverse_index
                        if self.setup_reverse_index:
                            DisplayDgt.show(text_bw)
                        else:
                            DisplayDgt.show(text_wb)
                else:
                    self.setup_uci960_index = not self.setup_uci960_index
                    if self.setup_uci960_index:
                        DisplayDgt.show(text_960yes)
                    else:
                        DisplayDgt.show(text_960no)

        elif self.top_result == Menu.LEVEL_MENU:
            if self.mode_result == Mode.REMOTE:
                DisplayDgt.show(text_nofunction)
            elif self.engine_has_levels:
                self.engine_level_index = (self.engine_level_index - 1) % self.n_levels
                level = str(self.engine_level_index)
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m="level " + level, s="lvl " + level, beep=BeepLevel.BUTTON, duration=0))
            else:
                DisplayDgt.show(text_nolevel)

        elif self.top_result == Menu.SYSTEM_MENU:
            self.system_index = SettingsLoop.prev(self.system_index)
            msg = self.system_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.ENGINE_MENU:
            if self.mode_result == Mode.REMOTE:
                DisplayDgt.show(text_nofunction)
            elif self.installed_engines:
                self.engine_index = (self.engine_index - 1) % self.n_engines
                msg = (self.installed_engines[self.engine_index])[1]
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))
            else:
                DisplayDgt.show(text_erroreng)

        elif self.top_result == Menu.BOOK_MENU:
            if self.mode_result == Mode.REMOTE:
                DisplayDgt.show(text_nofunction)
            else:
                self.book_index = (self.book_index - 1) % self.n_books
                msg = (self.all_books[self.book_index])[0]
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.TIME_MENU:
            if self.time_mode_result is None:
                self.time_mode_index = TimeModeLoop.prev(self.time_mode_index)
                msg = self.time_mode_index.value
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))
            else:
                if self.time_mode_index == TimeMode.FIXED:
                    self.time_control_fixed_index = (self.time_control_fixed_index - 1) % len(self.time_control_fixed_map)
                    msg = self.time_control_fixed_list[self.time_control_fixed_index]
                elif self.time_mode_index == TimeMode.BLITZ:
                    self.time_control_blitz_index = (self.time_control_blitz_index - 1) % len(self.time_control_blitz_map)
                    msg = self.time_control_blitz_list[self.time_control_blitz_index]
                elif self.time_mode_index == TimeMode.FISCHER:
                    self.time_control_fisch_index = (self.time_control_fisch_index - 1) % len(self.time_control_fisch_map)
                    msg = self.time_control_fisch_list[self.time_control_fisch_index]
                else:
                    logging.error('Wrong value for time_mode_index: {0}'.format(self.time_mode_index))
                    msg = 'error'
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

    def process_button2(self):
        if self.top_result is None:
            if self.mode_result == Mode.NORMAL:
                if self.alternative:
                    self.fire(Event.ALTERNATIVE_MOVE())
                else:
                    self.fire(Event.STARTSTOP_THINK())
            if self.mode_result == Mode.REMOTE:
                self.fire(Event.STARTSTOP_THINK())
            if self.mode_result == Mode.OBSERVE:
                self.fire(Event.STARTSTOP_CLOCK())
            if self.mode_result == Mode.ANALYSIS or self.mode_result == Mode.KIBITZ:
                DisplayDgt.show(text_nofunction)

    def process_button3(self):
        if self.top_result is None:
            if self.last_move:
                DisplayDgt.show(Dgt.DISPLAY_MOVE(move=self.last_move, fen=self.last_fen, beep=BeepLevel.BUTTON, duration=1))
            else:
                DisplayDgt.show(text_nomove)

        if self.top_result == Menu.TOP_MENU:
            self.top_index = MenuLoop.next(self.top_index)
            msg = self.top_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.MODE_MENU:
            self.mode_index = ModeLoop.next(self.mode_index)
            msg = self.mode_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.POSITION_MENU:
            if self.setup_uci960_result is None:
                if self.setup_reverse_result is None:
                    if self.setup_whitetomove_result is None:
                        self.setup_whitetomove_index = not self.setup_whitetomove_index
                        if self.setup_whitetomove_index:
                            DisplayDgt.show(text_sidewhite)
                        else:
                            DisplayDgt.show(text_sideblack)
                    else:
                        self.setup_reverse_index = not self.setup_reverse_index
                        if self.setup_reverse_index:
                            DisplayDgt.show(text_bw)
                        else:
                            DisplayDgt.show(text_wb)
                else:
                    self.setup_uci960_index = not self.setup_uci960_index
                    if self.setup_uci960_index:
                        DisplayDgt.show(text_960yes)
                    else:
                        DisplayDgt.show(text_960no)

        elif self.top_result == Menu.LEVEL_MENU:
            if self.mode_result == Mode.REMOTE:
                DisplayDgt.show(text_nofunction)
            elif self.engine_has_levels:
                self.engine_level_index = (self.engine_level_index + 1) % self.n_levels
                level = str(self.engine_level_index)
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m="level " + level, s="lvl " + level, beep=BeepLevel.BUTTON, duration=0))
            else:
                DisplayDgt.show(text_nolevel)

        elif self.top_result == Menu.SYSTEM_MENU:
            self.system_index = SettingsLoop.next(self.system_index)
            msg = self.system_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.ENGINE_MENU:
            if self.mode_result == Mode.REMOTE:
                DisplayDgt.show(text_nofunction)
            elif self.installed_engines:
                self.engine_index = (self.engine_index + 1) % self.n_engines
                msg = (self.installed_engines[self.engine_index])[1]
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))
            else:
                DisplayDgt.show(text_erroreng)

        elif self.top_result == Menu.BOOK_MENU:
            if self.mode_result == Mode.REMOTE:
                DisplayDgt.show(text_nofunction)
            else:
                self.book_index = (self.book_index + 1) % self.n_books
                msg = (self.all_books[self.book_index])[0]
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.TIME_MENU:
            if self.time_mode_result is None:
                self.time_mode_index = TimeModeLoop.next(self.time_mode_index)
                msg = self.time_mode_index.value
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))
            else:
                if self.time_mode_index == TimeMode.FIXED:
                    self.time_control_fixed_index = (self.time_control_fixed_index + 1) % len(self.time_control_fixed_map)
                    msg = self.time_control_fixed_list[self.time_control_fixed_index]
                elif self.time_mode_index == TimeMode.BLITZ:
                    self.time_control_blitz_index = (self.time_control_blitz_index + 1) % len(self.time_control_blitz_map)
                    msg = self.time_control_blitz_list[self.time_control_blitz_index]
                elif self.time_mode_index == TimeMode.FISCHER:
                    self.time_control_fisch_index = (self.time_control_fisch_index + 1) % len(self.time_control_fisch_map)
                    msg = self.time_control_fisch_list[self.time_control_fisch_index]
                else:
                    logging.error('Wrong value for time_mode_index: {0}'.format(self.time_mode_index))
                    msg = 'error'
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

    def process_button4(self):
        if self.top_result is None:
            self.top_result = Menu.TOP_MENU
            self.top_index = Menu.MODE_MENU
            msg = self.top_index.value
            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        elif self.top_result == Menu.TOP_MENU:
            self.top_result = self.top_index
            # display first entry of the submenu "top"
            if self.top_index == Menu.MODE_MENU:
                msg = self.mode_index.value
                text = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0)
            elif self.top_index == Menu.POSITION_MENU:
                self.setup_whitetomove_index = True
                if self.setup_whitetomove_index:
                    text = text_sidewhite
                else:
                    text = text_sideblack
            elif self.top_index == Menu.TIME_MENU:
                self.time_mode_index = TimeMode.FIXED
                msg = self.time_mode_index.value
                text = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0)
            elif self.top_index == Menu.BOOK_MENU:
                msg = (self.all_books[self.book_index])[0]
                text = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0)
            elif self.top_index == Menu.LEVEL_MENU:
                if self.mode_result == Mode.REMOTE:
                    text = text_nofunction
                elif self.engine_has_levels:
                    level = str(self.engine_level_index)
                    text = Dgt.DISPLAY_TEXT(l=None, m="level " + level, s="lvl " + level, beep=BeepLevel.BUTTON, duration=0)
                else:
                    text = text_nolevel
            elif self.top_index == Menu.ENGINE_MENU:
                if self.mode_result == Mode.REMOTE:
                    text = text_nofunction
                else:
                    if self.installed_engines:
                        msg = (self.installed_engines[self.engine_index])[1]
                        text = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0)
                    else:
                        # if its a remote engine, this menu shouldnt be displayed at all
                        text = text_erroreng
            elif self.top_index == Menu.SYSTEM_MENU:
                msg = self.system_index.value
                text = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0)
            else:
                logging.error('Wrong value for topindex: {0}'.format(self.top_index))
                text = text_errortop
            DisplayDgt.show(text)

        elif self.top_result == Menu.MODE_MENU:
            self.mode_result = self.mode_index
            self.fire(Event.SET_INTERACTION_MODE(mode=self.mode_result, beep=BeepLevel.BUTTON))
            self.top_result = None
            self.top_index = None

        elif self.top_result == Menu.POSITION_MENU:
            if self.setup_whitetomove_result is None:
                self.setup_whitetomove_result = self.setup_whitetomove_index
                self.setup_reverse_index = self.flip_board
                if self.setup_reverse_index:
                    DisplayDgt.show(text_bw)
                else:
                    DisplayDgt.show(text_wb)
            else:
                if self.setup_reverse_result is None:
                    self.setup_reverse_result = self.setup_reverse_index
                    self.setup_uci960_index = False
                    if self.setup_uci960_index:
                        DisplayDgt.show(text_960yes)
                    else:
                        DisplayDgt.show(text_960no)
                else:
                    if self.setup_uci960_result is None:
                        self.setup_uci960_result = self.setup_uci960_index
                        DisplayDgt.show(text_scanboard)
                    else:
                        to_move = 'w' if self.setup_whitetomove_index else 'b'
                        fen = self.dgt_fen
                        if self.flip_board != self.setup_reverse_result:
                            logging.debug('Flipping the board')
                            fen = fen[::-1]
                        fen += " {0} KQkq - 0 1".format(to_move)
                        bit_board = chess.Board(fen, self.setup_uci960_result)
                        # ask python-chess to correct the castling string
                        bit_board.set_fen(bit_board.fen())
                        if bit_board.is_valid():
                            self.flip_board = self.setup_reverse_result
                            self.fire(Event.SETUP_POSITION(fen=bit_board.fen(), uci960=self.setup_uci960_result))
                            self.setup_whitetomove_result = None
                            self.setup_reverse_result = None
                            self.setup_uci960_result = None
                            self.top_result = None
                            self.top_index = None
                        else:
                            DisplayDgt.show(text_illegalpos)

        elif self.top_result == Menu.LEVEL_MENU:
            if self.mode_result == Mode.REMOTE:
                DisplayDgt.show(text_nofunction)
            elif self.engine_has_levels:
                if self.engine_level_result != self.engine_level_index:
                    self.engine_level_result = self.engine_level_index
                    self.fire(Event.LEVEL(level=self.engine_level_result, beep=BeepLevel.BUTTON))
                    DisplayDgt.show(Dgt.DISPLAY_TEXT(l="okay level", m="ok level", s="ok lvl", beep=BeepLevel.BUTTON, duration=0))
                    self.top_result = None
                    self.top_index = None
            else:
                DisplayDgt.show(text_nolevel)

        elif self.top_result == Menu.SYSTEM_MENU:
            if self.system_index == Settings.VERSION:
                DisplayDgt.show(text_picochess)
                self.top_result = None
                self.top_index = None
            elif self.system_index == Settings.IPADR:
                msg = self.ip
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))
                self.top_result = None
                self.top_index = None
            elif self.system_index == Settings.SHUTDOWN:
                # self.power_off()
                pass
            elif self.system_index == Settings.REBOOT:
                # self.reboot()
                pass
            else:
                logging.error('Wrong value for system_index: {0}'.format(self.system_index))
            self.top_result = None
            self.top_index = None

        elif self.top_result == Menu.ENGINE_MENU:
            if self.mode_result == Mode.REMOTE:
                DisplayDgt.show(text_nofunction)
            elif self.installed_engines:
                # Reset level selections
                self.engine_level_index = self.engine_level_result
                self.engine_has_levels = False
                # This is a handshake change so index values changed and sync'd in the response below
                self.fire(Event.NEW_ENGINE(eng=self.installed_engines[self.engine_index]))
                self.engine_restart = True
                self.top_result = None
                self.top_index = None
            else:
                DisplayDgt.show(text_erroreng)

        elif self.top_result == Menu.BOOK_MENU:
            if self.mode_result == Mode.REMOTE:
                DisplayDgt.show(text_nofunction)
            elif self.book_result != self.book_index:
                self.book_result = self.book_index
                self.fire(Event.SET_OPENING_BOOK(book=self.all_books[self.book_index], book_control_string='ok book', beep=BeepLevel.BUTTON))
                self.top_result = None
                self.top_index = None

        elif self.top_result == Menu.TIME_MENU:
            if self.time_mode_result is None:
                self.time_mode_result = self.time_mode_index
                # display first entry of the submenu "time_control"
                if self.time_mode_index == TimeMode.FIXED:
                    msg = self.time_control_fixed_list[self.time_control_fixed_index]
                elif self.time_mode_index == TimeMode.BLITZ:
                    msg = self.time_control_blitz_list[self.time_control_blitz_index]
                elif self.time_mode_index == TimeMode.FISCHER:
                    msg = self.time_control_fisch_list[self.time_control_fisch_index]
                else:
                    logging.error('Wrong value for time_mode_index: {0}'.format(self.time_mode_index))
                    msg = 'error'
                DisplayDgt.show(Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=BeepLevel.BUTTON, duration=0))
            else:
                self.time_mode_result = None
                if self.time_mode_index == TimeMode.FIXED:
                    time_control = self.time_control_fixed_map[list(self.time_control_fixed_map)[self.time_control_fixed_index]]
                elif self.time_mode_index == TimeMode.BLITZ:
                    time_control = self.time_control_blitz_map[list(self.time_control_blitz_map)[self.time_control_blitz_index]]
                elif self.time_mode_index == TimeMode.FISCHER:
                    time_control = self.time_control_fisch_map[list(self.time_control_fisch_map)[self.time_control_fisch_index]]
                else:
                    logging.error('Wrong value for time_mode_index: {0}'.format(self.time_mode_index))
                    time_control = None
                self.fire(Event.SET_TIME_CONTROL(time_control=time_control, time_control_string='ok time', beep=BeepLevel.BUTTON))
                self.top_result = None
                self.top_index = None

    def drawresign(self):
        rnk_8, rnk_7, rnk_6, rnk_5, rnk_4, rnk_3, rnk_2, rnk_1 = self.dgt_fen.split("/")
        self.drawresign_fen = "8/8/8/" + rnk_5 + "/" + rnk_4 + "/8/8/8"

    def run(self):
        while True:
            # Check if we have something to display
            try:
                message = self.msg_queue.get()
                logging.debug("Received message from msg queue: %s", message)
                for case in switch(message):
                    if case(MessageApi.ENGINE_READY):
                        self.engine_result = self.installed_engines.index(message.eng)
                        self.engine_index = self.engine_result
                        self.engine_has_levels = message.has_levels
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l='okay engine', m='ok engin', s="ok eng", beep=BeepLevel.BUTTON, duration=1))
                        self.engine_restart = False
                        break
                    if case(MessageApi.ENGINE_STARTUP):
                        if message.path:
                            self.installed_engines = get_installed_engines(message.path)
                            self.n_engines = len(self.installed_engines)
                            for index in range(0, self.n_engines):
                                full_path, short = self.installed_engines[index]
                                if full_path == message.path:
                                    self.engine_result = index
                                    self.engine_index = self.engine_result
                                    self.engine_has_levels = message.has_levels
                        break
                    if case(MessageApi.ENGINE_FAIL):
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l='error eng', m='error', s=None, beep=BeepLevel.YES, duration=1))
                        break
                    if case(MessageApi.COMPUTER_MOVE):
                        move = message.result.bestmove
                        ponder = message.result.ponder
                        self.alternative = True
                        self.last_move = move
                        self.hint_move = chess.Move.null() if ponder is None else ponder
                        self.hint_fen = message.game.fen()
                        self.last_fen = message.fen
                        # Display the move
                        uci_move = move.uci()
                        DisplayDgt.show(Dgt.DISPLAY_MOVE(move=move, fen=message.fen, beep=BeepLevel.CONFIG, duration=0))
                        DisplayDgt.show(Dgt.LIGHT_SQUARES(squares=(uci_move[0:2], uci_move[2:4])))
                        break
                    if case(MessageApi.START_NEW_GAME):
                        DisplayDgt.show(Dgt.LIGHT_CLEAR())
                        self.last_move = chess.Move.null()
                        self.reset_hint_and_score()
                        self.mode_index = Mode.NORMAL
                        self.top_result = None
                        self.alternative = False
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m="new game", s="newgam", beep=BeepLevel.CONFIG, duration=1))
                        break
                    if case(MessageApi.WAIT_STATE):
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m="you move", s="youmov", beep=BeepLevel.OKAY, duration=0))
                        break
                    if case(MessageApi.COMPUTER_MOVE_DONE_ON_BOARD):
                        DisplayDgt.show(Dgt.LIGHT_CLEAR())
                        self.alternative = False
                        if self.ok_moves_messages:
                            DisplayDgt.show(Dgt.DISPLAY_TEXT(l="okay pico", m="ok pico", s="okpico", beep=BeepLevel.OKAY, duration=0.5))
                        break
                    if case(MessageApi.USER_MOVE):
                        self.alternative = False
                        if self.ok_moves_messages:
                            DisplayDgt.show(Dgt.DISPLAY_TEXT(l="okay user", m="ok user", s="okuser", beep=BeepLevel.OKAY, duration=0.5))
                        break
                    if case(MessageApi.REVIEW_MODE_MOVE):
                        self.last_move = message.move
                        self.last_fen = message.fen
                        if self.ok_moves_messages:
                            DisplayDgt.show(Dgt.DISPLAY_TEXT(l="okay move", m="ok move", s="okmove", beep=BeepLevel.OKAY, duration=0.5))
                        break
                    if case(MessageApi.ALTERNATIVE_MOVE):
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l="altn move", m="alt move", s="altmov", beep=BeepLevel.BUTTON, duration=0.5))
                        break
                    if case(MessageApi.LEVEL):
                        level = str(message.level)
                        if self.engine_restart:
                            pass
                        elif self.engine_level_result != self.engine_level_index:
                            self.engine_level_result = self.engine_level_index
                        else:
                            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m="level " + level, s="lvl " + level, beep=message.beep, duration=1))
                        break
                    if case(MessageApi.TIME_CONTROL):
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m=message.time_control_string, s=None, beep=message.beep, duration=1))
                        break
                    if case(MessageApi.OPENING_BOOK):
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m=message.book_control_string, s=None, beep=message.beep, duration=1))
                        break
                    if case(MessageApi.USER_TAKE_BACK):
                        self.reset_hint_and_score()
                        self.alternative = False
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m="takeback", s="takbak", beep=BeepLevel.CONFIG, duration=0))
                        break
                    if case(MessageApi.GAME_ENDS):
                        ge = message.result.value
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m=ge, s=None, beep=BeepLevel.CONFIG, duration=1))
                        break
                    if case(MessageApi.INTERACTION_MODE):
                        self.mode_result = message.mode
                        self.alternative = False
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m=message.mode.value, s=None, beep=message.beep, duration=1))
                        break
                    if case(MessageApi.PLAY_MODE):
                        pm = message.play_mode.value
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=pm, m=pm[:8], s=pm[:6], beep=BeepLevel.BUTTON, duration=1))
                        break
                    if case(MessageApi.NEW_SCORE):
                        self.score = message.score
                        self.mate = message.mate
                        if message.mode == Mode.KIBITZ:
                            DisplayDgt.show(Dgt.DISPLAY_TEXT(l=None, m=str(self.score).rjust(6), s=None, beep=BeepLevel.NO, duration=1))
                        break
                    if case(MessageApi.BOOK_MOVE):
                        self.score = None
                        self.mate = None
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l="book move", m="book mov", s="book", beep=BeepLevel.NO, duration=1))
                        break
                    if case(MessageApi.NEW_PV):
                        self.hint_move = message.pv[0]
                        self.hint_fen = message.fen
                        if message.mode == Mode.ANALYSIS:
                            DisplayDgt.show(Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen, beep=BeepLevel.NO, duration=0))
                        break
                    if case(MessageApi.SYSTEM_INFO):
                        self.ip = ' '.join(message.info["ip"].split('.')[2:])
                        break
                    if case(MessageApi.STARTUP_INFO):
                        self.book_result = message.info["book_index"]
                        self.book_index = self.book_result
                        break
                    if case(MessageApi.SEARCH_STARTED):
                        logging.debug('Search started')
                        break
                    if case(MessageApi.SEARCH_STOPPED):
                        logging.debug('Search stopped')
                        break
                    if case(MessageApi.RUN_CLOCK):
                        # @todo Make this code independent from DGT Hex codes => more abstract
                        tc = message.time_control
                        time_left = int(tc.clock_time[chess.WHITE])
                        if time_left < 0:
                            time_left = 0
                        time_right = int(tc.clock_time[chess.BLACK])
                        if time_right < 0:
                            time_right = 0
                        side = 0x01 if (message.turn == chess.WHITE) != self.flip_board else 0x02
                        if tc.mode == TimeMode.FIXED:
                            time_left = time_right = tc.seconds_per_move
                        if self.flip_board:
                            time_left, time_right = time_right, time_left
                        DisplayDgt.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=side))
                        break
                    if case(MessageApi.STOP_CLOCK):
                        DisplayDgt.show(Dgt.CLOCK_STOP())
                        break
                    if case(MessageApi.DGT_BUTTON):
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
                    if case(MessageApi.DGT_FEN):
                        fen = message.fen
                        if self.flip_board:  # Flip the board if needed
                            fen = fen[::-1]
                        if fen == "RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr":  # Check if we have to flip the board
                            logging.debug('Flipping the board')
                            # Flip the board
                            self.flip_board = not self.flip_board
                            # set standard for setup orientation too
                            # self.setup_reverse_orientation = self.flip_board
                            self.setup_reverse_index = self.flip_board
                            fen = fen[::-1]
                        logging.debug("DGT-Fen: " + fen)
                        if fen == self.dgt_fen:
                            logging.debug('Ignore same fen')
                            break
                        self.dgt_fen = fen
                        self.drawresign()
                        # Fire the appropriate event
                        if fen in level_map:  # User sets level
                            level = 3 * level_map.index(fen)
                            if level > 20:
                                level = 20
                            self.engine_level_result = level
                            self.engine_level_index = level
                            logging.debug("Map-Fen: New level")
                            self.fire(Event.LEVEL(level=level, beep=BeepLevel.MAP))
                        elif fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR":  # New game
                            logging.debug("Map-Fen: New game")
                            self.draw_setup_pieces = False
                            self.fire(Event.NEW_GAME())
                        elif fen in book_map:  # Choose opening book
                            book_index = book_map.index(fen)
                            try:
                                b = self.all_books[book_index]
                                self.book_result = book_index
                                logging.debug("Map-Fen: Opening book [%s]", b[1])
                                self.fire(Event.SET_OPENING_BOOK(book=b, book_control_string=b[0], beep=BeepLevel.MAP))
                            except IndexError:
                                pass
                        elif fen in mode_map:  # Set interaction mode
                            logging.debug("Map-Fen: Interaction mode [%s]", mode_map[fen])
                            self.fire(Event.SET_INTERACTION_MODE(mode=mode_map[fen], beep=BeepLevel.MAP))
                        elif fen in self.time_control_fixed_map:
                            logging.debug("Map-Fen: Time control fixed")
                            self.time_mode_result = TimeMode.FIXED
                            self.time_control_fixed_index = list(self.time_control_fixed_map.keys()).index(fen)
                            self.fire(Event.SET_TIME_CONTROL(time_control=self.time_control_fixed_map[fen],
                                                             time_control_string=self.time_control_fixed_list[self.time_control_fixed_index],
                                                             beep=BeepLevel.MAP))
                        elif fen in self.time_control_blitz_map:
                            logging.debug("Map-Fen: Time control blitz")
                            self.time_mode_result = TimeMode.BLITZ
                            self.time_control_blitz_index = list(self.time_control_blitz_map.keys()).index(fen)
                            self.fire(Event.SET_TIME_CONTROL(time_control=self.time_control_blitz_map[fen],
                                                             time_control_string=self.time_control_blitz_list[self.time_control_blitz_index],
                                                             beep=BeepLevel.MAP))
                        elif fen in self.time_control_fisch_map:
                            logging.debug("Map-Fen: Time control fischer")
                            self.time_mode_result = TimeMode.FISCHER
                            self.time_control_fisch_index = list(self.time_control_fisch_map.keys()).index(fen)
                            self.fire(Event.SET_TIME_CONTROL(time_control=self.time_control_fisch_map[fen],
                                                             time_control_string=self.time_control_fisch_list[self.time_control_fisch_index],
                                                             beep=BeepLevel.MAP))
                        elif fen in shutdown_map:
                            logging.debug("Map-Fen: shutdown")
                            self.power_off()
                        elif self.drawresign_fen in drawresign_map:
                            logging.debug("Map-Fen: drawresign")
                            self.fire(Event.DRAWRESIGN(result=drawresign_map[self.drawresign_fen]))
                        else:
                            if self.draw_setup_pieces:
                                DisplayDgt.show(Dgt.DISPLAY_TEXT(l="set pieces", m="set pcs", s="setup", beep=BeepLevel.NO, duration=0))
                                self.draw_setup_pieces = False
                            self.fire(Event.FEN(fen=fen))
                        break
                    if case(MessageApi.DGT_CLOCK_VERSION):
                        DisplayDgt.show(Dgt.CLOCK_VERSION(main_version=message.main_version,
                                                          sub_version=message.sub_version, attached=message.attached))
                        break
                    if case(MessageApi.DGT_CLOCK_TIME):
                        DisplayDgt.show(Dgt.CLOCK_TIME(time_left=message.time_left, time_right=message.time_right))
                        break
                    if case(MessageApi.JACK_CONNECTED_ERROR):  # this will only work in case of 2 clocks connected!
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l="error jack", m="err jack", s="jack", beep=BeepLevel.YES, duration=0))
                        break
                    if case(MessageApi.NO_EBOARD_ERROR):
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=message.l, m=message.m, s=message.s, beep=BeepLevel.NO, duration=0))
                        break
                    if case(MessageApi.EBOARD_VERSION):
                        DisplayDgt.show(Dgt.DISPLAY_TEXT(l=message.l, m=message.m, s=message.s, beep=BeepLevel.NO, duration=0.5))
                        break
                    if case():  # Default
                        # print(message)
                        pass
            except queue.Empty:
                pass
