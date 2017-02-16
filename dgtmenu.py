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

from configobj import ConfigObj
from collections import OrderedDict
from utilities import TimeMode, TimeModeLoop, BeepLevel, BeepLoop, Menu, MenuLoop, Mode, ModeLoop, Language, LanguageLoop
from utilities import Settings, SettingsLoop, VoiceType, VoiceTypeLoop, SystemDisplay, SystemDisplayLoop
from utilities import Observable, DisplayDgt, switch, Dgt, Event, ClockIcons
from timecontrol import TimeControl
import chess
import os
import logging


class MenuState(object):
    TOP = 100000

    MODE = 200000
    MODE_TYPE = 210000  # normal, observe, ...

    POS = 300000
    POS_COL = 310000
    POS_REV = 311000
    POS_UCI = 311100
    POS_READ = 311110

    TIME = 400000
    TIME_BLITZ = 410000  # blitz, fischer, fixed
    TIME_BLITZ_CTRL = 411000  # time_control objs
    TIME_FISCH = 420000
    TIME_FISCH_CTRL = 421000
    TIME_FIXED = 430000
    TIME_FIXED_CTRL = 431000

    BOOK = 500000
    BOOK_NAME = 510000

    ENG = 600000
    ENG_NAME = 610000
    ENG_NAME_LEVEL = 611000

    SYS = 700000
    SYS_VERS = 710000
    SYS_IP = 720000
    SYS_SOUND = 730000
    SYS_SOUND_TYPE = 731000  # never, always, some
    SYS_LANG = 740000
    SYS_LANG_NAME = 741000  # de, en, ...
    SYS_LOG = 750000
    SYS_VOICE = 760000
    SYS_VOICE_TYPE = 761000
    SYS_VOICE_TYPE_MUTE = 761100  # on, off
    SYS_VOICE_TYPE_MUTE_LANG = 761110
    SYS_VOICE_TYPE_MUTE_LANG_SPEAK = 761111  # al, christina, ...
    SYS_DISP = 770000
    SYS_DISP_OKMSG = 771000
    SYS_DISP_OKMSG_YESNO = 771100  # yes,no
    SYS_DISP_PONDER = 772000
    SYS_DISP_PONDER_TIME = 772100  # 1-8


