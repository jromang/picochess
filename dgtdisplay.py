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

from timecontrol import *
from collections import OrderedDict

from dgtiface import *
from engine import get_installed_engines
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

engine_map = ("rnbqkbnr/pppppppp/q7/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/1q6/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/2q5/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/3q4/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/4q3/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/5q2/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/6q1/8/8/8/PPPPPPPP/RNBQKBNR",
             "rnbqkbnr/pppppppp/7q/8/8/8/PPPPPPPP/RNBQKBNR")

shutdown_map = ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQQBNR",
                "RNBQQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr",
                "8/8/8/8/8/8/8/3QQ3",
                "3QQ3/8/8/8/8/8/8/8")

reboot_map = ("rnbqqbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
              "RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqqbnr",
              "8/8/8/8/8/8/8/3qq3",
              "3qq3/8/8/8/8/8/8/8")

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


class DgtDisplay(Observable, DisplayMsg, threading.Thread):
    def __init__(self, disable_ok_message, dgttranslate):
        super(DgtDisplay, self).__init__()
        self.show_ok_message = not disable_ok_message
        self.dgttranslate = dgttranslate

        self.flip_board = False
        self.dgt_fen = None
        self.engine_finished = False
        self.ip = '?'  # the last two parts of the IP
        self.drawresign_fen = None
        self.show_setup_pieces_msg = True

        self.reset_moves_and_score()

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

        self.engine_level_result = None
        self.engine_level_index = 20
        self.n_levels = 21  # Default engine (Stockfish) has 21 playing levels
        self.engine_has_levels = False  # Not all engines support levels - assume not
        self.engine_has_960 = False  # Not all engines support 960 mode - assume not
        self.engine_restart = False
        self.engine_result = None
        self.engine_index = 0
        self.installed_engines = None
        self.n_engines = 0

        self.book_index = 7  # Default book is 7 - book 'h'
        self.all_books = get_opening_books()
        self.n_books = len(self.all_books)

        self.system_index = Settings.VERSION
        self.system_sound_result = None
        self.system_sound_index = self.dgttranslate.beep_level
        self.system_language_result = None
        langs = {'en': Language.EN, 'de': Language.DE, 'nl': Language.NL, 'fr': Language.FR, 'es': Language.ES}
        self.system_language_index = langs[self.dgttranslate.language]

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
        self.time_control_fixed_list = ["  1", "  3", "  5", " 10", " 15", " 30", " 60", " 90"]
        self.time_control_blitz_list = ["   1", "   3", "   5", "  10", "  15", "  30", "  60", "  90"]
        self.time_control_fisch_list = [" 1  1", " 3  2", " 4  2", " 5  3", "10  5", "15 10", "30 15", "60 30"]

    def reset_menu_results(self):
        # dont override "mode_result", otherwise wQ a5-e5 wont work anymore (=> if's)
        self.time_mode_result = None
        self.setup_whitetomove_result = None
        self.setup_reverse_result = None
        self.setup_uci960_result = None
        self.top_result = None
        self.engine_result = None
        self.engine_level_result = None
        self.system_sound_result = None
        self.system_language_result = None

    def power_off(self):
        DisplayDgt.show(self.dgttranslate.text('Y10_goodbye'))
        self.engine_restart = True
        self.fire(Event.SHUTDOWN())

    def reboot(self):
        DisplayDgt.show(self.dgttranslate.text('Y10_pleasewait'))
        self.engine_restart = True
        self.fire(Event.REBOOT())

    def reset_moves_and_score(self):
        self.play_move = chess.Move.null()
        self.play_fen = None
        self.play_turn = None
        self.hint_move = chess.Move.null()
        self.hint_fen = None
        self.hint_turn = None
        self.last_move = chess.Move.null()
        self.last_fen = None
        self.last_turn = None
        self.score = None
        self.mate = None

    def process_button0(self):
        if self.top_result is None:
            if self.last_move:
                side = ClockSide.LEFT if (self.last_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                text = Dgt.DISPLAY_MOVE(move=self.last_move, fen=self.last_fen, side=side, wait=False,
                                        beep=self.dgttranslate.bl(BeepLevel.BUTTON), maxtime=1)
            else:
                text = self.dgttranslate.text('B10_nomove')
            DisplayDgt.show(text)
            self.exit_display(wait=True)

        if self.top_result == Menu.TOP_MENU:
            self.reset_menu_results()
            self.exit_display()

        elif self.top_result == Menu.MODE_MENU:
            self.top_result = Menu.TOP_MENU
            text = self.dgttranslate.text(self.top_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.POSITION_MENU:
            if self.setup_uci960_result is None:
                if self.setup_reverse_result is None:
                    if self.setup_whitetomove_result is None:
                        self.top_result = Menu.TOP_MENU
                        text = self.dgttranslate.text(self.top_index.value)
                    else:
                        self.setup_whitetomove_result = None
                        text = self.dgttranslate.text('B00_sidewhite' if self.setup_whitetomove_index else 'B00_sideblack')
                else:
                    self.setup_reverse_result = None
                    text = self.dgttranslate.text('B00_bw' if self.setup_reverse_index else 'B00_wb')
            else:
                self.setup_uci960_result = None
                text = self.dgttranslate.text('B00_960yes' if self.setup_uci960_index else 'B00_960no')
            DisplayDgt.show(text)

        elif self.top_result == Menu.SYSTEM_MENU:
            if self.system_sound_result is None and self.system_language_result is None:
                self.top_result = Menu.TOP_MENU
                text = self.dgttranslate.text(self.top_index.value)
            else:
                if self.system_language_result is None:
                    self.system_sound_result = None
                else:
                    self.system_language_result = None
                text = self.dgttranslate.text(self.system_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.ENGINE_MENU:
            if self.engine_result is None:
                self.top_result = Menu.TOP_MENU
                text = self.dgttranslate.text(self.top_index.value)
            else:
                msg = (self.installed_engines[self.engine_result])[1]
                text = self.dgttranslate.text('B00_default', msg)
                self.engine_result = None
            DisplayDgt.show(text)

        elif self.top_result == Menu.BOOK_MENU:
            self.top_result = Menu.TOP_MENU
            text = self.dgttranslate.text(self.top_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.TIME_MENU:
            if self.time_mode_result is None:
                self.top_result = Menu.TOP_MENU
                text = self.dgttranslate.text(self.top_index.value)
            else:
                text = self.dgttranslate.text(self.time_mode_result.value)
                self.time_mode_result = None
            DisplayDgt.show(text)

    def process_button1(self):
        if self.top_result is None:
            if self.mate is None:
                text = self.dgttranslate.text('B10_score', self.score)
            else:
                text = self.dgttranslate.text('B10_mate', str(self.mate))
            DisplayDgt.show(text)
            self.exit_display(wait=True)

        if self.top_result == Menu.TOP_MENU:
            self.top_index = MenuLoop.prev(self.top_index)
            text = self.dgttranslate.text(self.top_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.MODE_MENU:
            self.mode_index = ModeLoop.prev(self.mode_index)
            text = self.dgttranslate.text(self.mode_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.POSITION_MENU:
            if self.setup_uci960_result is None:
                if self.setup_reverse_result is None:
                    if self.setup_whitetomove_result is None:
                        self.setup_whitetomove_index = not self.setup_whitetomove_index
                        text = self.dgttranslate.text('B00_sidewhite' if self.setup_whitetomove_index else 'B00_sideblack')
                    else:
                        self.setup_reverse_index = not self.setup_reverse_index
                        text = self.dgttranslate.text('B00_bw' if self.setup_reverse_index else 'B00_wb')
                else:
                    if self.engine_has_960:
                        self.setup_uci960_index = not self.setup_uci960_index
                        text = self.dgttranslate.text('B00_960yes' if self.setup_uci960_index else 'B00_960no')
                    else:
                        text = self.dgttranslate.text('Y00_error960')
                DisplayDgt.show(text)

        elif self.top_result == Menu.SYSTEM_MENU:
            if self.system_sound_result is None and self.system_language_result is None:
                self.system_index = SettingsLoop.prev(self.system_index)
                text = self.dgttranslate.text(self.system_index.value)
            else:
                if self.system_language_result is None:
                    self.system_sound_index = (self.system_sound_index-1) & 0x0f
                    msg = str(self.system_sound_index).rjust(2)
                    text = self.dgttranslate.text('B00_beep', msg)
                else:
                    self.system_language_index = LanguageLoop.prev(self.system_language_index)
                    text = self.dgttranslate.text(self.system_language_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.ENGINE_MENU:
            if self.mode_result == Mode.REMOTE:
                text = self.dgttranslate.text('B00_nofunction')
            else:
                if self.engine_result is None:
                    self.engine_index = (self.engine_index-1) % self.n_engines
                    msg = (self.installed_engines[self.engine_index])[1]
                    text = self.dgttranslate.text('B00_default', msg)
                else:
                    self.engine_level_index = (self.engine_level_index-1) % self.n_levels
                    msg = str(self.engine_level_index).rjust(2)
                    text = self.dgttranslate.text('B00_level', msg)
            DisplayDgt.show(text)

        elif self.top_result == Menu.BOOK_MENU:
            if self.mode_result == Mode.REMOTE:
                text = self.dgttranslate.text('B00_nofunction')
            else:
                self.book_index = (self.book_index-1) % self.n_books
                msg = (self.all_books[self.book_index])[0]
                text = self.dgttranslate.text('B00_default', msg)
            DisplayDgt.show(text)

        elif self.top_result == Menu.TIME_MENU:
            if self.time_mode_result is None:
                self.time_mode_index = TimeModeLoop.prev(self.time_mode_index)
                text = self.dgttranslate.text(self.time_mode_index.value)
            else:
                if self.time_mode_index == TimeMode.FIXED:
                    self.time_control_fixed_index = (self.time_control_fixed_index-1) % len(self.time_control_fixed_map)
                    text = self.dgttranslate.text('B00_tc_fixed', self.time_control_fixed_list[self.time_control_fixed_index])
                elif self.time_mode_index == TimeMode.BLITZ:
                    self.time_control_blitz_index = (self.time_control_blitz_index-1) % len(self.time_control_blitz_map)
                    text = self.dgttranslate.text('B00_tc_blitz', self.time_control_blitz_list[self.time_control_blitz_index])
                elif self.time_mode_index == TimeMode.FISCHER:
                    self.time_control_fisch_index = (self.time_control_fisch_index-1) % len(self.time_control_fisch_map)
                    text = self.dgttranslate.text('B00_tc_fisch', self.time_control_fisch_list[self.time_control_fisch_index])
                else:
                    logging.warning('wrong value for time_mode_index: {0}'.format(self.time_mode_index))
                    text = self.dgttranslate.text('B00_default', 'error')
            DisplayDgt.show(text)

    def process_button2(self):
        if self.top_result is None:
            if self.engine_finished:
                # @todo Protect against multi entrance of Alt-move
                self.engine_finished = False  # This is not 100% ok, but for the moment better as nothing
                self.fire(Event.ALTERNATIVE_MOVE())
            else:
                if self.mode_result in (Mode.ANALYSIS, Mode.KIBITZ):
                    text = self.dgttranslate.text('B00_nofunction')
                    DisplayDgt.show(text)
                else:
                    self.fire(Event.PAUSE_RESUME())

    def process_button3(self):
        if self.top_result is None:
            if self.hint_move:
                side = ClockSide.LEFT if (self.hint_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                text = Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen, side=side, wait=False,
                                        beep=self.dgttranslate.bl(BeepLevel.BUTTON), maxtime=1)
            else:
                text = self.dgttranslate.text('B10_nomove')
            DisplayDgt.show(text)
            self.exit_display(wait=True)

        if self.top_result == Menu.TOP_MENU:
            self.top_index = MenuLoop.next(self.top_index)
            text = self.dgttranslate.text(self.top_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.MODE_MENU:
            self.mode_index = ModeLoop.next(self.mode_index)
            text = self.dgttranslate.text(self.mode_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.POSITION_MENU:
            if self.setup_uci960_result is None:
                if self.setup_reverse_result is None:
                    if self.setup_whitetomove_result is None:
                        self.setup_whitetomove_index = not self.setup_whitetomove_index
                        text = self.dgttranslate.text('B00_sidewhite' if self.setup_whitetomove_index else 'B00_sideblack')
                    else:
                        self.setup_reverse_index = not self.setup_reverse_index
                        text = self.dgttranslate.text('B00_bw' if self.setup_reverse_index else 'B00_wb')
                else:
                    if self.engine_has_960:
                        self.setup_uci960_index = not self.setup_uci960_index
                        text = self.dgttranslate.text('B00_960yes' if self.setup_uci960_index else 'B00_960no')
                    else:
                        text = self.dgttranslate.text('Y00_error960')
                DisplayDgt.show(text)

        elif self.top_result == Menu.SYSTEM_MENU:
            if self.system_sound_result is None and self.system_language_result is None:
                self.system_index = SettingsLoop.next(self.system_index)
                text = self.dgttranslate.text(self.system_index.value)
            else:
                if self.system_language_result is None:
                    self.system_sound_index = (self.system_sound_index+1) & 0x0f
                    msg = str(self.system_sound_index).rjust(2)
                    text = self.dgttranslate.text('B00_beep', msg)
                else:
                    self.system_language_index = LanguageLoop.next(self.system_language_index)
                    text = self.dgttranslate.text(self.system_language_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.ENGINE_MENU:
            if self.mode_result == Mode.REMOTE:
                text = self.dgttranslate.text('B00_nofunction')
            else:
                if self.engine_result is None:
                    self.engine_index = (self.engine_index+1) % self.n_engines
                    msg = (self.installed_engines[self.engine_index])[1]
                    text = self.dgttranslate.text('B00_default', msg)
                else:
                    self.engine_level_index = (self.engine_level_index+1) % self.n_levels
                    msg = str(self.engine_level_index).rjust(2)
                    text = self.dgttranslate.text('B00_level', msg)
            DisplayDgt.show(text)

        elif self.top_result == Menu.BOOK_MENU:
            if self.mode_result == Mode.REMOTE:
                text = self.dgttranslate.text('B00_nofunction')
            else:
                self.book_index = (self.book_index+1) % self.n_books
                msg = (self.all_books[self.book_index])[0]
                text = self.dgttranslate.text('B00_default', msg)
            DisplayDgt.show(text)

        elif self.top_result == Menu.TIME_MENU:
            if self.time_mode_result is None:
                self.time_mode_index = TimeModeLoop.next(self.time_mode_index)
                text = self.dgttranslate.text(self.time_mode_index.value)
            else:
                if self.time_mode_index == TimeMode.FIXED:
                    self.time_control_fixed_index = (self.time_control_fixed_index+1) % len(self.time_control_fixed_map)
                    text = self.dgttranslate.text('B00_tc_fixed', self.time_control_fixed_list[self.time_control_fixed_index])
                elif self.time_mode_index == TimeMode.BLITZ:
                    self.time_control_blitz_index = (self.time_control_blitz_index+1) % len(self.time_control_blitz_map)
                    text = self.dgttranslate.text('B00_tc_blitz', self.time_control_blitz_list[self.time_control_blitz_index])
                elif self.time_mode_index == TimeMode.FISCHER:
                    self.time_control_fisch_index = (self.time_control_fisch_index+1) % len(self.time_control_fisch_map)
                    text = self.dgttranslate.text('B00_tc_fisch', self.time_control_fisch_list[self.time_control_fisch_index])
                else:
                    logging.warning('wrong value for time_mode_index: {0}'.format(self.time_mode_index))
                    text = self.dgttranslate.text('B00_default', 'error')
            DisplayDgt.show(text)

    def process_button4(self):
        if self.top_result is None:
            self.top_result = Menu.TOP_MENU
            self.top_index = Menu.MODE_MENU
            text = self.dgttranslate.text(self.top_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.TOP_MENU:
            self.top_result = self.top_index
            # display first entry of the submenu "top"
            if self.top_index == Menu.MODE_MENU:
                text = self.dgttranslate.text(self.mode_index.value)
            elif self.top_index == Menu.POSITION_MENU:
                self.setup_whitetomove_index = True
                text = self.dgttranslate.text('B00_sidewhite' if self.setup_whitetomove_index else 'B00_sideblack')
            elif self.top_index == Menu.TIME_MENU:
                text = self.dgttranslate.text(self.time_mode_index.value)
            elif self.top_index == Menu.BOOK_MENU:
                msg = (self.all_books[self.book_index])[0]
                text = self.dgttranslate.text('B00_default', msg)
            elif self.top_index == Menu.ENGINE_MENU:
                if self.mode_result == Mode.REMOTE:
                    text = self.dgttranslate.text('B00_nofunction')
                else:
                    msg = (self.installed_engines[self.engine_index])[1]
                    text = self.dgttranslate.text('B00_default', msg)
            elif self.top_index == Menu.SYSTEM_MENU:
                text = self.dgttranslate.text(self.system_index.value)
            else:
                logging.warning('wrong value for topindex: {0}'.format(self.top_index))
                text = self.dgttranslate.text('Y00_errormenu')
            DisplayDgt.show(text)

        elif self.top_result == Menu.MODE_MENU:
            self.mode_result = self.mode_index
            text = self.dgttranslate.text('B10_okmode')
            self.fire(Event.SET_INTERACTION_MODE(mode=self.mode_result, mode_text=text, ok_text=True))
            self.reset_menu_results()

        elif self.top_result == Menu.POSITION_MENU:
            if self.setup_whitetomove_result is None:
                self.setup_whitetomove_result = self.setup_whitetomove_index
                self.setup_reverse_index = self.flip_board
                text = self.dgttranslate.text('B00_bw' if self.setup_reverse_index else 'B00_wb')
            else:
                if self.setup_reverse_result is None:
                    self.setup_reverse_result = self.setup_reverse_index
                    self.setup_uci960_index = False
                    text = self.dgttranslate.text('B00_960yes' if self.setup_uci960_index else 'B00_960no')
                else:
                    if self.setup_uci960_result is None:
                        self.setup_uci960_result = self.setup_uci960_index
                        text = self.dgttranslate.text('B00_scanboard')
                    else:
                        to_move = 'w' if self.setup_whitetomove_index else 'b'
                        fen = self.dgt_fen
                        if self.flip_board != self.setup_reverse_result:
                            logging.debug('flipping the board')
                            fen = fen[::-1]
                        fen += " {0} KQkq - 0 1".format(to_move)
                        bit_board = chess.Board(fen, self.setup_uci960_result)
                        # ask python-chess to correct the castling string
                        bit_board.set_fen(bit_board.fen())
                        if bit_board.is_valid():
                            self.flip_board = self.setup_reverse_result
                            self.fire(Event.SETUP_POSITION(fen=bit_board.fen(), uci960=self.setup_uci960_result))
                            self.reset_moves_and_score()
                            self.reset_menu_results()
                            return
                        else:
                            DisplayDgt.show(self.dgttranslate.text('Y05_illegalpos'))
                            text = self.dgttranslate.text('B00_scanboard')
            DisplayDgt.show(text)

        elif self.top_result == Menu.SYSTEM_MENU:
            exit_menu = True
            if self.system_index == Settings.VERSION:
                text = self.dgttranslate.text('B10_picochess')
                DisplayDgt.show(text)
            elif self.system_index == Settings.IPADR:
                if len(self.ip):
                    msg = self.ip
                    text = self.dgttranslate.text('B10_default', msg)
                else:
                    text = self.dgttranslate.text('B10_noipadr')
                DisplayDgt.show(text)
            elif self.system_index == Settings.SOUND:
                if self.system_sound_result is None:
                    self.system_sound_result = self.system_sound_index
                    msg = str(self.system_sound_index).rjust(2)
                    text = self.dgttranslate.text('B00_beep', msg)
                    exit_menu = False
                else:
                    self.dgttranslate.set_beep_level(self.system_sound_index)
                    text = self.dgttranslate.text('B10_okbeep')
                DisplayDgt.show(text)
            elif self.system_index == Settings.LANGUAGE:
                if self.system_language_result is None:
                    self.system_language_result = self.system_language_index
                    text = self.dgttranslate.text(self.system_language_result.value)
                    exit_menu = False
                else:
                    langs = {Language.EN: 'en', Language.DE: 'de', Language.NL: 'nl', Language.FR: 'fr', Language.ES: 'es'}
                    language = langs[self.system_language_index]
                    self.dgttranslate.set_language(language)
                    text = self.dgttranslate.text('B10_oklang')
                DisplayDgt.show(text)
            else:
                logging.warning('wrong value for system_index: {0}'.format(self.system_index))
            if exit_menu:
                self.reset_menu_results()
                self.exit_display()

        elif self.top_result == Menu.ENGINE_MENU:
            if self.mode_result == Mode.REMOTE:
                text = self.dgttranslate.text('B00_nofunction')
                DisplayDgt.show(text)
            else:
                if self.engine_result is None:
                    eng = self.installed_engines[self.engine_index]
                    if eng[2]:  # 2=has_levels
                        self.engine_result = self.engine_index
                        msg = str(self.engine_level_index).rjust(2)
                        text = self.dgttranslate.text('B00_level', msg)
                        DisplayDgt.show(text)
                    else:
                        text = self.dgttranslate.text('B10_okengine')
                        self.fire(Event.NEW_ENGINE(eng=eng, eng_text=text, ok_text=True))
                        self.engine_restart = True
                        self.reset_menu_results()
                else:
                    level = self.engine_level_index
                    lvl_text = self.dgttranslate.text('B10_level', str(level).rjust(2))
                    eng = self.installed_engines[self.engine_result]
                    eng_text = self.dgttranslate.text('B10_okengine')
                    self.fire(Event.LEVEL(level=level, level_text=lvl_text, ok_text=False))
                    self.fire(Event.NEW_ENGINE(eng=eng, eng_text=eng_text, ok_text=True))
                    self.engine_restart = True
                    self.reset_menu_results()

        elif self.top_result == Menu.BOOK_MENU:
            if self.mode_result == Mode.REMOTE:
                text = self.dgttranslate.text('B00_nofunction')
                DisplayDgt.show(text)
            else:
                text = self.dgttranslate.text('B10_okbook')
                self.fire(Event.SET_OPENING_BOOK(book=self.all_books[self.book_index], book_text=text, ok_text=True))
                self.reset_menu_results()

        elif self.top_result == Menu.TIME_MENU:
            if self.time_mode_result is None:
                self.time_mode_result = self.time_mode_index
                # display first entry of the submenu "time_control"
                if self.time_mode_index == TimeMode.FIXED:
                    text = self.dgttranslate.text('B00_tc_fixed', self.time_control_fixed_list[self.time_control_fixed_index])
                elif self.time_mode_index == TimeMode.BLITZ:
                    text = self.dgttranslate.text('B00_tc_blitz', self.time_control_blitz_list[self.time_control_blitz_index])
                elif self.time_mode_index == TimeMode.FISCHER:
                    text = self.dgttranslate.text('B00_tc_fisch', self.time_control_fisch_list[self.time_control_fisch_index])
                else:
                    logging.warning('wrong value for time_mode_index: {0}'.format(self.time_mode_index))
                    text = self.dgttranslate.text('B00_default', 'error')
                DisplayDgt.show(text)
            else:
                if self.time_mode_index == TimeMode.FIXED:
                    time_control = self.time_control_fixed_map[list(self.time_control_fixed_map)[self.time_control_fixed_index]]
                elif self.time_mode_index == TimeMode.BLITZ:
                    time_control = self.time_control_blitz_map[list(self.time_control_blitz_map)[self.time_control_blitz_index]]
                elif self.time_mode_index == TimeMode.FISCHER:
                    time_control = self.time_control_fisch_map[list(self.time_control_fisch_map)[self.time_control_fisch_index]]
                else:
                    logging.warning('wrong value for time_mode_index: {0}'.format(self.time_mode_index))
                    time_control = None
                time_left, time_right = time_control.current_clock_time(self.flip_board)
                text = self.dgttranslate.text('B10_oktime')
                self.fire(Event.SET_TIME_CONTROL(time_control=time_control, time_text=text, ok_text=True))
                DisplayDgt.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=ClockSide.NONE))
                self.reset_menu_results()

    def process_lever(self, right_side_down):
        logging.debug('lever position right_side_down: {}'.format(right_side_down))
        if self.top_result is None:
            self.play_move = chess.Move.null()
            self.play_fen = None
            self.play_turn = None
            self.fire(Event.SWITCH_SIDES(engine_finished=self.engine_finished))

    def drawresign(self):
        _, _, _, rnk_5, rnk_4, _, _, _ = self.dgt_fen.split("/")
        return "8/8/8/" + rnk_5 + "/" + rnk_4 + "/8/8/8"

    def exit_display(self, wait=False, force=True):
        if self.play_move and self.mode_result in (Mode.NORMAL, Mode.REMOTE):
            side = ClockSide.LEFT if (self.play_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
            text = Dgt.DISPLAY_MOVE(move=self.play_move, fen=self.play_fen, side=side, wait=wait,
                                    beep=self.dgttranslate.bl(BeepLevel.BUTTON), maxtime=1)
        else:
            text = Dgt.DISPLAY_TIME(force=force, wait=True)
        DisplayDgt.show(text)

    def run(self):
        logging.info('msg_queue ready')
        while True:
            # Check if we have something to display
            try:
                message = self.msg_queue.get()
                logging.debug("received message from msg_queue: %s", message)
                for case in switch(message):
                    if case(MessageApi.ENGINE_READY):
                        self.engine_index = self.installed_engines.index(message.eng)
                        self.engine_has_levels = message.has_levels
                        self.engine_has_960 = message.has_960
                        if self.show_ok_message or not message.ok_text:
                            DisplayDgt.show(message.eng_text)
                        self.engine_restart = False
                        self.exit_display(force=message.ok_text)
                        break
                    if case(MessageApi.ENGINE_STARTUP):
                        self.installed_engines = get_installed_engines(message.shell, message.path)
                        self.n_engines = len(self.installed_engines)
                        for index in range(0, self.n_engines):
                            full_path, short, haslevels = self.installed_engines[index]
                            if full_path == message.path:
                                self.engine_index = index
                                self.engine_has_levels = message.has_levels
                                self.engine_has_960 = message.has_960
                        break
                    if case(MessageApi.ENGINE_FAIL):
                        DisplayDgt.show(self.dgttranslate.text('Y00_erroreng'))
                        break
                    if case(MessageApi.COMPUTER_MOVE):
                        move = message.result.bestmove
                        ponder = message.result.ponder
                        fen = message.fen
                        turn = message.turn
                        self.engine_finished = True
                        self.play_move = move
                        self.play_fen = fen
                        self.play_turn = turn
                        self.hint_move = chess.Move.null() if ponder is None else ponder
                        self.hint_fen = None if ponder is None else message.game.fen()
                        self.hint_turn = None if ponder is None else message.game.turn
                        # Display the move
                        uci_move = move.uci()
                        side = ClockSide.LEFT if (turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                        DisplayDgt.show(Dgt.DISPLAY_MOVE(move=move, fen=message.fen, side=side, wait=message.wait,
                                                         beep=self.dgttranslate.bl(BeepLevel.CONFIG), maxtime=0))
                        DisplayDgt.show(Dgt.LIGHT_SQUARES(squares=(uci_move[0:2], uci_move[2:4])))
                        break
                    if case(MessageApi.START_NEW_GAME):
                        DisplayDgt.show(Dgt.LIGHT_CLEAR())
                        self.reset_moves_and_score()
                        # self.mode_index = Mode.NORMAL  # @todo
                        self.reset_menu_results()
                        self.engine_finished = False
                        text = self.dgttranslate.text('C10_newgame')
                        text.wait = True  # in case of GAME_ENDS before, wait for "abort"
                        DisplayDgt.show(text)
                        if self.mode_result in (Mode.NORMAL, Mode.OBSERVE, Mode.REMOTE):
                            time_left, time_right = message.time_control.current_clock_time(flip_board=self.flip_board)
                            DisplayDgt.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=ClockSide.NONE))
                        break
                    if case(MessageApi.COMPUTER_MOVE_DONE_ON_BOARD):
                        DisplayDgt.show(Dgt.LIGHT_CLEAR())
                        self.last_move = self.play_move
                        self.last_fen = self.play_fen
                        self.last_turn = self.play_turn
                        self.play_move = chess.Move.null()
                        self.play_fen = None
                        self.play_turn = None
                        self.engine_finished = False
                        if self.show_ok_message:
                            DisplayDgt.show(self.dgttranslate.text('K05_okpico'))
                        self.reset_menu_results()
                        break
                    if case(MessageApi.USER_MOVE):
                        self.last_move = message.move
                        self.last_fen = message.fen
                        self.last_turn = message.turn
                        self.engine_finished = False
                        if self.show_ok_message:
                            DisplayDgt.show(self.dgttranslate.text('K05_okuser'))
                        break
                    if case(MessageApi.REVIEW_MOVE):
                        self.last_move = message.move
                        self.last_fen = message.fen
                        self.last_turn = message.turn
                        if self.show_ok_message:
                            DisplayDgt.show(self.dgttranslate.text('K05_okmove'))
                        break
                    if case(MessageApi.ALTERNATIVE_MOVE):
                        DisplayDgt.show(self.dgttranslate.text('B05_altmove'))
                        break
                    if case(MessageApi.LEVEL):
                        if self.engine_restart:
                            pass
                        else:
                            if self.show_ok_message or not message.ok_text:
                                DisplayDgt.show(message.level_text)
                            self.exit_display(force=message.ok_text)
                        break
                    if case(MessageApi.TIME_CONTROL):
                        if self.show_ok_message or not message.ok_text:
                            DisplayDgt.show(message.time_text)
                        self.exit_display(force=message.ok_text)
                        break
                    if case(MessageApi.OPENING_BOOK):
                        if self.show_ok_message or not message.ok_text:
                            DisplayDgt.show(message.book_text)
                        self.exit_display(force=message.ok_text)
                        break
                    if case(MessageApi.USER_TAKE_BACK):
                        self.reset_moves_and_score()
                        self.engine_finished = False
                        DisplayDgt.show(self.dgttranslate.text('C00_takeback'))
                        break
                    if case(MessageApi.GAME_ENDS):
                        if not self.engine_restart:  # filter out the shutdown/reboot process
                            ge = message.result.value
                            DisplayDgt.show(self.dgttranslate.text(ge))
                        break
                    if case(MessageApi.INTERACTION_MODE):
                        self.mode_index = message.mode
                        self.mode_result = message.mode  # needed, otherwise Q-placing wont work correctly
                        self.engine_finished = False
                        if self.show_ok_message or not message.ok_text:
                            DisplayDgt.show(message.mode_text)
                        self.exit_display(force=message.ok_text)
                        break
                    if case(MessageApi.PLAY_MODE):
                        DisplayDgt.show(message.play_mode_text)
                        break
                    if case(MessageApi.NEW_SCORE):
                        self.score = message.score
                        self.mate = message.mate
                        if message.mode == Mode.KIBITZ and self.top_result is None:
                            DisplayDgt.show(self.dgttranslate.text('N10_default', str(self.score).rjust(6)))
                        break
                    if case(MessageApi.BOOK_MOVE):
                        self.score = None
                        self.mate = None
                        DisplayDgt.show(self.dgttranslate.text('N10_bookmove'))
                        break
                    if case(MessageApi.NEW_PV):
                        self.hint_move = message.pv[0]
                        self.hint_fen = message.fen
                        self.hint_turn = message.turn
                        if message.mode == Mode.ANALYSIS and self.top_result is None:
                            side = ClockSide.LEFT if (self.hint_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                            DisplayDgt.show(Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen, side=side, wait=False,
                                                             beep=self.dgttranslate.bl(BeepLevel.NO), maxtime=0))
                        break
                    if case(MessageApi.SYSTEM_INFO):
                        self.ip = ' '.join(message.info["ip"].split('.')[2:])
                        break
                    if case(MessageApi.STARTUP_INFO):
                        self.mode_result = message.info['interaction_mode']
                        self.book_index = message.info['book_index']
                        break
                    if case(MessageApi.SEARCH_STARTED):
                        logging.debug('Search started')
                        break
                    if case(MessageApi.SEARCH_STOPPED):
                        logging.debug('Search stopped')
                        break
                    if case(MessageApi.CLOCK_START):
                        tc = message.time_control
                        if tc.mode == TimeMode.FIXED:
                            time_left = time_right = tc.seconds_per_move
                        else:
                            time_left, time_right = tc.current_clock_time(flip_board=self.flip_board)
                            if time_left < 0:
                                time_left = 0
                            if time_right < 0:
                                time_right = 0
                        side = ClockSide.LEFT if (message.turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                        DisplayDgt.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=side))
                        break
                    if case(MessageApi.CLOCK_STOP):
                        DisplayDgt.show(Dgt.CLOCK_STOP())
                        break
                    if case(MessageApi.DGT_BUTTON):
                        button = int(message.button)
                        if not self.engine_restart:
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
                            elif button == 0x11:
                                self.power_off()
                            elif button == 0x40:
                                self.process_lever(right_side_down=True)
                            elif button == -0x40:
                                self.process_lever(right_side_down=False)
                        break
                    if case(MessageApi.DGT_FEN):
                        fen = message.fen
                        if self.flip_board:  # Flip the board if needed
                            fen = fen[::-1]
                        if fen == "RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr":  # Check if we have to flip the board
                            logging.debug('flipping the board')
                            # Flip the board
                            self.flip_board = not self.flip_board
                            # set standard for setup orientation too
                            self.setup_reverse_index = self.flip_board
                            fen = fen[::-1]
                        logging.debug("DGT-Fen: "+fen)
                        if fen == self.dgt_fen:
                            logging.debug('ignore same fen')
                            break
                        self.dgt_fen = fen
                        self.drawresign_fen = self.drawresign()
                        map_bl = self.dgttranslate.bl(BeepLevel.MAP)
                        # Fire the appropriate event
                        if fen in level_map:
                            level = 3 * level_map.index(fen)
                            if level > 20:
                                level = 20
                            self.engine_level_result = level
                            self.engine_level_index = level
                            logging.debug("Map-Fen: New level")
                            text = self.dgttranslate.text('M10_level', str(level).rjust(2))
                            self.fire(Event.LEVEL(level=level, level_text=text, ok_text=False))
                        elif fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR":
                            logging.debug("Map-Fen: New game")
                            self.show_setup_pieces_msg = False
                            self.fire(Event.NEW_GAME())
                        elif fen in book_map:
                            book_index = book_map.index(fen)
                            try:
                                b = self.all_books[book_index]
                                self.book_index = book_index
                                logging.debug("Map-Fen: Opening book [%s]", b[1])
                                text = self.dgttranslate.text('M10_default', b[0])
                                self.fire(Event.SET_OPENING_BOOK(book=b, book_text=text, ok_text=False))
                                self.reset_menu_results()
                            except IndexError:
                                pass
                        elif fen in engine_map:
                            if self.installed_engines:
                                engine_index = engine_map.index(fen)
                                try:
                                    self.engine_index = engine_index
                                    eng = self.installed_engines[self.engine_index]
                                    logging.debug("Map-Fen: Engine name [%s]", eng[1])
                                    eng_text = self.dgttranslate.text('M10_default', eng[1])

                                    level = self.engine_level_index if self.engine_level_result is None else self.engine_level_result
                                    lvl_text = self.dgttranslate.text('M10_level', str(level).rjust(2))
                                    self.fire(Event.LEVEL(level=level, level_text=lvl_text, ok_text=False))
                                    self.fire(Event.NEW_ENGINE(eng=eng, eng_text=eng_text, ok_text=False))
                                    self.engine_restart = True
                                    self.reset_menu_results()
                                except IndexError:
                                    pass
                            else:
                                DisplayDgt.show(self.dgttranslate.text('Y00_erroreng'))
                        elif fen in mode_map:
                            logging.debug("Map-Fen: Interaction mode [%s]", mode_map[fen])
                            text = self.dgttranslate.text(mode_map[fen].value)
                            text.beep = map_bl  # BeepLevel is Map not Button
                            text.maxtime = 1  # wait 1sec not forever
                            self.fire(Event.SET_INTERACTION_MODE(mode=mode_map[fen], mode_text=text,ok_text=False))
                            self.reset_menu_results()
                        elif fen in self.time_control_fixed_map:
                            logging.debug("Map-Fen: Time control fixed")
                            self.time_mode_index = TimeMode.FIXED
                            self.time_control_fixed_index = list(self.time_control_fixed_map.keys()).index(fen)
                            text = self.dgttranslate.text('B00_tc_fixed', self.time_control_fixed_list[self.time_control_fixed_index])
                            text.beep = map_bl  # BeepLevel is Map not Button
                            text.maxtime = 1  # wait 1sec not forever
                            self.fire(Event.SET_TIME_CONTROL(time_control=self.time_control_fixed_map[fen],
                                                             time_text=text, ok_text=False))
                            self.reset_menu_results()
                        elif fen in self.time_control_blitz_map:
                            logging.debug("Map-Fen: Time control blitz")
                            self.time_mode_index = TimeMode.BLITZ
                            self.time_control_blitz_index = list(self.time_control_blitz_map.keys()).index(fen)
                            text = self.dgttranslate.text('B00_tc_blitz', self.time_control_blitz_list[self.time_control_blitz_index])
                            text.beep = map_bl  # BeepLevel is Map not Button
                            text.maxtime = 1  # wait 1sec not forever
                            self.fire(Event.SET_TIME_CONTROL(time_control=self.time_control_blitz_map[fen],
                                                             time_text=text, ok_text=False))
                            self.reset_menu_results()
                        elif fen in self.time_control_fisch_map:
                            logging.debug("Map-Fen: Time control fischer")
                            self.time_mode_index = TimeMode.FISCHER
                            self.time_control_fisch_index = list(self.time_control_fisch_map.keys()).index(fen)
                            text = self.dgttranslate.text('B00_tc_fisch', self.time_control_fisch_list[self.time_control_fisch_index])
                            text.beep = map_bl  # BeepLevel is Map not Button
                            text.maxtime = 1  # wait 1sec not forever
                            self.fire(Event.SET_TIME_CONTROL(time_control=self.time_control_fisch_map[fen],
                                                             time_text=text, ok_text=False))
                            self.reset_menu_results()
                        elif fen in shutdown_map:
                            logging.debug("Map-Fen: shutdown")
                            self.power_off()
                        elif fen in reboot_map:
                            logging.debug("Map-Fen: reboot")
                            self.reboot()
                        elif self.drawresign_fen in drawresign_map:
                            if self.top_result is None:
                                logging.debug("Map-Fen: drawresign")
                                self.fire(Event.DRAWRESIGN(result=drawresign_map[self.drawresign_fen]))
                        else:
                            if self.show_setup_pieces_msg:
                                DisplayDgt.show(self.dgttranslate.text('N00_setpieces'))
                                self.show_setup_pieces_msg = False
                            if self.top_result is None:
                                self.fire(Event.FEN(fen=fen))
                            else:
                                logging.debug('inside the menu. fen "{}" ignored'.format(fen))
                        break
                    if case(MessageApi.DGT_CLOCK_VERSION):
                        DisplayDgt.show(Dgt.CLOCK_VERSION(main_version=message.main_version,
                                                          sub_version=message.sub_version, attached=message.attached))
                        break
                    if case(MessageApi.DGT_CLOCK_TIME):
                        DisplayDgt.show(Dgt.CLOCK_TIME(time_left=message.time_left, time_right=message.time_right))
                        break
                    if case(MessageApi.JACK_CONNECTED_ERROR):  # this will only work in case of 2 clocks connected!
                        DisplayDgt.show(self.dgttranslate.text('Y00_errorjack'))
                        break
                    if case(MessageApi.EBOARD_VERSION):
                        DisplayDgt.show(message.text)
                        break
                    if case(MessageApi.NO_EBOARD_ERROR):
                        if message.is_pi:
                            DisplayDgt.show(message.text)
                        break
                    if case(MessageApi.SWITCH_SIDES):
                        self.engine_finished = False
                        self.hint_move = chess.Move.null()
                        self.hint_fen = None
                        self.hint_turn = None
                        logging.debug('user ignored move {}'.format(message.move))
                        break
                    if case():  # Default
                        # print(message)
                        pass
            except queue.Empty:
                pass
