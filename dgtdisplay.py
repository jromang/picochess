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
import math

from dgtiface import *
from engine import get_installed_engines
import threading
from configobj import ConfigObj


class DgtDisplay(Observable, DisplayMsg, threading.Thread):
    def __init__(self, disable_ok_message, dgttranslate):
        super(DgtDisplay, self).__init__()
        self.show_ok_message = not disable_ok_message
        self.dgttranslate = dgttranslate

        self.flip_board = False
        self.dgt_fen = None
        self.engine_finished = False
        self.ip = None
        self.drawresign_fen = None
        self.show_setup_pieces_msg = True
        self.show_move_or_value = 0

        self._reset_moves_and_score()

        self.setup_whitetomove_index = None
        self.setup_whitetomove_result = None
        self.setup_reverse_index = None
        self.setup_reverse_result = None
        self.setup_uci960_index = None
        self.setup_uci960_result = None

        self.top_result = None
        self.top_index = None
        self.mode_result = None
        self.mode_index = None

        self.engine_level_index = None
        self.engine_has_960 = False  # Not all engines support 960 mode - assume not
        self.engine_restart = False
        self.engine_result = None
        self.engine_index = 0
        self.installed_engines = None

        self.book_index = 0
        self.all_books = None

        self.system_index = Settings.VERSION
        self.system_sound_result = None
        self.system_sound_index = self.dgttranslate.beep

        self.system_language_result = None
        langs = {'en': Language.EN, 'de': Language.DE, 'nl': Language.NL, 'fr': Language.FR, 'es': Language.ES}
        self.system_language_index = langs[self.dgttranslate.language]

        self.time_mode_result = None
        self.time_mode_index = TimeMode.BLITZ

        self.time_control_fixed_index = 0
        self.time_control_blitz_index = 2  # Default time control: Blitz, 5min
        self.time_control_fisch_index = 0
        self.time_control_fixed_list = [' 1', ' 3', ' 5', '10', '15', '30', '60', '90']
        self.time_control_blitz_list = [' 1', ' 3', ' 5', '10', '15', '30', '60', '90']
        self.time_control_fisch_list = [' 1  1', ' 3  2', ' 4  2', ' 5  3', '10  5', '15 10', '30 15', '60 30']
        self.time_control_fixed_map = OrderedDict([
            ('rnbqkbnr/pppppppp/Q7/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=1)),
            ('rnbqkbnr/pppppppp/1Q6/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=3)),
            ('rnbqkbnr/pppppppp/2Q5/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=5)),
            ('rnbqkbnr/pppppppp/3Q4/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=10)),
            ('rnbqkbnr/pppppppp/4Q3/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=15)),
            ('rnbqkbnr/pppppppp/5Q2/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=30)),
            ('rnbqkbnr/pppppppp/6Q1/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=60)),
            ('rnbqkbnr/pppppppp/7Q/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=90))])
        self.time_control_blitz_map = OrderedDict([
            ('rnbqkbnr/pppppppp/8/8/Q7/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=1)),
            ('rnbqkbnr/pppppppp/8/8/1Q6/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=3)),
            ('rnbqkbnr/pppppppp/8/8/2Q5/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=5)),
            ('rnbqkbnr/pppppppp/8/8/3Q4/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=10)),
            ('rnbqkbnr/pppppppp/8/8/4Q3/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=15)),
            ('rnbqkbnr/pppppppp/8/8/5Q2/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=30)),
            ('rnbqkbnr/pppppppp/8/8/6Q1/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=60)),
            ('rnbqkbnr/pppppppp/8/8/7Q/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=90))])
        self.time_control_fisch_map = OrderedDict([
            ('rnbqkbnr/pppppppp/8/8/8/Q7/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=1, fischer_increment=1)),
            ('rnbqkbnr/pppppppp/8/8/8/1Q6/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=3, fischer_increment=2)),
            ('rnbqkbnr/pppppppp/8/8/8/2Q5/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=4, fischer_increment=2)),
            ('rnbqkbnr/pppppppp/8/8/8/3Q4/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=5, fischer_increment=3)),
            ('rnbqkbnr/pppppppp/8/8/8/4Q3/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=10, fischer_increment=5)),
            ('rnbqkbnr/pppppppp/8/8/8/5Q2/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=15, fischer_increment=10)),
            ('rnbqkbnr/pppppppp/8/8/8/6Q1/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=30, fischer_increment=15)),
            ('rnbqkbnr/pppppppp/8/8/8/7Q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=60, fischer_increment=30))])

    def _reset_menu_results(self):
        # dont override "mode_result", otherwise wQ a5-e5 wont work anymore (=> if's)
        self.time_mode_result = None
        self.setup_whitetomove_result = None
        self.setup_reverse_result = None
        self.setup_uci960_result = None
        self.top_result = None
        self.engine_result = None
        self.system_sound_result = None
        self.system_language_result = None

    def _power_off(self):
        DisplayDgt.show(self.dgttranslate.text('Y10_goodbye'))
        self.engine_restart = True
        self.fire(Event.SHUTDOWN())

    def _reboot(self):
        DisplayDgt.show(self.dgttranslate.text('Y10_pleasewait'))
        self.engine_restart = True
        self.fire(Event.REBOOT())

    def _reset_moves_and_score(self):
        self.play_move = chess.Move.null()
        self.play_fen = None
        self.play_turn = None
        self.hint_move = chess.Move.null()
        self.hint_fen = None
        self.hint_turn = None
        self.last_move = chess.Move.null()
        self.last_fen = None
        self.last_turn = None
        self.score = self.dgttranslate.text('N10_score', None)
        self.depth = None

    def _combine_depth_and_score(self):
        def score_to_string(score_val, length):
            if length == 's':
                return '{:5.2f}'.format(int(score_val) / 100).replace('.', '')
            if length == 'm':
                return '{:7.2f}'.format(int(score_val) / 100).replace('.', '')
            if length == 'l':
                return '{:9.2f}'.format(int(score_val) / 100).replace('.', '')

        score = copy.copy(self.score)
        try:
            if int(score.s) <= -1000:
                score.s = '-999'
            if int(score.s) >= 1000:
                score.s = '999'
            score.l = '{:3d}{:s}'.format(self.depth, score_to_string(score.l[-8:], 'l'))
            score.m = '{:2d}{:s}'.format(self.depth % 100, score_to_string(score.m[-6:], 'm'))
            score.s = '{:2d}{:s}'.format(self.depth % 100, score_to_string(score.s[-4:], 's'))
            score.rd = ClockDots.DOT
        except ValueError:
            pass
        return score

    def _process_button0(self):
        def top0():
            self._reset_menu_results()
            self._exit_display()

        def mode0():
            self.top_result = Menu.TOP_MENU
            text = self.dgttranslate.text(self.top_index.value)
            DisplayDgt.show(text)

        def position0():
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

        def system0():
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

        def engine0():
            if self.engine_result is None:
                self.top_result = Menu.TOP_MENU
                text = self.dgttranslate.text(self.top_index.value)
            else:
                text = self.installed_engines[self.engine_result]['text']
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
                self.engine_result = None
            DisplayDgt.show(text)

        def book0():
            self.top_result = Menu.TOP_MENU
            text = self.dgttranslate.text(self.top_index.value)
            text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
            DisplayDgt.show(text)

        def time0():
            if self.time_mode_result is None:
                self.top_result = Menu.TOP_MENU
                text = self.dgttranslate.text(self.top_index.value)
            else:
                text = self.dgttranslate.text(self.time_mode_result.value)
                self.time_mode_result = None
            DisplayDgt.show(text)

        if self.top_result is None:
            if self.last_move:
                side = ClockSide.LEFT if (self.last_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                text = Dgt.DISPLAY_MOVE(move=self.last_move, fen=self.last_fen, side=side, wait=False,
                                        beep=self.dgttranslate.bl(BeepLevel.BUTTON), maxtime=1)
            else:
                text = self.dgttranslate.text('B10_nomove')
            DisplayDgt.show(text)
            self._exit_display(wait=True)

        if self.top_result == Menu.TOP_MENU:
            top0()
        elif self.top_result == Menu.MODE_MENU:
            mode0()
        elif self.top_result == Menu.POSITION_MENU:
            position0()
        elif self.top_result == Menu.SYSTEM_MENU:
            system0()
        elif self.top_result == Menu.ENGINE_MENU:
            engine0()
        elif self.top_result == Menu.BOOK_MENU:
            book0()
        elif self.top_result == Menu.TIME_MENU:
            time0()

    def _process_button1(self):
        def top1():
            self.top_index = MenuLoop.prev(self.top_index)
            text = self.dgttranslate.text(self.top_index.value)
            DisplayDgt.show(text)

        def mode1():
            self.mode_index = ModeLoop.prev(self.mode_index)
            text = self.dgttranslate.text(self.mode_index.value)
            DisplayDgt.show(text)

        def position1():
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

        def system1():
            if self.system_sound_result is None and self.system_language_result is None:
                self.system_index = SettingsLoop.prev(self.system_index)
                text = self.dgttranslate.text(self.system_index.value)
            else:
                if self.system_language_result is None:
                    self.system_sound_index = BeepLoop.prev(self.system_sound_index)
                    text = self.dgttranslate.text(self.system_sound_index.value)
                else:
                    self.system_language_index = LanguageLoop.prev(self.system_language_index)
                    text = self.dgttranslate.text(self.system_language_index.value)
            DisplayDgt.show(text)

        def engine1():
            if self.engine_result is None:
                self.engine_index = (self.engine_index-1) % len(self.installed_engines)
                text = self.installed_engines[self.engine_index]['text']
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
            else:
                level_dict = self.installed_engines[self.engine_index]['level_dict']
                self.engine_level_index = (self.engine_level_index-1) % len(level_dict)
                msg = sorted(level_dict)[self.engine_level_index]
                text = self.dgttranslate.text('B00_level', msg)
            DisplayDgt.show(text)

        def book1():
            self.book_index = (self.book_index-1) % len(self.all_books)
            text = self.all_books[self.book_index]['text']
            text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
            DisplayDgt.show(text)

        def time1():
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
                    logging.warning('wrong value for time_mode_index: {}'.format(self.time_mode_index))
                    text = self.dgttranslate.text('Y00_errormenu')
            DisplayDgt.show(text)

        if self.top_result is None:
            text = self._combine_depth_and_score()
            text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
            DisplayDgt.show(text)
            self._exit_display(wait=True)

        if self.top_result == Menu.TOP_MENU:
            top1()
        elif self.top_result == Menu.MODE_MENU:
            mode1()
        elif self.top_result == Menu.POSITION_MENU:
            position1()
        elif self.top_result == Menu.SYSTEM_MENU:
            system1()
        elif self.top_result == Menu.ENGINE_MENU:
            engine1()
        elif self.top_result == Menu.BOOK_MENU:
            book1()
        elif self.top_result == Menu.TIME_MENU:
            time1()

    def _process_button2(self):
        if self.top_result is None:
            if self.engine_finished:
                # @todo Protect against multi entrance of Alt-move
                self.engine_finished = False  # This is not 100% ok, but for the moment better as nothing
                self.fire(Event.ALTERNATIVE_MOVE())
            else:
                if self.mode_result in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
                    text = self.dgttranslate.text('B00_nofunction')
                    DisplayDgt.show(text)
                else:
                    self.fire(Event.PAUSE_RESUME())

    def _process_button3(self):
        def top3():
            self.top_index = MenuLoop.next(self.top_index)
            text = self.dgttranslate.text(self.top_index.value)
            DisplayDgt.show(text)

        def mode3():
            self.mode_index = ModeLoop.next(self.mode_index)
            text = self.dgttranslate.text(self.mode_index.value)
            DisplayDgt.show(text)

        def position3():
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

        def system3():
            if self.system_sound_result is None and self.system_language_result is None:
                self.system_index = SettingsLoop.next(self.system_index)
                text = self.dgttranslate.text(self.system_index.value)
            else:
                if self.system_language_result is None:
                    self.system_sound_index = BeepLoop.next(self.system_sound_index)
                    text = self.dgttranslate.text(self.system_sound_index.value)
                else:
                    self.system_language_index = LanguageLoop.next(self.system_language_index)
                    text = self.dgttranslate.text(self.system_language_index.value)
            DisplayDgt.show(text)

        def engine3():
            if self.engine_result is None:
                self.engine_index = (self.engine_index+1) % len(self.installed_engines)
                text = self.installed_engines[self.engine_index]['text']
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
            else:
                level_dict = self.installed_engines[self.engine_index]['level_dict']
                self.engine_level_index = (self.engine_level_index+1) % len(level_dict)
                msg = sorted(level_dict)[self.engine_level_index]
                text = self.dgttranslate.text('B00_level', msg)
            DisplayDgt.show(text)

        def book3():
            self.book_index = (self.book_index+1) % len(self.all_books)
            text = self.all_books[self.book_index]['text']
            text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
            DisplayDgt.show(text)

        def time3():
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
                    logging.warning('wrong value for time_mode_index: {}'.format(self.time_mode_index))
                    text = self.dgttranslate.text('Y00_errormenu')
            DisplayDgt.show(text)

        if self.top_result is None:
            if self.hint_move:
                side = ClockSide.LEFT if (self.hint_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                text = Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen, side=side, wait=False,
                                        beep=self.dgttranslate.bl(BeepLevel.BUTTON), maxtime=1)
            else:
                text = self.dgttranslate.text('B10_nomove')
            DisplayDgt.show(text)
            self._exit_display(wait=True)

        if self.top_result == Menu.TOP_MENU:
            top3()
        elif self.top_result == Menu.MODE_MENU:
            mode3()
        elif self.top_result == Menu.POSITION_MENU:
            position3()
        elif self.top_result == Menu.SYSTEM_MENU:
            system3()
        elif self.top_result == Menu.ENGINE_MENU:
            engine3()
        elif self.top_result == Menu.BOOK_MENU:
            book3()
        elif self.top_result == Menu.TIME_MENU:
            time3()

    def _process_button4(self):
        def top4():
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
                text = self.all_books[self.book_index]['text']
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
            elif self.top_index == Menu.ENGINE_MENU:
                text = self.installed_engines[self.engine_index]['text']
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)

            elif self.top_index == Menu.SYSTEM_MENU:
                text = self.dgttranslate.text(self.system_index.value)
            else:
                logging.warning('wrong value for topindex: {}'.format(self.top_index))
                text = self.dgttranslate.text('Y00_errormenu')
            DisplayDgt.show(text)

        def mode4():
            self.mode_result = self.mode_index
            text = self.dgttranslate.text('B10_okmode')
            self.fire(Event.SET_INTERACTION_MODE(mode=self.mode_result, mode_text=text, ok_text=True))
            self._reset_menu_results()

        def position4():
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
                            self._reset_moves_and_score()
                            self._reset_menu_results()
                            return
                        else:
                            DisplayDgt.show(self.dgttranslate.text('Y05_illegalpos'))
                            text = self.dgttranslate.text('B00_scanboard')
            DisplayDgt.show(text)

        def system4():
            exit_menu = True
            if self.system_index == Settings.VERSION:
                text = self.dgttranslate.text('B10_picochess')
                text.rd = ClockDots.DOT
                text.wait = False
            elif self.system_index == Settings.IPADR:
                if self.ip:
                    msg = ' '.join(self.ip.split('.')[2:])
                    text = self.dgttranslate.text('B10_default', msg)
                else:
                    text = self.dgttranslate.text('B10_noipadr')
            elif self.system_index == Settings.SOUND:
                if self.system_sound_result is None:
                    self.system_sound_result = self.system_sound_index
                    text = self.dgttranslate.text(self.system_sound_result.value)
                    exit_menu = False
                else:
                    self.dgttranslate.set_beep(self.system_sound_index)
                    config = ConfigObj('picochess.ini')
                    config['beep-config'] = self.dgttranslate.beep_to_config(self.system_sound_index)
                    config.write()
                    text = self.dgttranslate.text('B10_okbeep')
            elif self.system_index == Settings.LANGUAGE:
                if self.system_language_result is None:
                    self.system_language_result = self.system_language_index
                    text = self.dgttranslate.text(self.system_language_result.value)
                    exit_menu = False
                else:
                    langs = {Language.EN: 'en', Language.DE: 'de', Language.NL: 'nl', Language.FR: 'fr', Language.ES: 'es'}
                    language = langs[self.system_language_index]
                    self.dgttranslate.set_language(language)
                    config = ConfigObj('picochess.ini')
                    config['language'] = language
                    config.write()
                    text = self.dgttranslate.text('B10_oklang')
            elif self.system_index == Settings.LOGFILE:
                self.fire(Event.EMAIL_LOG())
                text = self.dgttranslate.text('B10_oklogfile')  # @todo give pos/neg feedback
            else:
                logging.warning('wrong value for system_index: {}'.format(self.system_index))
                text = self.dgttranslate.text('Y00_errormenu')
            DisplayDgt.show(text)
            if exit_menu:
                self._reset_menu_results()
                self._exit_display()

        def engine4():
            eng = self.installed_engines[self.engine_index]
            level_dict = eng['level_dict']
            if self.engine_result is None:
                if level_dict:
                    self.engine_result = self.engine_index
                    if self.engine_level_index is None or len(level_dict) <= self.engine_level_index:
                        self.engine_level_index = len(level_dict) - 1
                    msg = sorted(level_dict)[self.engine_level_index]
                    text = self.dgttranslate.text('B00_level', msg)
                    DisplayDgt.show(text)
                else:
                    config = ConfigObj('picochess.ini')
                    config['engine-level'] = None
                    config.write()
                    text = self.dgttranslate.text('B10_okengine')
                    self.fire(Event.NEW_ENGINE(eng=eng, eng_text=text, options={}, ok_text=True))
                    self.engine_restart = True
                    self._reset_menu_results()
            else:
                if level_dict:
                    msg = sorted(level_dict)[self.engine_level_index]
                    options = level_dict[msg]
                    config = ConfigObj('picochess.ini')
                    config['engine-level'] = msg
                    config.write()
                    self.fire(Event.LEVEL(options={}, level_text=self.dgttranslate.text('B10_level', msg)))
                else:
                    options = {}
                eng_text = self.dgttranslate.text('B10_okengine')
                self.fire(Event.NEW_ENGINE(eng=eng, eng_text=eng_text, options=options, ok_text=True))
                self.engine_restart = True
                self._reset_menu_results()

        def book4():
            text = self.dgttranslate.text('B10_okbook')
            self.fire(Event.SET_OPENING_BOOK(book=self.all_books[self.book_index], book_text=text, ok_text=True))
            self._reset_menu_results()

        def time4():
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
                    logging.warning('wrong value for time_mode_index: {}'.format(self.time_mode_index))
                    text = self.dgttranslate.text('Y00_errormenu')
                DisplayDgt.show(text)
            else:
                if self.time_mode_index == TimeMode.FIXED:
                    time_control = self.time_control_fixed_map[list(self.time_control_fixed_map)[self.time_control_fixed_index]]
                elif self.time_mode_index == TimeMode.BLITZ:
                    time_control = self.time_control_blitz_map[list(self.time_control_blitz_map)[self.time_control_blitz_index]]
                elif self.time_mode_index == TimeMode.FISCHER:
                    time_control = self.time_control_fisch_map[list(self.time_control_fisch_map)[self.time_control_fisch_index]]
                else:
                    logging.warning('wrong value for time_mode_index: {}'.format(self.time_mode_index))
                    text = self.dgttranslate.text('Y00_errormenu')
                    DisplayDgt.show(text)
                    return
                time_left, time_right = time_control.current_clock_time(self.flip_board)
                text = self.dgttranslate.text('B10_oktime')
                self.fire(Event.SET_TIME_CONTROL(time_control=time_control, time_text=text, ok_text=True))
                DisplayDgt.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=ClockSide.NONE))
                self._reset_menu_results()

        if self.top_result is None:
            self.top_result = Menu.TOP_MENU
            self.top_index = Menu.MODE_MENU
            text = self.dgttranslate.text(self.top_index.value)
            DisplayDgt.show(text)

        elif self.top_result == Menu.TOP_MENU:
            top4()
        elif self.top_result == Menu.MODE_MENU:
            mode4()
        elif self.top_result == Menu.POSITION_MENU:
            position4()
        elif self.top_result == Menu.SYSTEM_MENU:
            system4()
        elif self.top_result == Menu.ENGINE_MENU:
            engine4()
        elif self.top_result == Menu.BOOK_MENU:
            book4()
        elif self.top_result == Menu.TIME_MENU:
            time4()

    def _process_lever(self, right_side_down):
        logging.debug('lever position right_side_down: {}'.format(right_side_down))
        if self.top_result is None:
            self.play_move = chess.Move.null()
            self.play_fen = None
            self.play_turn = None
            self.fire(Event.SWITCH_SIDES(engine_finished=self.engine_finished))

    def _drawresign(self):
        _, _, _, rnk_5, rnk_4, _, _, _ = self.dgt_fen.split('/')
        return '8/8/8/' + rnk_5 + '/' + rnk_4 + '/8/8/8'

    def _exit_display(self, wait=False, force=True):
        if self.play_move and self.mode_result in (Mode.NORMAL, Mode.REMOTE):
            side = ClockSide.LEFT if (self.play_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
            text = Dgt.DISPLAY_MOVE(move=self.play_move, fen=self.play_fen, side=side, wait=wait,
                                    beep=self.dgttranslate.bl(BeepLevel.BUTTON), maxtime=1)
        else:
            text = Dgt.DISPLAY_TIME(force=force, wait=True)
        DisplayDgt.show(text)

    def _process_message(self, message):
        level_map = ('rnbqkbnr/pppppppp/8/q7/8/8/PPPPPPPP/RNBQKBNR',
                     'rnbqkbnr/pppppppp/8/1q6/8/8/PPPPPPPP/RNBQKBNR',
                     'rnbqkbnr/pppppppp/8/2q5/8/8/PPPPPPPP/RNBQKBNR',
                     'rnbqkbnr/pppppppp/8/3q4/8/8/PPPPPPPP/RNBQKBNR',
                     'rnbqkbnr/pppppppp/8/4q3/8/8/PPPPPPPP/RNBQKBNR',
                     'rnbqkbnr/pppppppp/8/5q2/8/8/PPPPPPPP/RNBQKBNR',
                     'rnbqkbnr/pppppppp/8/6q1/8/8/PPPPPPPP/RNBQKBNR',
                     'rnbqkbnr/pppppppp/8/7q/8/8/PPPPPPPP/RNBQKBNR')

        book_map = ('rnbqkbnr/pppppppp/8/8/8/q7/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/8/1q6/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/8/2q5/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/8/3q4/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/8/4q3/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/8/5q2/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/8/6q1/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/8/7q/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/q7/8/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/1q6/8/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/2q5/8/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/3q4/8/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/4q3/8/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/5q2/8/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/6q1/8/PPPPPPPP/RNBQKBNR',
                    'rnbqkbnr/pppppppp/8/8/7q/8/PPPPPPPP/RNBQKBNR')

        engine_map = ('rnbqkbnr/pppppppp/q7/8/8/8/PPPPPPPP/RNBQKBNR',
                      'rnbqkbnr/pppppppp/1q6/8/8/8/PPPPPPPP/RNBQKBNR',
                      'rnbqkbnr/pppppppp/2q5/8/8/8/PPPPPPPP/RNBQKBNR',
                      'rnbqkbnr/pppppppp/3q4/8/8/8/PPPPPPPP/RNBQKBNR',
                      'rnbqkbnr/pppppppp/4q3/8/8/8/PPPPPPPP/RNBQKBNR',
                      'rnbqkbnr/pppppppp/5q2/8/8/8/PPPPPPPP/RNBQKBNR',
                      'rnbqkbnr/pppppppp/6q1/8/8/8/PPPPPPPP/RNBQKBNR',
                      'rnbqkbnr/pppppppp/7q/8/8/8/PPPPPPPP/RNBQKBNR')

        shutdown_map = ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQQBNR',
                        'RNBQQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr',
                        '8/8/8/8/8/8/8/3QQ3',
                        '3QQ3/8/8/8/8/8/8/8')

        reboot_map = ('rnbqqbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                      'RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqqbnr',
                      '8/8/8/8/8/8/8/3qq3',
                      '3qq3/8/8/8/8/8/8/8')

        mode_map = {'rnbqkbnr/pppppppp/8/Q7/8/8/PPPPPPPP/RNBQKBNR': Mode.NORMAL,
                    'rnbqkbnr/pppppppp/8/1Q6/8/8/PPPPPPPP/RNBQKBNR': Mode.ANALYSIS,
                    'rnbqkbnr/pppppppp/8/2Q5/8/8/PPPPPPPP/RNBQKBNR': Mode.KIBITZ,
                    'rnbqkbnr/pppppppp/8/3Q4/8/8/PPPPPPPP/RNBQKBNR': Mode.OBSERVE,
                    'rnbqkbnr/pppppppp/8/4Q3/8/8/PPPPPPPP/RNBQKBNR': Mode.REMOTE,
                    'rnbqkbnr/pppppppp/8/5Q2/8/8/PPPPPPPP/RNBQKBNR': Mode.PONDER}

        drawresign_map = {'8/8/8/3k4/4K3/8/8/8': GameResult.WIN_WHITE,
                          '8/8/8/3K4/4k3/8/8/8': GameResult.WIN_WHITE,
                          '8/8/8/4k3/3K4/8/8/8': GameResult.WIN_BLACK,
                          '8/8/8/4K3/3k4/8/8/8': GameResult.WIN_BLACK,
                          '8/8/8/3kK3/8/8/8/8': GameResult.DRAW,
                          '8/8/8/3Kk3/8/8/8/8': GameResult.DRAW,
                          '8/8/8/8/3kK3/8/8/8': GameResult.DRAW,
                          '8/8/8/8/3Kk3/8/8/8': GameResult.DRAW}

        for case in switch(message):
            if case(MessageApi.ENGINE_READY):
                self.engine_index = self.installed_engines.index(message.eng)
                self.engine_has_960 = message.has_960
                if self.show_ok_message or not message.ok_text:
                    DisplayDgt.show(message.eng_text)
                self.engine_restart = False
                self._exit_display(force=message.ok_text)
                break
            if case(MessageApi.ENGINE_STARTUP):
                self.installed_engines = get_installed_engines(message.shell, message.file)
                for index in range(0, len(self.installed_engines)):
                    eng = self.installed_engines[index]
                    if eng['file'] == message.file:
                        self.engine_index = index
                        self.engine_has_960 = message.has_960
                        # @todo preset correct startup level (which needs a message.engine_index parameter)
                        self.engine_level_index = len(eng['level_dict'])-1 if eng['level_dict'] else None
                break
            if case(MessageApi.ENGINE_FAIL):
                DisplayDgt.show(self.dgttranslate.text('Y00_erroreng'))
                break
            if case(MessageApi.COMPUTER_MOVE):
                move = message.move
                ponder = message.ponder
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
                side = ClockSide.LEFT if (turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                DisplayDgt.show(Dgt.DISPLAY_MOVE(move=move, fen=message.fen, side=side, wait=message.wait,
                                                 beep=self.dgttranslate.bl(BeepLevel.CONFIG), maxtime=0))
                DisplayDgt.show(Dgt.LIGHT_SQUARES(uci_move=move.uci()))
                break
            if case(MessageApi.START_NEW_GAME):
                DisplayDgt.show(Dgt.LIGHT_CLEAR())
                self._reset_moves_and_score()
                # self.mode_index = Mode.NORMAL  # @todo
                self._reset_menu_results()
                self.engine_finished = False
                pos960 = message.game.chess960_pos()
                text = self.dgttranslate.text('C10_newgame' if pos960 is None or pos960 == 518 else 'C10_ucigame',
                                              str(pos960))
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
                self._reset_menu_results()
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
                    DisplayDgt.show(message.level_text)
                    self._exit_display(force=False)
                break
            if case(MessageApi.TIME_CONTROL):
                if self.show_ok_message or not message.ok_text:
                    DisplayDgt.show(message.time_text)
                self._exit_display(force=message.ok_text)
                break
            if case(MessageApi.OPENING_BOOK):
                if self.show_ok_message or not message.ok_text:
                    DisplayDgt.show(message.book_text)
                self._exit_display(force=message.ok_text)
                break
            if case(MessageApi.USER_TAKE_BACK):
                DisplayDgt.show(Dgt.LIGHT_CLEAR())
                self._reset_moves_and_score()
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
                self._exit_display(force=message.ok_text)
                break
            if case(MessageApi.PLAY_MODE):
                DisplayDgt.show(message.play_mode_text)
                break
            if case(MessageApi.NEW_SCORE):
                if message.score == 'gaviota':
                    text = self.dgttranslate.text('N10_gaviota', '{}'.format(message.mate))
                else:
                    if message.mate is None:
                        score = int(message.score)
                        if message.turn == chess.BLACK:
                            score *= -1
                        text = self.dgttranslate.text('N10_score', score)
                    else:
                        text = self.dgttranslate.text('N10_mate', str(message.mate))
                self.score = text
                if message.mode == Mode.KIBITZ and self.top_result is None:
                    DisplayDgt.show(self._combine_depth_and_score())
                break
            if case(MessageApi.BOOK_MOVE):
                self.score = self.dgttranslate.text('N10_score', None)
                DisplayDgt.show(self.dgttranslate.text('N10_bookmove'))
                break
            if case(MessageApi.NEW_PV):
                self.hint_move = message.pv[0]
                self.hint_fen = message.fen
                self.hint_turn = message.turn
                if message.mode == Mode.ANALYSIS and self.top_result is None:
                    side = ClockSide.LEFT if (self.hint_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                    DisplayDgt.show(Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen, side=side, wait=True,
                                                     beep=self.dgttranslate.bl(BeepLevel.NO), maxtime=0))
                break
            if case(MessageApi.NEW_DEPTH):
                self.depth = message.depth
                break
            if case(MessageApi.SYSTEM_INFO):
                self.ip = message.info['ip']
                break
            if case(MessageApi.STARTUP_INFO):
                self.mode_index = message.info['interaction_mode']
                self.mode_result = message.info['interaction_mode']
                self.book_index = message.info['book_index']
                self.all_books = message.info['books']
                tc = message.info['time_control']
                self.time_mode_index = tc.mode
                # try to find the index from the given time_control (tc)
                # if user gave a non-existent tc value stay at standard
                index = 0
                if tc.mode == TimeMode.FIXED:
                    for val in self.time_control_fixed_map.values():
                        if val == tc:
                            self.time_control_fixed_index = index
                            break
                        index += 1
                elif tc.mode == TimeMode.BLITZ:
                    for val in self.time_control_blitz_map.values():
                        if val == tc:
                            self.time_control_blitz_index = index
                            break
                        index += 1
                elif tc.mode == TimeMode.FISCHER:
                    for val in self.time_control_fisch_map.values():
                        if val == tc:
                            self.time_control_fisch_index = index
                            break
                        index += 1
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
                        self._process_button0()
                    elif button == 1:
                        self._process_button1()
                    elif button == 2:
                        self._process_button2()
                    elif button == 3:
                        self._process_button3()
                    elif button == 4:
                        self._process_button4()
                    elif button == 0x11:
                        self._power_off()
                    elif button == 0x40:
                        self._process_lever(right_side_down=True)
                    elif button == -0x40:
                        self._process_lever(right_side_down=False)
                break
            if case(MessageApi.DGT_FEN):
                fen = message.fen
                if self.flip_board:  # Flip the board if needed
                    fen = fen[::-1]
                if fen == 'RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr':  # Check if we have to flip the board
                    logging.debug('flipping the board')
                    # Flip the board
                    self.flip_board = not self.flip_board
                    # set standard for setup orientation too
                    self.setup_reverse_index = self.flip_board
                    fen = fen[::-1]
                logging.debug("DGT-Fen [%s]", fen)
                if fen == self.dgt_fen:
                    logging.debug('ignore same fen')
                    break
                self.dgt_fen = fen
                self.drawresign_fen = self._drawresign()
                # Fire the appropriate event
                if fen in level_map:
                    eng = self.installed_engines[self.engine_index]
                    level_dict = eng['level_dict']
                    if level_dict:
                        inc = math.ceil(len(level_dict) / 8)
                        self.engine_level_index = min(inc * level_map.index(fen), len(level_dict)-1)
                        msg = sorted(level_dict)[self.engine_level_index]
                        text = self.dgttranslate.text('M10_level', msg)
                        logging.debug("Map-Fen: New level {}".format(msg))
                        config = ConfigObj('picochess.ini')
                        config['engine-level'] = msg
                        config.write()
                        self.fire(Event.LEVEL(options=level_dict[msg], level_text=text))
                    else:
                        logging.debug('engine doesnt support levels')
                elif fen in book_map:
                    book_index = book_map.index(fen)
                    try:
                        b = self.all_books[book_index]
                        self.book_index = book_index
                        logging.debug("Map-Fen: Opening book [%s]", b['file'])
                        text = b['text']
                        text.beep = self.dgttranslate.bl(BeepLevel.MAP)
                        text.maxtime = 1
                        self.fire(Event.SET_OPENING_BOOK(book=b, book_text=text, ok_text=False))
                        self._reset_menu_results()
                    except IndexError:
                        pass
                elif fen in engine_map:
                    if self.installed_engines:
                        engine_index = engine_map.index(fen)
                        try:
                            self.engine_index = engine_index
                            eng = self.installed_engines[self.engine_index]
                            level_dict = eng['level_dict']
                            logging.debug("Map-Fen: Engine name [%s]", eng['name'])
                            eng_text = eng['text']
                            eng_text.beep = self.dgttranslate.bl(BeepLevel.MAP)
                            eng_text.maxtime = 1
                            if level_dict:
                                if self.engine_level_index is None or len(level_dict) <= self.engine_level_index:
                                    self.engine_level_index = len(level_dict)-1
                                msg = sorted(level_dict)[self.engine_level_index]
                                options = level_dict[msg]  # cause of "new-engine", send options lateron - now only {}
                                self.fire(Event.LEVEL(options={}, level_text=self.dgttranslate.text('M10_level', msg)))
                            else:
                                msg = None
                                options = {}
                            config = ConfigObj('picochess.ini')
                            config['engine-level'] = msg
                            config.write()
                            self.fire(Event.NEW_ENGINE(eng=eng, eng_text=eng_text, options=options, ok_text=False))
                            self.engine_restart = True
                            self._reset_menu_results()
                        except IndexError:
                            pass
                    else:
                        DisplayDgt.show(self.dgttranslate.text('Y00_erroreng'))
                elif fen in mode_map:
                    logging.debug("Map-Fen: Interaction mode [%s]", mode_map[fen])
                    text = self.dgttranslate.text(mode_map[fen].value)
                    text.beep = self.dgttranslate.bl(BeepLevel.MAP)
                    text.maxtime = 1  # wait 1sec not forever
                    self.fire(Event.SET_INTERACTION_MODE(mode=mode_map[fen], mode_text=text, ok_text=False))
                    self._reset_menu_results()
                elif fen in self.time_control_fixed_map:
                    logging.debug('Map-Fen: Time control fixed')
                    self.time_mode_index = TimeMode.FIXED
                    self.time_control_fixed_index = list(self.time_control_fixed_map.keys()).index(fen)
                    text = self.dgttranslate.text('M10_tc_fixed', self.time_control_fixed_list[self.time_control_fixed_index])
                    self.fire(Event.SET_TIME_CONTROL(time_control=self.time_control_fixed_map[fen],
                                                     time_text=text, ok_text=False))
                    self._reset_menu_results()
                elif fen in self.time_control_blitz_map:
                    logging.debug('Map-Fen: Time control blitz')
                    self.time_mode_index = TimeMode.BLITZ
                    self.time_control_blitz_index = list(self.time_control_blitz_map.keys()).index(fen)
                    text = self.dgttranslate.text('M10_tc_blitz', self.time_control_blitz_list[self.time_control_blitz_index])
                    self.fire(Event.SET_TIME_CONTROL(time_control=self.time_control_blitz_map[fen],
                                                     time_text=text, ok_text=False))
                    self._reset_menu_results()
                elif fen in self.time_control_fisch_map:
                    logging.debug('Map-Fen: Time control fischer')
                    self.time_mode_index = TimeMode.FISCHER
                    self.time_control_fisch_index = list(self.time_control_fisch_map.keys()).index(fen)
                    text = self.dgttranslate.text('M10_tc_fisch', self.time_control_fisch_list[self.time_control_fisch_index])
                    self.fire(Event.SET_TIME_CONTROL(time_control=self.time_control_fisch_map[fen],
                                                     time_text=text, ok_text=False))
                    self._reset_menu_results()
                elif fen in shutdown_map:
                    logging.debug('Map-Fen: shutdown')
                    self._power_off()
                elif fen in reboot_map:
                    logging.debug('Map-Fen: reboot')
                    self._reboot()
                elif self.drawresign_fen in drawresign_map:
                    if self.top_result is None:
                        logging.debug('Map-Fen: drawresign')
                        self.fire(Event.DRAWRESIGN(result=drawresign_map[self.drawresign_fen]))
                elif '/pppppppp/8/8/8/8/PPPPPPPP/' in fen:  # check for the lines 2-7 cause could be an uci960 pos too
                    bit_board = chess.Board(fen + ' w - - 0 1')
                    pos960 = bit_board.chess960_pos(ignore_castling=True)
                    if pos960 is not None:
                        if pos960 == 518 or self.engine_has_960:
                            logging.debug('Map-Fen: New game')
                            self.show_setup_pieces_msg = False
                            self.fire(Event.NEW_GAME(pos960=pos960))
                        else:
                            # self._reset_moves_and_score()
                            DisplayDgt.show(self.dgttranslate.text('Y00_error960'))
                else:
                    if self.top_result is None:
                        if self.show_setup_pieces_msg:
                            DisplayDgt.show(self.dgttranslate.text('N00_setpieces'))
                            # self.show_setup_pieces_msg = False @todo does that work?
                        self.fire(Event.FEN(fen=fen))
                    else:
                        logging.debug('inside the menu. fen "{}" ignored'.format(fen))
                break
            if case(MessageApi.DGT_CLOCK_VERSION):
                DisplayDgt.show(Dgt.CLOCK_VERSION(main=message.main, sub=message.sub, attached=message.attached))
                break
            if case(MessageApi.DGT_CLOCK_TIME):
                DisplayDgt.show(Dgt.CLOCK_TIME(time_left=message.time_left, time_right=message.time_right))
                break
            if case(MessageApi.DGT_SERIAL_NR):
                # logging.debug('Serial number {}'.format(message.number))  # actually used for watchdog (once a second)
                if self.mode_result == Mode.PONDER and self.top_result is None:
                    if self.show_move_or_value > 1:
                        if self.hint_move:
                            show_left = (self.hint_turn == chess.WHITE) != self.flip_board
                            text = Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen,
                                                    side=ClockSide.LEFT if show_left else ClockSide.RIGHT, wait=True,
                                                    beep=self.dgttranslate.bl(BeepLevel.NO), maxtime=1)
                        else:
                            text = self.dgttranslate.text('N10_nomove')
                    else:
                        text = self._combine_depth_and_score()
                    text.wait = True
                    DisplayDgt.show(text)
                    self.show_move_or_value = (self.show_move_or_value + 1) % 4
                break
            if case(MessageApi.JACK_CONNECTED_ERROR):  # this will only work in case of 2 clocks connected!
                DisplayDgt.show(self.dgttranslate.text('Y00_errorjack'))
                break
            if case(MessageApi.EBOARD_VERSION):
                DisplayDgt.show(message.text)
                break
            if case(MessageApi.NO_EBOARD_ERROR):
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

    def run(self):
        logging.info('msg_queue ready')
        while True:
            # Check if we have something to display
            try:
                message = self.msg_queue.get()
                logging.debug("received message from msg_queue: %s", message)
                self._process_message(message)
            except queue.Empty:
                pass