class MenuStateMachine(Observable):
    def __init__(self, dgttranslate):
        super(MenuStateMachine, self).__init__()
        self.state = MenuState.TOP
        self.dgttranslate = dgttranslate

        self.menu_setup_whitetomove_index = None
        self.menu_setup_reverse_index = None
        self.menu_setup_uci960_index = None

        self.menu_inside_flag = False
        self.menu_top_index = Menu.MODE_MENU
        self.menu_mode_index = Mode.NORMAL

        self.engine_level_index = None
        self.engine_has_960 = False  # Not all engines support 960 mode - assume not
        # self.engine_restart = False @todo Its inside the dgtdisplay function!
        self.menu_engine_name_index = 0
        self.installed_engines = None

        self.menu_book_index = 0
        self.all_books = None

        self.menu_system_index = Settings.VERSION
        self.menu_system_sound_beep_index = self.dgttranslate.beep

        langs = {'en': Language.EN, 'de': Language.DE, 'nl': Language.NL,
                 'fr': Language.FR, 'es': Language.ES, 'it': Language.IT}
        self.menu_system_language_lang_index = langs[self.dgttranslate.language]

        self.voices_conf = ConfigObj('talker' + os.sep + 'voices' + os.sep + 'voices.ini')
        self.menu_system_voice_type_result = None
        self.menu_system_voice_type_index = VoiceType.COMP_VOICE
        self.menu_system_voice_mute_index = False  # @todo set this to 'True' if mute voice choosen
        try:
            self.menu_system_voice_lang_index = self.voices_conf.keys().index(self.dgttranslate.language)
        except ValueError:
            self.menu_system_voice_lang_index = 0
        self.menu_system_voice_speak_index = 0

        self.menu_system_display_index = SystemDisplay.PONDER_TIME
        self.menu_system_display_okmessage_index = False
        self.menu_system_display_pondertime_index = 3 # self.ponder_time

        self.menu_time_mode_index = TimeMode.BLITZ

        self.tc_fixed_index = 0
        self.tc_blitz_index = 2  # Default time control: Blitz, 5min
        self.tc_fisch_index = 0
        self.tc_fixed_list = [' 1', ' 3', ' 5', '10', '15', '30', '60', '90']
        self.tc_blitz_list = [' 1', ' 3', ' 5', '10', '15', '30', '60', '90']
        self.tc_fisch_list = [' 1  1', ' 3  2', ' 4  2', ' 5  3', '10  5', '15 10', '30 15', '60 30']
        self.tc_fixed_map = OrderedDict([
            ('rnbqkbnr/pppppppp/Q7/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=1)),
            ('rnbqkbnr/pppppppp/1Q6/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=3)),
            ('rnbqkbnr/pppppppp/2Q5/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=5)),
            ('rnbqkbnr/pppppppp/3Q4/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=10)),
            ('rnbqkbnr/pppppppp/4Q3/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=15)),
            ('rnbqkbnr/pppppppp/5Q2/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=30)),
            ('rnbqkbnr/pppppppp/6Q1/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=60)),
            ('rnbqkbnr/pppppppp/7Q/8/8/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FIXED, seconds_per_move=90))])
        self.tc_blitz_map = OrderedDict([
            ('rnbqkbnr/pppppppp/8/8/Q7/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=1)),
            ('rnbqkbnr/pppppppp/8/8/1Q6/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=3)),
            ('rnbqkbnr/pppppppp/8/8/2Q5/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=5)),
            ('rnbqkbnr/pppppppp/8/8/3Q4/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=10)),
            ('rnbqkbnr/pppppppp/8/8/4Q3/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=15)),
            ('rnbqkbnr/pppppppp/8/8/5Q2/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=30)),
            ('rnbqkbnr/pppppppp/8/8/6Q1/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=60)),
            ('rnbqkbnr/pppppppp/8/8/7Q/8/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.BLITZ, minutes_per_game=90))])
        self.tc_fisch_map = OrderedDict([
            ('rnbqkbnr/pppppppp/8/8/8/Q7/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=1, fischer_increment=1)),
            ('rnbqkbnr/pppppppp/8/8/8/1Q6/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=3, fischer_increment=2)),
            ('rnbqkbnr/pppppppp/8/8/8/2Q5/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=4, fischer_increment=2)),
            ('rnbqkbnr/pppppppp/8/8/8/3Q4/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=5, fischer_increment=3)),
            ('rnbqkbnr/pppppppp/8/8/8/4Q3/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=10, fischer_increment=5)),
            ('rnbqkbnr/pppppppp/8/8/8/5Q2/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=15, fischer_increment=10)),
            ('rnbqkbnr/pppppppp/8/8/8/6Q1/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=30, fischer_increment=15)),
            ('rnbqkbnr/pppppppp/8/8/8/7Q/PPPPPPPP/RNBQKBNR', TimeControl(TimeMode.FISCHER, minutes_per_game=60, fischer_increment=30))])

    def _reset_menu_results(self):
        self.state = MenuState.TOP

    def get(self):
        return self.state

    def enter_top_menu(self):
        self.state = MenuState.TOP
        text = self.dgttranslate.text(self.menu_top_index.value)
        print('enter_TOP_menu')
        return text

    def enter_mode_menu(self):
        self.state = MenuState.MODE
        text = self.dgttranslate.text(Menu.MODE_MENU.value)
        return text

    def enter_mode_type_menu(self):
        self.state = MenuState.MODE_TYPE
        text = self.dgttranslate.text(self.menu_mode_index.value)
        return text

    def enter_pos_menu(self):
        self.state = MenuState.POS
        text = self.dgttranslate.text(Menu.POSITION_MENU.value)
        return text

    def enter_pos_color_menu(self):
        self.state = MenuState.POS_COL
        text = self.dgttranslate.text('B00_sidewhite' if self.menu_setup_whitetomove_index else 'B00_sideblack')
        return text

    def enter_pos_rev_menu(self):
        self.state = MenuState.POS_REV
        text = self.dgttranslate.text('B00_bw' if self.menu_setup_reverse_index else 'B00_wb')
        return text

    def enter_pos_uci_menu(self):
        self.state = MenuState.POS_UCI
        text = self.dgttranslate.text('B00_960yes' if self.menu_setup_uci960_index else 'B00_960no')
        return text

    def enter_pos_read_menu(self):
        self.state = MenuState.POS_READ
        text = self.dgttranslate.text('B00_scanboard')
        return text

    def enter_time_menu(self):
        self.state = MenuState.TIME
        text = self.dgttranslate.text(Menu.TIME_MENU.value)
        return text

    def enter_time_blitz_menu(self):
        self.state = MenuState.TIME_BLITZ
        text = self.dgttranslate.text(self.menu_time_mode_index.value)
        return text

    def enter_time_blitz_ctrl_menu(self):
        self.state = MenuState.TIME_BLITZ_CTRL
        text = self.dgttranslate.text('B00_tc_blitz', self.tc_blitz_list[self.tc_blitz_index])
        return text

    def enter_time_fisch_menu(self):
        self.state = MenuState.TIME_FISCH
        text = self.dgttranslate.text(self.menu_time_mode_index.value)
        return text

    def enter_time_fisch_ctrl_menu(self):
        self.state = MenuState.TIME_FISCH_CTRL
        text = self.dgttranslate.text('B00_tc_fisch', self.tc_fisch_list[self.tc_fisch_index])
        return text

    def enter_time_fixed_menu(self):
        self.state = MenuState.TIME_FIXED
        text = self.dgttranslate.text(self.menu_time_mode_index.value)
        return text

    def enter_time_fixed_ctrl_menu(self):
        self.state = MenuState.TIME_FIXED_CTRL
        text = self.dgttranslate.text('B00_tc_fixed', self.tc_fixed_list[self.tc_fixed_index])
        return text

    def enter_book_menu(self):
        self.state = MenuState.BOOK
        text = self.dgttranslate.text(Menu.BOOK_MENU.value)
        return text

    def enter_book_name_menu(self):
        self.state = MenuState.BOOK_NAME
        text = self.all_books[self.menu_book_index]['text']
        text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
        return text

    def enter_eng_menu(self):
        self.state = MenuState.ENG
        text = self.dgttranslate.text(Menu.ENGINE_MENU.value)
        return text

    def enter_eng_name_menu(self):
        self.state = MenuState.ENG_NAME
        text = self.installed_engines[self.menu_engine_name_index]['text']
        text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
        return text

    def enter_eng_name_level_menu(self):
        self.state = MenuState.ENG_NAME_LEVEL
        eng = self.installed_engines[self.menu_engine_name_index]
        level_dict = eng['level_dict']
        if level_dict:
            if self.engine_level_index is None or len(level_dict) <= self.engine_level_index:
                self.engine_level_index = len(level_dict) - 1
            msg = sorted(level_dict)[self.engine_level_index]
            text = self.dgttranslate.text('B00_level', msg)
        else:
            text = self.dgttranslate.text('Y00_errormenu')
        return text

    def enter_sys_menu(self):
        self.state = MenuState.SYS
        text = self.dgttranslate.text(Menu.SYSTEM_MENU.value)
        return text

    def enter_sys_vers_menu(self):
        self.state = MenuState.SYS_VERS
        text = self.dgttranslate.text(self.menu_system_index.value)
        return text

    def enter_sys_ip_menu(self):
        self.state = MenuState.SYS_IP
        text = self.dgttranslate.text(self.menu_system_index.value)
        return text

    def enter_sys_sound_menu(self):
        self.state = MenuState.SYS_SOUND
        text = self.dgttranslate.text(self.menu_system_index.value)
        return text

    def enter_sys_sound_type_menu(self):
        self.state = MenuState.SYS_SOUND_TYPE
        text = self.dgttranslate.text(self.menu_system_sound_beep_index.value)
        return text

    def enter_sys_lang_menu(self):
        self.state = MenuState.SYS_LANG
        text = self.dgttranslate.text(self.menu_system_index.value)
        return text

    def enter_sys_lang_name_menu(self):
        self.state = MenuState.SYS_LANG_NAME
        text = self.dgttranslate.text(self.menu_system_language_lang_index.value)
        return text

    def enter_sys_log_menu(self):
        self.state = MenuState.SYS_LOG
        text = self.dgttranslate.text(self.menu_system_index.value)
        return text

    def enter_sys_voice_menu(self):
        self.state = MenuState.SYS_VOICE
        text = self.dgttranslate.text(self.menu_system_index.value)
        return text

    def enter_sys_voice_type_menu(self):
        self.state = MenuState.SYS_VOICE_TYPE
        text = self.dgttranslate.text(self.menu_system_voice_type_index.value)
        return text

    def enter_sys_voice_type_mute_menu(self):
        self.state = MenuState.SYS_VOICE_TYPE_MUTE
        msg = 'on' if self.menu_system_voice_mute_index else 'off'
        text = self.dgttranslate.text('B00_voice_' + msg)
        return text

    def enter_sys_voice_type_mute_lang_menu(self):
        self.state = MenuState.SYS_VOICE_TYPE_MUTE_LANG
        vkey = self.voices_conf.keys()[self.menu_system_voice_lang_index]
        text = self.dgttranslate.text('B00_language_' + vkey + '_menu')
        return text

    def enter_sys_voice_type_mute_lang_speak_menu(self):
        self.state = MenuState.SYS_VOICE_TYPE_MUTE_LANG_SPEAK
        vkey = self.voices_conf.keys()[self.menu_system_voice_lang_index]
        speakers = self.voices_conf[vkey]
        speaker = speakers[list(speakers)[self.menu_system_voice_speak_index]]
        text = Dgt.DISPLAY_TEXT(l=speaker['large'], m=speaker['medium'], s=speaker['small'])
        text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
        text.wait = False
        text.maxtime = 0
        text.devs = {'ser', 'i2c', 'web'}
        return text

    def enter_sys_disp_menu(self):
        self.state = MenuState.SYS_DISP
        text = self.dgttranslate.text(self.menu_system_index.value)
        return text

    def enter_sys_disp_okmsg_menu(self):
        self.state = MenuState.SYS_DISP_OKMSG
        text = self.dgttranslate.text(SystemDisplay.OK_MESSAGE.value)
        return text

    def enter_sys_disp_okmsg_yesno_menu(self):
        self.state = MenuState.SYS_DISP_OKMSG_YESNO
        msg = 'on' if self.menu_system_display_okmessage_index else 'off'
        text = self.dgttranslate.text('B00_okmessage_' + msg)
        return text

    def enter_sys_disp_ponder_menu(self):
        self.state = MenuState.SYS_DISP_PONDER
        text = self.dgttranslate.text(SystemDisplay.PONDER_TIME.value)
        return text

    def enter_sys_disp_ponder_time_menu(self):
        self.state = MenuState.SYS_DISP_PONDER_TIME
        text = self.dgttranslate.text('B00_pondertime_time', str(self.menu_system_display_pondertime_index))
        return text

    def up(self):
        text = self.dgttranslate.text('Y00_errormenu')
        for case in switch(self.state):
            if case(MenuState.TOP):
                break
            if case(MenuState.MODE):
                text = self.enter_top_menu()
                break
            if case(MenuState.MODE_TYPE):
                text = self.enter_mode_menu()
                break
            if case(MenuState.POS):
                text = self.enter_top_menu()
                break
            if case(MenuState.POS_COL):
                text = self.enter_pos_menu()
                break
            if case(MenuState.POS_REV):
                text = self.enter_pos_color_menu()
                break
            if case(MenuState.POS_UCI):
                text = self.enter_pos_rev_menu()
                break
            if case(MenuState.POS_READ):
                text = self.enter_pos_uci_menu()
                break
            if case(MenuState.TIME):
                text = self.enter_top_menu()
                break
            if case(MenuState.TIME_BLITZ):
                text = self.enter_time_menu()
                break
            if case(MenuState.TIME_BLITZ_CTRL):
                text = self.enter_time_blitz_menu()
                break
            if case(MenuState.TIME_FISCH):
                text = self.enter_time_menu()
                break
            if case(MenuState.TIME_FISCH_CTRL):
                text = self.enter_time_fisch_menu()
                break
            if case(MenuState.TIME_FIXED):
                text = self.enter_time_menu()
                break
            if case(MenuState.TIME_FIXED_CTRL):
                text = self.enter_time_fixed_menu()
                break
            if case(MenuState.BOOK):
                text = self.enter_top_menu()
                break
            if case(MenuState.BOOK_NAME):
                text = self.enter_book_menu()
                break
            if case(MenuState.ENG):
                text = self.enter_top_menu()
                break
            if case(MenuState.ENG_NAME):
                text = self.enter_eng_menu()
                break
            if case(MenuState.ENG_NAME_LEVEL):
                text = self.enter_eng_name_menu()
                break
            if case(MenuState.SYS):
                text = self.enter_top_menu()
                break
            if case(MenuState.SYS_VERS):
                text = self.enter_sys_menu()
                break
            if case(MenuState.SYS_IP):
                text = self.enter_sys_menu()
                break
            if case(MenuState.SYS_SOUND):
                text = self.enter_sys_menu()
                break
            if case(MenuState.SYS_SOUND_TYPE):
                text = self.enter_sys_sound_menu()
                break
            if case(MenuState.SYS_LANG):
                text = self.enter_sys_menu()
                break
            if case(MenuState.SYS_LANG_NAME):
                text = self.enter_sys_lang_menu()
                break
            if case(MenuState.SYS_LOG):
                text = self.enter_sys_menu()
                break
            if case(MenuState.SYS_VOICE):
                text = self.enter_sys_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE):
                text = self.enter_sys_voice_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE):
                text = self.enter_sys_voice_type_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG):
                text = self.enter_sys_voice_type_mute_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG_SPEAK):
                text = self.enter_sys_voice_type_mute_lang_menu()
                break
            if case(MenuState.SYS_DISP):
                text = self.enter_sys_menu()
                break
            if case(MenuState.SYS_DISP_OKMSG):
                text = self.enter_sys_disp_menu()
                break
            if case(MenuState.SYS_DISP_OKMSG_YESNO):
                text = self.enter_sys_disp_okmsg_menu()
                break
            if case(MenuState.SYS_DISP_PONDER):
                text = self.enter_sys_disp_menu()
                break
            if case(MenuState.SYS_DISP_PONDER_TIME):
                text = self.enter_sys_disp_ponder_menu()
                break
            if case():  # Default
                break
        return text

    def down(self):
        text = self.dgttranslate.text('Y00_errormenu')
        for case in switch(self.state):
            if case(MenuState.TOP):
                if self.menu_top_index == Menu.MODE_MENU:
                    text = self.enter_mode_menu()
                if self.menu_top_index == Menu.POSITION_MENU:
                    text = self.enter_pos_menu()
                if self.menu_top_index == Menu.TIME_MENU:
                    text = self.enter_time_menu()
                if self.menu_top_index == Menu.BOOK_MENU:
                    text = self.enter_book_menu()
                if self.menu_top_index == Menu.ENGINE_MENU:
                    text = self.enter_eng_menu()
                if self.menu_top_index == Menu.SYSTEM_MENU:
                    text = self.enter_sys_menu()
                break
            if case(MenuState.MODE):
                text = self.enter_mode_type_menu()
                break
            if case(MenuState.MODE_TYPE):
                # do action!
                text = self.dgttranslate.text('B10_okmode')
                self.menu_mode_result = self.menu_mode_index
                self.fire(Event.SET_INTERACTION_MODE(mode=self.menu_mode_result, mode_text=text, ok_text=True))
                self._reset_menu_results()
                break
            if case(MenuState.POS):
                text = self.enter_pos_color_menu()
                break
            if case(MenuState.POS_COL):
                text = self.enter_pos_rev_menu()
                break
            if case(MenuState.POS_REV):
                text = self.enter_pos_uci_menu()
                break
            if case(MenuState.POS_UCI):
                text = self.enter_pos_read_menu()
                break
            if case(MenuState.POS_READ):
                # do action!
                to_move = 'w' if self.menu_setup_whitetomove_index else 'b'
                fen = self.dgt_fen
                if self.flip_board != self.menu_setup_reverse_index:
                    logging.debug('flipping the board')
                    fen = fen[::-1]
                fen += " {0} KQkq - 0 1".format(to_move)
                bit_board = chess.Board(fen, self.menu_setup_uci960_index)
                # ask python-chess to correct the castling string
                bit_board.set_fen(bit_board.fen())
                if bit_board.is_valid():
                    self.flip_board = self.menu_setup_reverse_index
                    self.fire(Event.SETUP_POSITION(fen=bit_board.fen(), uci960=self.menu_setup_uci960_index))
                    # self._reset_moves_and_score() done in "START_NEW_GAME"
                    self._reset_menu_results()
                    return
                else:
                    DisplayDgt.show(self.dgttranslate.text('Y05_illegalpos'))
                    text = self.dgttranslate.text('B00_scanboard')
                break
            if case(MenuState.TIME):
                if self.menu_time_mode_index == TimeMode.BLITZ:
                    text = self.enter_time_blitz_menu()
                if self.menu_time_mode_index == TimeMode.FISCHER:
                    text = self.enter_time_fisch_menu()
                if self.menu_time_mode_index == TimeMode.FIXED:
                    text = self.enter_time_fixed_menu()
                break
            if case(MenuState.TIME_BLITZ):
                text = self.enter_time_blitz_ctrl_menu()
                break
            if case(MenuState.TIME_BLITZ_CTRL):
                # do action!
                text = self.dgttranslate.text('B10_oktime')
                time_control = self.tc_blitz_map[list(self.tc_blitz_map)[self.tc_blitz_index]]
                self.fire(Event.SET_TIME_CONTROL(time_control=time_control, time_text=text, ok_text=True))
                self._reset_menu_results()
                break
            if case(MenuState.TIME_FISCH):
                text = self.enter_time_fisch_ctrl_menu()
                break
            if case(MenuState.TIME_FISCH_CTRL):
                # do action!
                text = self.dgttranslate.text('B10_oktime')
                time_control = self.tc_fisch_map[list(self.tc_fisch_map)[self.tc_fisch_index]]
                self.fire(Event.SET_TIME_CONTROL(time_control=time_control, time_text=text, ok_text=True))
                self._reset_menu_results()
                break
            if case(MenuState.TIME_FIXED):
                text = self.enter_time_fixed_ctrl_menu()
                break
            if case(MenuState.TIME_FIXED_CTRL):
                # do action!
                text = self.dgttranslate.text('B10_oktime')
                time_control = self.tc_fixed_map[list(self.tc_fixed_map)[self.tc_fixed_index]]
                self.fire(Event.SET_TIME_CONTROL(time_control=time_control, time_text=text, ok_text=True))
                self._reset_menu_results()
                break
            if case(MenuState.BOOK):
                text = self.enter_book_name_menu()
                break
            if case(MenuState.BOOK_NAME):
                # do action!
                text = self.dgttranslate.text('B10_okbook')
                self.fire(Event.SET_OPENING_BOOK(book=self.all_books[self.menu_book_index], book_text=text, ok_text=True))
                self._reset_menu_results()
                break
            if case(MenuState.ENG):
                text = self.enter_eng_name_menu()
                break
            if case(MenuState.ENG_NAME):
                # maybe do action!
                eng = self.installed_engines[self.menu_engine_name_index]
                level_dict = eng['level_dict']
                if level_dict:
                    if self.engine_level_index is None or len(level_dict) <= self.engine_level_index:
                        self.engine_level_index = len(level_dict) - 1
                    msg = sorted(level_dict)[self.engine_level_index]
                    text = self.dgttranslate.text('B00_level', msg)
                    DisplayDgt.show(text)
                else:
                    config = ConfigObj('picochess.ini')
                    config['engine-level'] = None
                    config.write()
                    eng_text = self.dgttranslate.text('B10_okengine')
                    self.fire(Event.NEW_ENGINE(eng=eng, eng_text=eng_text, options={}, ok_text=True))
                    self.engine_restart = True
                    self._reset_menu_results()
                break
            if case(MenuState.ENG_NAME_LEVEL):
                # do action!
                eng = self.installed_engines[self.menu_engine_name_index]
                level_dict = eng['level_dict']
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
                break
            if case(MenuState.SYS):
                if self.menu_system_index == Settings.VERSION:
                    text = self.enter_sys_vers_menu()
                if self.menu_system_index == Settings.IPADR:
                    text = self.enter_sys_ip_menu()
                if self.menu_system_index == Settings.SOUND:
                    text = self.enter_sys_sound_menu()
                if self.menu_system_index == Settings.LANGUAGE:
                    text = self.enter_sys_lang_menu()
                if self.menu_system_index == Settings.LOGFILE:
                    text = self.enter_sys_log_menu()
                if self.menu_system_index == Settings.VOICE:
                    text = self.enter_sys_voice_menu()
                if self.menu_system_index == Settings.DISPLAY:
                    text = self.enter_sys_disp_menu()
                break
            if case(MenuState.SYS_VERS):
                # do action!
                text = self.dgttranslate.text('B10_picochess')
                text.rd = ClockIcons.DOT
                text.wait = False
                break
            if case(MenuState.SYS_IP):
                # do action!
                if self.ip:
                    msg = ' '.join(self.ip.split('.')[:2])
                    text = self.dgttranslate.text('B07_default', msg)
                    if len(msg) == 7:  # delete the " " for XL incase its "123 456"
                        text.s = msg[:3] + msg[4:]
                    DisplayDgt.show(text)
                    msg = ' '.join(self.ip.split('.')[2:])
                    text = self.dgttranslate.text('N07_default', msg)
                    if len(msg) == 7:  # delete the " " for XL incase its "123 456"
                        text.s = msg[:3] + msg[4:]
                    text.wait = True
                else:
                    text = self.dgttranslate.text('B10_noipadr')
                break
            if case(MenuState.SYS_SOUND):
                text = self.enter_sys_sound_type_menu()
                break
            if case(MenuState.SYS_SOUND_TYPE):
                # do action!
                self.dgttranslate.set_beep(self.menu_system_sound_beep_index)
                config = ConfigObj('picochess.ini')
                config['beep-config'] = self.dgttranslate.beep_to_config(self.menu_system_sound_beep_index)
                config.write()
                text = self.dgttranslate.text('B10_okbeep')
                break
            if case(MenuState.SYS_LANG):
                text = self.enter_sys_lang_name_menu()
                break
            if case(MenuState.SYS_LANG_NAME):
                # do action!
                langs = {Language.EN: 'en', Language.DE: 'de', Language.NL: 'nl',
                         Language.FR: 'fr', Language.ES: 'es', Language.IT: 'it'}
                language = langs[self.menu_system_language_lang_index]
                self.dgttranslate.set_language(language)
                config = ConfigObj('picochess.ini')
                config['language'] = language
                config.write()
                text = self.dgttranslate.text('B10_oklang')
                break
            if case(MenuState.SYS_LOG):
                # do action!
                self.fire(Event.EMAIL_LOG())
                text = self.dgttranslate.text('B10_oklogfile')  # @todo give pos/neg feedback
                break
            if case(MenuState.SYS_VOICE):
                text = self.enter_sys_voice_type_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE):
                text = self.enter_sys_voice_type_mute_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE):
                # maybe do action!
                # config = ConfigObj('picochess.ini')
                # ckey = 'user' if self.menu_system_voice_type_index == VoiceType.USER_VOICE else 'computer'
                # if ckey + '-voice' in config:
                #     del (config[ckey + '-voice'])
                #     config.write()
                # self.fire(Event.SET_VOICE(type=self.menu_system_voice_type_index, lang=vkey, speaker='mute'))
                # text = self.dgttranslate.text('B10_okvoice')
                text = self.enter_sys_voice_type_mute_lang_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG):
                text = self.enter_sys_voice_type_mute_lang_speak_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG_SPEAK):
                # do action!
                vkey = self.voices_conf.keys()[self.menu_system_voice_lang_index]
                speakers = self.voices_conf[vkey].keys()
                config = ConfigObj('picochess.ini')
                ckey = 'user' if self.menu_system_voice_type_index == VoiceType.USER_VOICE else 'computer'
                skey = speakers[self.menu_system_voice_speak_index]
                config[ckey + '-voice'] = vkey + ':' + skey
                config.write()
                self.fire(Event.SET_VOICE(type=self.menu_system_voice_type_index, lang=vkey, speaker=skey))
                text = self.dgttranslate.text('B10_okvoice')
                break
            if case(MenuState.SYS_DISP):
                if self.menu_system_display_index == SystemDisplay.PONDER_TIME:
                    text = self.enter_sys_disp_ponder_menu()
                if self.menu_system_display_index == SystemDisplay.OK_MESSAGE:
                    text = self.enter_sys_disp_okmsg_menu()
                break
            if case(MenuState.SYS_DISP_OKMSG):
                text = self.enter_sys_disp_okmsg_yesno_menu()
                break
            if case(MenuState.SYS_DISP_OKMSG_YESNO):
                # do action!
                config = ConfigObj('picochess.ini')
                config['disable-ok-message'] = self.menu_system_display_okmessage_index
                config.write()
                self.show_ok_message = self.menu_system_display_okmessage_index
                text = self.dgttranslate.text('B10_okmessage')
                break
            if case(MenuState.SYS_DISP_PONDER):
                text = self.enter_sys_disp_ponder_time_menu()
                break
            if case(MenuState.SYS_DISP_PONDER_TIME):
                # do action!
                config = ConfigObj('picochess.ini')
                config['ponder-time'] = self.menu_system_display_pondertime_index
                config.write()
                self.ponder_time = self.menu_system_display_pondertime_index
                text = self.dgttranslate.text('B10_okpondertime')
                break
            if case():  # Default
                break
        return text

    def left(self):
        text = self.dgttranslate.text('Y00_errormenu')
        for case in switch(self.state):
            if case(MenuState.TOP):
                break
            if case(MenuState.MODE):
                self.state = MenuState.SYS
                self.menu_top_index = MenuLoop.prev(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.MODE_TYPE):
                self.menu_mode_index = ModeLoop.prev(self.menu_mode_index)
                text = self.dgttranslate.text(self.menu_mode_index.value)
                break
            if case(MenuState.POS):
                self.state = MenuState.MODE
                self.menu_top_index = MenuLoop.prev(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.POS_COL):
                self.menu_setup_whitetomove_index = not self.menu_setup_whitetomove_index
                text = self.dgttranslate.text('B00_sidewhite' if self.menu_setup_whitetomove_index else 'B00_sideblack')
                break
            if case(MenuState.POS_REV):
                self.menu_setup_reverse_index = not self.menu_setup_reverse_index
                text = self.dgttranslate.text('B00_bw' if self.menu_setup_reverse_index else 'B00_wb')
                break
            if case(MenuState.POS_UCI):
                if self.engine_has_960:
                    self.menu_setup_uci960_index = not self.menu_setup_uci960_index
                    text = self.dgttranslate.text('B00_960yes' if self.menu_setup_uci960_index else 'B00_960no')
                else:
                    text = self.dgttranslate.text('Y00_error960')
                break
            if case(MenuState.POS_READ):
                break
            if case(MenuState.TIME):
                self.state = MenuState.POS
                self.menu_top_index = MenuLoop.prev(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.TIME_BLITZ):
                self.state = MenuState.TIME_FIXED
                self.menu_time_mode_index = TimeModeLoop.prev(self.menu_time_mode_index)
                text = self.dgttranslate.text(self.menu_time_mode_index.value)
                break
            if case(MenuState.TIME_BLITZ_CTRL):
                self.tc_blitz_index = (self.tc_blitz_index - 1) % len(self.tc_blitz_map)
                text = self.dgttranslate.text('B00_tc_blitz', self.tc_blitz_list[self.tc_blitz_index])
                break
            if case(MenuState.TIME_FISCH):
                self.state = MenuState.TIME_BLITZ
                self.menu_time_mode_index = TimeModeLoop.prev(self.menu_time_mode_index)
                text = self.dgttranslate.text(self.menu_time_mode_index.value)
                break
            if case(MenuState.TIME_FISCH_CTRL):
                self.tc_fisch_index = (self.tc_fisch_index - 1) % len(self.tc_fisch_map)
                text = self.dgttranslate.text('B00_tc_fisch', self.tc_fisch_list[self.tc_fisch_index])
                break
            if case(MenuState.TIME_FIXED):
                self.state = MenuState.TIME_FISCH
                self.menu_time_mode_index = TimeModeLoop.prev(self.menu_time_mode_index)
                text = self.dgttranslate.text(self.menu_time_mode_index.value)
                break
            if case(MenuState.TIME_FIXED_CTRL):
                self.tc_fixed_index = (self.tc_fixed_index - 1) % len(self.tc_fixed_map)
                text = self.dgttranslate.text('B00_tc_fixed', self.tc_fixed_list[self.tc_fixed_index])
                break
            if case(MenuState.BOOK):
                self.state = MenuState.TIME
                self.menu_top_index = MenuLoop.prev(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.BOOK_NAME):
                self.menu_book_index = (self.menu_book_index - 1) % len(self.all_books)
                text = self.all_books[self.menu_book_index]['text']
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
                break
            if case(MenuState.ENG):
                self.state = MenuState.BOOK
                self.menu_top_index = MenuLoop.prev(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.ENG_NAME):
                self.menu_engine_name_index = (self.menu_engine_name_index - 1) % len(self.installed_engines)
                text = self.installed_engines[self.menu_engine_name_index]['text']
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
                break
            if case(MenuState.ENG_NAME_LEVEL):
                level_dict = self.installed_engines[self.menu_engine_name_index]['level_dict']
                self.engine_level_index = (self.engine_level_index - 1) % len(level_dict)
                msg = sorted(level_dict)[self.engine_level_index]
                text = self.dgttranslate.text('B00_level', msg)
                break
            if case(MenuState.SYS):
                self.state = MenuState.ENG
                self.menu_top_index = MenuLoop.prev(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.SYS_VERS):
                self.state = MenuState.SYS_DISP
                self.menu_system_index = SettingsLoop.prev(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_IP):
                self.state = MenuState.SYS_VERS
                self.menu_system_index = SettingsLoop.prev(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_SOUND):
                self.state = MenuState.SYS_IP
                self.menu_system_index = SettingsLoop.prev(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_SOUND_TYPE):
                self.menu_system_sound_beep_index = BeepLoop.prev(self.menu_system_sound_beep_index)
                text = self.dgttranslate.text(self.menu_system_sound_beep_index.value)
                break
            if case(MenuState.SYS_LANG):
                self.state = MenuState.SYS_SOUND
                self.menu_system_index = SettingsLoop.prev(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_LANG_NAME):
                self.menu_system_language_lang_index = LanguageLoop.prev(self.menu_system_language_lang_index)
                text = self.dgttranslate.text(self.menu_system_language_lang_index.value)
                break
            if case(MenuState.SYS_LOG):
                self.state = MenuState.SYS_LANG
                self.menu_system_index = SettingsLoop.prev(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_VOICE):
                self.state = MenuState.SYS_LOG
                self.menu_system_index = SettingsLoop.prev(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_VOICE_TYPE):
                self.menu_system_voice_type_index = VoiceTypeLoop.prev(self.menu_system_voice_type_index)
                text = self.dgttranslate.text(self.menu_system_voice_type_index.value)
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE):
                self.menu_system_voice_mute_index = not self.menu_system_voice_mute_index
                msg = 'on' if self.menu_system_voice_mute_index else 'off'
                text = self.dgttranslate.text('B00_voice_' + msg)
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG):
                self.menu_system_voice_lang_index = (self.menu_system_voice_lang_index - 1) % len(self.voices_conf)
                vkey = self.voices_conf.keys()[self.menu_system_voice_lang_index]
                text = self.dgttranslate.text('B00_language_' + vkey + '_menu')  # voice using same as language
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG_SPEAK):
                vkey = self.voices_conf.keys()[self.menu_system_voice_lang_index]
                speakers = self.voices_conf[vkey]
                self.menu_system_voice_speak_index = (self.menu_system_voice_speak_index - 1) % len(speakers)
                speaker = speakers[list(speakers)[self.menu_system_voice_speak_index]]
                text = Dgt.DISPLAY_TEXT(l=speaker['large'], m=speaker['medium'], s=speaker['small'])
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
                text.wait = False
                text.maxtime = 0
                text.devs = {'ser', 'i2c', 'web'}
                break
            if case(MenuState.SYS_DISP):
                self.state = MenuState.SYS_VOICE
                self.menu_system_index = SettingsLoop.prev(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_DISP_OKMSG):
                self.state = MenuState.SYS_DISP_PONDER
                self.menu_system_display_index = SystemDisplayLoop.prev(self.menu_system_display_index)
                text = self.dgttranslate.text(self.menu_system_display_index.value)
                break
            if case(MenuState.SYS_DISP_OKMSG_YESNO):
                self.menu_system_display_okmessage_index = not self.menu_system_display_okmessage_index
                msg = 'on' if self.menu_system_display_okmessage_index else 'off'
                text = self.dgttranslate.text('B00_okmessage_' + msg)
                break
            if case(MenuState.SYS_DISP_PONDER):
                self.state = MenuState.SYS_DISP_OKMSG
                self.menu_system_display_index = SystemDisplayLoop.prev(self.menu_system_display_index)
                text = self.dgttranslate.text(self.menu_system_display_index.value)
                break
            if case(MenuState.SYS_DISP_PONDER_TIME):
                self.menu_system_display_pondertime_index -= 1
                if self.menu_system_display_pondertime_index < 1:
                    self.menu_system_display_pondertime_index = 8
                text = self.dgttranslate.text('B00_pondertime_time', str(self.menu_system_display_pondertime_index))
                break
            if case():  # Default
                break
        return text

    def right(self):
        text = self.dgttranslate.text('Y00_errormenu')
        for case in switch(self.state):
            if case(MenuState.TOP):
                break
            if case(MenuState.MODE):
                self.state = MenuState.POS
                self.menu_top_index = MenuLoop.next(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.MODE_TYPE):
                self.menu_mode_index = ModeLoop.next(self.menu_mode_index)
                text = self.dgttranslate.text(self.menu_mode_index.value)
                break
            if case(MenuState.POS):
                self.state = MenuState.TIME
                self.menu_top_index = MenuLoop.next(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.POS_COL):
                self.menu_setup_whitetomove_index = not self.menu_setup_whitetomove_index
                text = self.dgttranslate.text('B00_sidewhite' if self.menu_setup_whitetomove_index else 'B00_sideblack')
                break
            if case(MenuState.POS_REV):
                self.menu_setup_reverse_index = not self.menu_setup_reverse_index
                text = self.dgttranslate.text('B00_bw' if self.menu_setup_reverse_index else 'B00_wb')
                break
            if case(MenuState.POS_UCI):
                if self.engine_has_960:
                    self.menu_setup_uci960_index = not self.menu_setup_uci960_index
                    text = self.dgttranslate.text('B00_960yes' if self.menu_setup_uci960_index else 'B00_960no')
                else:
                    text = self.dgttranslate.text('Y00_error960')
                break
            if case(MenuState.POS_READ):
                break
            if case(MenuState.TIME):
                self.state = MenuState.BOOK
                self.menu_top_index = MenuLoop.next(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.TIME_BLITZ):
                self.state = MenuState.TIME_FIXED
                self.menu_time_mode_index = TimeModeLoop.next(self.menu_time_mode_index)
                text = self.dgttranslate.text(self.menu_time_mode_index.value)
                break
            if case(MenuState.TIME_BLITZ_CTRL):
                self.tc_blitz_index = (self.tc_blitz_index + 1) % len(self.tc_blitz_map)
                text = self.dgttranslate.text('B00_tc_blitz', self.tc_blitz_list[self.tc_blitz_index])
                break
            if case(MenuState.TIME_FISCH):
                self.state = MenuState.TIME_BLITZ
                self.menu_time_mode_index = TimeModeLoop.next(self.menu_time_mode_index)
                text = self.dgttranslate.text(self.menu_time_mode_index.value)
                break
            if case(MenuState.TIME_FISCH_CTRL):
                self.tc_fisch_index = (self.tc_fisch_index + 1) % len(self.tc_fisch_map)
                text = self.dgttranslate.text('B00_tc_fisch', self.tc_fisch_list[self.tc_fisch_index])
                break
            if case(MenuState.TIME_FIXED):
                self.state = MenuState.TIME_FISCH
                self.menu_time_mode_index = TimeModeLoop.next(self.menu_time_mode_index)
                text = self.dgttranslate.text(self.menu_time_mode_index.value)
                break
            if case(MenuState.TIME_FIXED_CTRL):
                self.tc_fixed_index = (self.tc_fixed_index + 1) % len(self.tc_fixed_map)
                text = self.dgttranslate.text('B00_tc_fixed', self.tc_fixed_list[self.tc_fixed_index])
                break
            if case(MenuState.BOOK):
                self.state = MenuState.ENG
                self.menu_top_index = MenuLoop.next(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.BOOK_NAME):
                self.menu_book_index = (self.menu_book_index + 1) % len(self.all_books)
                text = self.all_books[self.menu_book_index]['text']
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
                break
            if case(MenuState.ENG):
                self.state = MenuState.SYS
                self.menu_top_index = MenuLoop.next(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.ENG_NAME):
                self.menu_engine_name_index = (self.menu_engine_name_index + 1) % len(self.installed_engines)
                text = self.installed_engines[self.menu_engine_name_index]['text']
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
                break
            if case(MenuState.ENG_NAME_LEVEL):
                level_dict = self.installed_engines[self.menu_engine_name_index]['level_dict']
                self.engine_level_index = (self.engine_level_index + 1) % len(level_dict)
                msg = sorted(level_dict)[self.engine_level_index]
                text = self.dgttranslate.text('B00_level', msg)
                break
            if case(MenuState.SYS):
                self.state = MenuState.MODE
                self.menu_top_index = MenuLoop.next(self.menu_top_index)
                text = self.dgttranslate.text(self.menu_top_index.value)
                break
            if case(MenuState.SYS_VERS):
                self.state = MenuState.SYS_IP
                self.menu_system_index = SettingsLoop.next(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_IP):
                self.state = MenuState.SYS_SOUND
                self.menu_system_index = SettingsLoop.next(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_SOUND):
                self.state = MenuState.SYS_LANG
                self.menu_system_index = SettingsLoop.next(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_SOUND_TYPE):
                self.menu_system_sound_beep_index = BeepLoop.next(self.menu_system_sound_beep_index)
                text = self.dgttranslate.text(self.menu_system_sound_beep_index.value)
                break
            if case(MenuState.SYS_LANG):
                self.state = MenuState.SYS_LOG
                self.menu_system_index = SettingsLoop.next(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_LANG_NAME):
                self.menu_system_language_lang_index = LanguageLoop.next(self.menu_system_language_lang_index)
                text = self.dgttranslate.text(self.menu_system_language_lang_index.value)
                break
            if case(MenuState.SYS_LOG):
                self.state = MenuState.SYS_VOICE
                self.menu_system_index = SettingsLoop.next(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_VOICE):
                self.state = MenuState.SYS_DISP
                self.menu_system_index = SettingsLoop.next(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_VOICE_TYPE):
                self.menu_system_voice_type_index = VoiceTypeLoop.next(self.menu_system_voice_type_index)
                text = self.dgttranslate.text(self.menu_system_voice_type_index.value)
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE):
                self.menu_system_voice_mute_index = not self.menu_system_voice_mute_index
                msg = 'on' if self.menu_system_voice_mute_index else 'off'
                text = self.dgttranslate.text('B00_voice_' + msg)
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG):
                self.menu_system_voice_lang_index = (self.menu_system_voice_lang_index + 1) % len(self.voices_conf)
                vkey = self.voices_conf.keys()[self.menu_system_voice_lang_index]
                text = self.dgttranslate.text('B00_language_' + vkey + '_menu')  # voice using same as language
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG_SPEAK):
                vkey = self.voices_conf.keys()[self.menu_system_voice_lang_index]
                speakers = self.voices_conf[vkey]
                self.menu_system_voice_speak_index = (self.menu_system_voice_speak_index + 1) % len(speakers)
                speaker = speakers[list(speakers)[self.menu_system_voice_speak_index]]
                text = Dgt.DISPLAY_TEXT(l=speaker['large'], m=speaker['medium'], s=speaker['small'])
                text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
                text.wait = False
                text.maxtime = 0
                text.devs = {'ser', 'i2c', 'web'}
                break
            if case(MenuState.SYS_DISP):
                self.state = MenuState.SYS_VERS
                self.menu_system_index = SettingsLoop.next(self.menu_system_index)
                text = self.dgttranslate.text(self.menu_system_index.value)
                break
            if case(MenuState.SYS_DISP_OKMSG):
                self.state = MenuState.SYS_DISP_PONDER
                self.menu_system_display_index = SystemDisplayLoop.next(self.menu_system_display_index)
                text = self.dgttranslate.text(self.menu_system_display_index.value)
                break
            if case(MenuState.SYS_DISP_OKMSG_YESNO):
                self.menu_system_display_okmessage_index = not self.menu_system_display_okmessage_index
                msg = 'on' if self.menu_system_display_okmessage_index else 'off'
                text = self.dgttranslate.text('B00_okmessage_' + msg)
                break
            if case(MenuState.SYS_DISP_PONDER):
                self.state = MenuState.SYS_DISP_OKMSG
                self.menu_system_display_index = SystemDisplayLoop.next(self.menu_system_display_index)
                text = self.dgttranslate.text(self.menu_system_display_index.value)
                break
            if case(MenuState.SYS_DISP_PONDER_TIME):
                self.menu_system_display_pondertime_index += 1
                if self.menu_system_display_pondertime_index > 8:
                    self.menu_system_display_pondertime_index = 1
                text = self.dgttranslate.text('B00_pondertime_time', str(self.menu_system_display_pondertime_index))
                break
            if case():  # Default
                break
        return text

    def inside_menu(self):
        return self.state != MenuState.TOP
