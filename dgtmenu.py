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
from utilities import TimeMode, BeepLevel, Menu, Mode, Language, Settings, VoiceType, switch, Dgt
from timecontrol import TimeControl
import os


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


class MenuStateMachine(object):
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
        self.engine_restart = False
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
        text = self.dgttranslate.text('B00_okmessage')
        return text

    def enter_sys_disp_okmsg_yesno_menu(self):
        self.state = MenuState.SYS_DISP_OKMSG_YESNO
        msg = 'on' if self.menu_system_display_okmessage_index else 'off'
        text = self.dgttranslate.text('B00_okmessage_' + msg)
        return text

    def enter_sys_disp_ponder_menu(self):
        self.state = MenuState.SYS_DISP_PONDER
        text = self.dgttranslate.text('B00_pondertime')
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
                text = self.enter_mode_menu()
                break
            if case(MenuState.MODE):
                # decide the correct submenu
                text = self.enter_mode_type_menu()
                break
            if case(MenuState.MODE_TYPE):
                # do action!
                text = self.enter_top_menu()
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
                text = self.enter_top_menu()
                break
            if case(MenuState.TIME):
                # decide the correct submenu
                text = self.enter_time_blitz_menu()
                break
            if case(MenuState.TIME_BLITZ):
                text = self.enter_time_blitz_ctrl_menu()
                break
            if case(MenuState.TIME_BLITZ_CTRL):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.TIME_FISCH):
                text = self.enter_time_fisch_ctrl_menu()
                break
            if case(MenuState.TIME_FISCH_CTRL):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.TIME_FIXED):
                text = self.enter_time_fixed_ctrl_menu()
                break
            if case(MenuState.TIME_FIXED_CTRL):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.BOOK):
                text = self.enter_book_name_menu()
                break
            if case(MenuState.BOOK_NAME):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.ENG):
                text = self.enter_eng_name_menu()
                break
            if case(MenuState.ENG_NAME):
                # maybe do action!
                # text = self.enter_top_menu()
                # next line only if engine has level support
                text = self.enter_eng_name_level_menu()
                break
            if case(MenuState.ENG_NAME_LEVEL):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.SYS):
                # decide the correct submenu
                text = self.enter_sys_vers_menu()
                break
            if case(MenuState.SYS_VERS):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.SYS_IP):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.SYS_SOUND):
                text = self.enter_sys_sound_type_menu()
                break
            if case(MenuState.SYS_SOUND_TYPE):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.SYS_LANG):
                text = self.enter_sys_lang_name_menu()
                break
            if case(MenuState.SYS_LANG_NAME):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.SYS_LOG):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.SYS_VOICE):
                text = self.enter_sys_voice_type_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE):
                text = self.enter_sys_voice_type_mute_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE):
                text = self.enter_sys_voice_type_mute_lang_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG):
                text = self.enter_sys_voice_type_mute_lang_speak_menu()
                break
            if case(MenuState.SYS_VOICE_TYPE_MUTE_LANG_SPEAK):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.SYS_DISP):
                # decide the correct submenu
                text = self.enter_sys_disp_okmsg_menu()
                break
            if case(MenuState.SYS_DISP_OKMSG):
                text = self.enter_sys_disp_okmsg_yesno_menu()
                break
            if case(MenuState.SYS_DISP_OKMSG_YESNO):
                # do action!
                text = self.enter_top_menu()
                break
            if case(MenuState.SYS_DISP_PONDER):
                text = self.enter_sys_disp_ponder_time_menu()
                break
            if case(MenuState.SYS_DISP_PONDER_TIME):
                # do action!
                text = self.enter_top_menu()
                break
            if case():  # Default
                break
        return text

    def inside_menu(self):
        return self.state != MenuState.TOP

    def inside_mode(self):
        return self.inside_menu() and self.state in (MenuState.MODE, MenuState.MODE_TYPE)

    def inside_position(self):
        ins = self.state in (MenuState.POS, MenuState.POS_COL, MenuState.POS_READ, MenuState.POS_REV, MenuState.POS_UCI)
        return self.inside_menu() and ins

    def inside_time(self):
        blitz = self.state in (MenuState.TIME_BLITZ, MenuState.TIME_BLITZ_CTRL)
        fisch = self.state in (MenuState.TIME_FISCH, MenuState.TIME_FISCH_CTRL)
        fixed = self.state in (MenuState.TIME_FIXED, MenuState.TIME_FIXED_CTRL)
        return self.inside_menu() and (blitz or fisch or fixed or self.state == MenuState.TIME)

    def inside_book(self):
        return self.inside_menu() and self.state in (MenuState.BOOK, MenuState.BOOK_NAME)

    def inside_engine(self):
        return self.inside_menu() and self.state in (MenuState.ENG, MenuState.ENG_NAME, MenuState.ENG_NAME_LEVEL)

    def inside_system(self):
        versn = self.state == MenuState.SYS_VERS
        ipadr = self.state == MenuState.SYS_IP
        sound = self.state in (MenuState.SYS_SOUND, MenuState.SYS_SOUND_TYPE)
        langu = self.state in (MenuState.SYS_LANG, MenuState.SYS_LANG_NAME)
        lfile = self.state == MenuState.SYS_LOG
        voice = self.state in (MenuState.SYS_VOICE, MenuState.SYS_VOICE_TYPE, MenuState.SYS_VOICE_TYPE_MUTE,
                               MenuState.SYS_VOICE_TYPE_MUTE_LANG, MenuState.SYS_VOICE_TYPE_MUTE_LANG_SPEAK)
        displ = self.state in (MenuState.SYS_DISP, MenuState.SYS_DISP_OKMSG, MenuState.SYS_DISP_OKMSG_YESNO,
                               MenuState.SYS_DISP_PONDER, MenuState.SYS_DISP_PONDER_TIME)
        return self.inside_menu() and (versn or ipadr or sound or langu or lfile or voice or displ or self.state == MenuState.SYS)
