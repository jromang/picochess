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
import pifacecad

from timecontrol import *
from collections import OrderedDict
from utilities import *

from dgtinterface import *
import threading

piface_testpath = "/dev/spidev0.0"

piface_icons = [0x1f,0x11,0xa,0x4,0xa,0x11,0x1f,0x0],[0x1f,0x11,0xa,0x4,0xa,0x1f,0x1f,0x0], [0x1f,0x11,0xa,0x4,0xe,0x1f,0x1f,0x0]

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

shutdown_map = ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQQBNR",
                "8/8/8/8/8/8/8/3QQ3",
                "3QQ3/8/8/8/8/8/8/8")

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

        
class DGTDisplay(Observable, Display, threading.Thread):
    def __init__(self, ok_move_messages):
        super(DGTDisplay, self).__init__()
        self.ok_moves_messages = ok_move_messages
        
        if (os.path.exists(piface_testpath)):
            self.cad = pifacecad.PiFaceCAD()
            self.cad.lcd.clear()
        self.PiFaceExists = os.path.exists(piface_testpath)
        self.pifaceUpdate = False
        self.side = 0x00
        self.thinkerboll = 0
        self.piface_toptext = ""
        self.piface_buttomtext = ""
            
        self.dgtintf = DGTInterface
        
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

        self.time_control_mode = ClockMode.BLITZ
        self.time_control_fen_map = None
        self.build_time_control_fens()
        self.time_control_index = 10  # index for selecting new time control
        self.time_control_menu_index = 2  # index for selecting new time control
        self.time_control_fen = list(time_control_map.keys())[self.time_control_index]  # Default time control: Blitz, 5min
        
        self.pifi_lefttime = 300
        self.pifi_righttime = 300
        thread_input = threading.Thread(target=self.pifi_timertick)
        thread_input.start()

    def show_pifi(self, text_line1 = None, text_line2 = None, icon = None):
        if (self.PiFaceExists is False):
            return
        logging.debug('show_pifi %s , %s ' % (text_line1, text_line2))
        
        while(self.pifaceUpdate is True):
            time.sleep(0.05)
            
        self.pifaceUpdate = True
        self.cad.lcd.blink_off()
        self.cad.lcd.cursor_off()
        if ((text_line1 != None) or (text_line2 != None)):
            if ((text_line1 != None) and (text_line2 != None)):
                self.cad.lcd.clear()
            self.cad.lcd.backlight_on()


            if (text_line1 is not None):
                logging.debug('show_pifi : headline = %s ' % text_line1)
                newtext = text_line1.ljust(14,' ')
                if (newtext is not self.piface_toptext):
                    self.cad.lcd.set_cursor(0, 0)
                    self.cad.lcd.write(newtext)
                    self.piface_toptext = newtext

            if (text_line2 is not None):
                logging.debug('show_pifi : buttomline = %s ' % text_line2)
                newtext = text_line2.ljust(14,' ')
                if (newtext is not self.piface_buttomtext):
                    self.cad.lcd.set_cursor(0, 1)
                    self.cad.lcd.write(newtext)
                    self.piface_buttomtext = newtext

        if (icon is not None):
            logging.debug('show_pifi : icon  line=%i  pos=%i  icon=%i ' % (icon[0],icon[1],icon[2]))
            self.cad.lcd.set_cursor(icon[0],icon[1])
            if (icon[2] < 0):
                icon[2] = 0
            if (icon[2] > 14):
                icon[2] = 14                
            self.cad.lcd.write_custom_bitmap(icon[2])

        self.pifaceUpdate = False
        
    def getTimeString(self, timestring):
        #a = (2 * 60 * 60) + (12 * 60 ) + 25
        hour = 60 * 60
        min = 60
        
        a = int(timestring)
        h = str(int((a - (a % hour)) / hour)).rjust(2,'0')
        a = a % hour
        m = str(int((a - (a % min)) / min)).rjust(2,'0')
        a = int(a % min)
        s = str(a).rjust(2,'0')

        if (h == "00"):
            return ("%s:%s" % (m,s))
        else:
            return ("%s:%s:%s" % (h,m,s))
        
        
    def pifi_timertick(self):
        if (self.PiFaceExists is False):
            return
 
        bLasClear = True
 
        # init PiFace Icons
        #logging.debug('init PiFace Icons')
        #i = 0
        
        #for piface_icon in piface_icons:
        #    logging.debug('add Icon %i' % i)
        #    quaver = pifacecad.LCDBitmap(piface_icon)
        #    self.cad.lcd.store_custom_bitmap(i, quaver)
        #    self.cad.lcd.write_custom_bitmap(i)
        #    i += 1
        
        logging.debug('init PiFace Timer')
        while True:
            if (self.side == 0x1 and self.pifi_lefttime > 0):
                self.pifi_lefttime = self.pifi_lefttime -1
            if (self.side == 0x2 and self.pifi_righttime > 0):
                self.pifi_righttime = self.pifi_righttime -1

            time.sleep(1)
            
            if (self.side != 0x3):
                bLasClear = False
                if (self.pifaceUpdate is False):
                    self.pifaceUpdate = True
                    self.cad.lcd.set_cursor(0, 1)
                    self.cad.lcd.write(self.getTimeString(self.pifi_lefttime) + "  "  + self.getTimeString(self.pifi_righttime))
                    self.pifaceUpdate = False
            else:
                if (bLasClear is False):
                    self.show_pifi(None,"".ljust(18,' ')) 
                    bLasClear = True

    def power_off(self):
        DgtDisplay.show(Dgt.DISPLAY_TEXT(text="good bye", xl="bye", beep=BeepLevel.YES, duration=0))
        self.show_pifi("good bye")
        self.engine_restart = True
        self.fire(Event.SHUTDOWN())

    def reboot(self):
        DgtDisplay.show(Dgt.DISPLAY_TEXT(text="pls wait", xl="wait", beep=BeepLevel.YES, duration=0))
        self.show_pifi("please wait")
        self.engine_restart = True
        self.fire(Event.REBOOT())

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
                DgtDisplay.show(Dgt.DISPLAY_MOVE(move=self.last_move, fen=self.last_fen, beep=BeepLevel.BUTTON, duration=1))
            else:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="no move", xl="nomove", beep=BeepLevel.YES, duration=1))

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_to_move = chess.WHITE if self.setup_to_move == chess.BLACK else chess.BLACK
            to_move = PlayMode.PLAY_WHITE if self.setup_to_move == chess.WHITE else PlayMode.PLAY_BLACK
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text=to_move.value, xl=None, beep=BeepLevel.BUTTON, duration=0))

        if self.dgt_clock_menu == Menu.LEVEL_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            elif self.engine_has_levels:
                # Display current level
                level = str(self.engine_level)
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="level " + level, xl="lvl " + level, beep=BeepLevel.BUTTON, duration=0))
            else:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="no level", xl="no lvl", beep=BeepLevel.YES, duration=0))

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text='pico ' + version, xl='pic ' + version, beep=BeepLevel.BUTTON, duration=0))

        if self.dgt_clock_menu == Menu.ENGINE_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            else:
                # Display current engine
                msg = (self.installed_engines[self.engine_index])[1]
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=msg, xl=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        if self.dgt_clock_menu == Menu.BOOK_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            else:
                # Display current book
                msg = (self.all_books[self.book_index])[0]
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=msg, xl=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        if self.dgt_clock_menu == Menu.TIME_MENU:
            # Select a time control mode
            try:
                self.time_control_mode = ClockMode(self.time_control_mode.value + 1)
            except ValueError:
                self.time_control_mode = ClockMode(1)
            self.build_time_control_fens()
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text=time_controls[self.time_control_mode], xl=None, beep=BeepLevel.BUTTON, duration=0))
            self.time_control_index = 0
            self.time_control_menu_index = self.time_control_index
            self.time_control_fen = self.time_control_fen_map[self.time_control_index]

    def process_button1(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            if self.display_move:
                if bool(self.hint_move):
                    DgtDisplay.show(Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen,
                                    beep=BeepLevel.BUTTON, duration=1))
                else:
                    DgtDisplay.show(Dgt.DISPLAY_TEXT(text="no move", xl="nomove", beep=BeepLevel.YES, duration=1))
            else:
                if self.mate is None:
                    sc = 'no scr' if self.score is None else str(self.score).rjust(6)
                else:
                    sc = 'm ' + str(self.mate)
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=sc, xl=None, beep=BeepLevel.BUTTON, duration=1))
            self.display_move = not self.display_move

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_reverse_orientation = not self.setup_reverse_orientation
            orientation_xl = "b    w" if self.setup_reverse_orientation else "w    b"
            orientation = " b     w" if self.setup_reverse_orientation else " w     b"
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text=orientation, xl=orientation_xl, beep=BeepLevel.BUTTON, duration=0))

        if self.dgt_clock_menu == Menu.LEVEL_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.BUTTON, duration=0))
            elif self.engine_has_levels:
                self.engine_level_menu = ((self.engine_level_menu-1) % self.n_levels)
                level = str(self.engine_level_menu)
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="level " + level, xl="lvl " + level, beep=BeepLevel.BUTTON, duration=0))
            else:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="no level", xl="no lvl", beep=BeepLevel.YES, duration=0))

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text=self.ip, xl=None, beep=BeepLevel.BUTTON, duration=0))

        if self.dgt_clock_menu == Menu.ENGINE_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            elif self.installed_engines:
                self.engine_menu_index = ((self.engine_menu_index-1) % self.n_engines)
                msg = (self.installed_engines[self.engine_menu_index])[1]
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=msg, xl=msg[:6], beep=BeepLevel.BUTTON, duration=0))
            else:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text='error', xl=None, beep=BeepLevel.YES, duration=0))

        if self.dgt_clock_menu == Menu.BOOK_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            else:
                self.book_menu_index = ((self.book_menu_index-1) % self.n_books)
                msg = (self.all_books[self.book_menu_index])[0]
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=msg, xl=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        if self.dgt_clock_menu == Menu.TIME_MENU:
            self.time_control_menu_index -= 1
            if self.time_control_menu_index < 0:
                self.time_control_menu_index = len(self.time_control_fen_map) - 1
            msg = dgt_xl_time_control_list[list(time_control_map.keys()).index(self.time_control_fen_map[self.time_control_menu_index])]
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text=msg, xl=msg, beep=BeepLevel.BUTTON, duration=0))

    def process_button2(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            if self.mode == Mode.GAME:
                if self.alternative:
                    self.fire(Event.ALTERNATIVE_MOVE())
                else:
                    self.fire(Event.STARTSTOP_THINK())
            if self.mode == Mode.REMOTE:
                self.fire(Event.STARTSTOP_THINK())
            if self.mode == Mode.OBSERVE:
                self.fire(Event.STARTSTOP_CLOCK())
            if self.mode == Mode.ANALYSIS or self.mode == Mode.KIBITZ:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="error", xl=None, beep=BeepLevel.YES, duration=0))

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text="scan", xl=None, beep=BeepLevel.BUTTON, duration=0))
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
                self.fire(Event.SETUP_POSITION(fen=bit_board.fen(), uci960=self.setup_uci960))
            else:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="bad pos", xl="badpos", beep=BeepLevel.YES, duration=0))

        if self.dgt_clock_menu == Menu.LEVEL_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            elif self.engine_has_levels:
                if self.engine_level != self.engine_level_menu:
                    self.fire(Event.LEVEL(level=self.engine_level_menu, beep=BeepLevel.BUTTON))
                    DgtDisplay.show(Dgt.DISPLAY_TEXT(text="ok level", xl="ok lvl", beep=BeepLevel.BUTTON, duration=0))
            else:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="no level", xl="no lvl", beep=BeepLevel.YES, duration=0))

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text="pwroff ?", xl="-off-", beep=BeepLevel.YES, duration=0))
            self.awaiting_confirm = PowerMenu.CONFIRM_PWR

        if self.dgt_clock_menu == Menu.ENGINE_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            elif self.installed_engines:
                # Reset level selections
                self.engine_level_menu = self.engine_level
                self.engine_has_levels = False
                # This is a handshake change so index values changed and sync'd in the response below
                self.fire(Event.NEW_ENGINE(eng=self.installed_engines[self.engine_menu_index]))
                self.engine_restart = True
            else:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text='error', xl=None, beep=BeepLevel.YES, duration=0))

        if self.dgt_clock_menu == Menu.BOOK_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            elif self.book_index != self.book_menu_index:
                self.fire(Event.SET_OPENING_BOOK(book=self.all_books[self.book_menu_index], book_control_string='ok book', beep=BeepLevel.BUTTON))

        if self.dgt_clock_menu == Menu.TIME_MENU: 
            if self.time_control_index != self.time_control_menu_index:
                self.time_control_index = self.time_control_menu_index
                self.time_control_fen = self.time_control_fen_map[self.time_control_index]
                self.fire(Event.SET_TIME_CONTROL(time_control=time_control_map[self.time_control_fen], time_control_string='ok time', beep=BeepLevel.BUTTON))

    def process_button3(self):
        if self.dgt_clock_menu == Menu.GAME_MENU:
            mode_list = list(iter(Mode))
            self.mode_index += 1
            if self.mode_index >= len(mode_list):
                self.mode_index = 0
            mode_new = mode_list[self.mode_index]
            self.fire(Event.SET_INTERACTION_MODE(mode=mode_new, beep=BeepLevel.BUTTON))

        if self.dgt_clock_menu == Menu.SETUP_POSITION_MENU:
            self.setup_uci960 = not self.setup_uci960
            text = '960 yes' if self.setup_uci960 else '960 no'
            text_xl = '960yes' if self.setup_uci960 else '960 no'
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text=text, xl=text_xl, beep=BeepLevel.BUTTON, duration=0))

        if self.dgt_clock_menu == Menu.LEVEL_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            elif self.engine_has_levels:
                self.engine_level_menu = ((self.engine_level_menu+1) % self.n_levels)
                level = str(self.engine_level_menu)
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="level " + level, xl="lvl " + level, beep=BeepLevel.BUTTON, duration=0))
            else:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="no level", xl="no lvl", beep=BeepLevel.YES, duration=0))

        if self.dgt_clock_menu == Menu.SETTINGS_MENU:
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text="reboot ?", xl="-boot-", beep=BeepLevel.BUTTON, duration=0))
            self.awaiting_confirm = PowerMenu.CONFIRM_RBT

        if self.dgt_clock_menu == Menu.ENGINE_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            elif self.installed_engines:
                self.engine_menu_index = ((self.engine_menu_index+1) % self.n_engines)
                msg = (self.installed_engines[self.engine_menu_index])[1]
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=msg, xl=msg[:6], beep=BeepLevel.BUTTON, duration=0))
            else:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text='error', xl=None, beep=BeepLevel.YES, duration=0))

        if self.dgt_clock_menu == Menu.BOOK_MENU:
            if self.mode == Mode.REMOTE:
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=Mode.REMOTE.value, xl=None, beep=BeepLevel.YES, duration=0))
            else:
                self.book_menu_index = ((self.book_menu_index+1) % self.n_books)
                msg = (self.all_books[self.book_menu_index])[0]
                DgtDisplay.show(Dgt.DISPLAY_TEXT(text=msg, xl=msg[:6], beep=BeepLevel.BUTTON, duration=0))

        if self.dgt_clock_menu == Menu.TIME_MENU:
            self.time_control_menu_index += 1
            if self.time_control_menu_index >= len(self.time_control_fen_map):
                self.time_control_menu_index = 0
            msg = dgt_xl_time_control_list[list(time_control_map.keys()).index(self.time_control_fen_map[self.time_control_menu_index])]
            DgtDisplay.show(Dgt.DISPLAY_TEXT(text=msg, xl=None, beep=BeepLevel.BUTTON, duration=0))

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
        DgtDisplay.show(Dgt.DISPLAY_TEXT(text=msg, xl=msg[:6], beep=BeepLevel.BUTTON, duration=0))
        # Reset time control fen to match current time control
        self.time_control_mode = time_control_map[self.time_control_fen].mode
        self.time_control_selected_index = 0
        # Reset menu selections
        self.book_menu_index = self.book_index
        self.engine_menu_index = self.engine_index

    def drawresign(self):
        rnk_8, rnk_7, rnk_6, rnk_5, rnk_4, rnk_3, rnk_2, rnk_1 = self.dgt_fen.split("/")
        self.drawresign_fen = "8/8/8/" + rnk_5 + "/" + rnk_4 + "/8/8/8"
        #self.show_pifi(rnk_5 + "  " + rnk_4)
    def run(self):
        while True:
            # Check if we have something to display
            try:
                message = self.message_queue.get()
                if type(message).__name__ == 'Message':
                    logging.debug("Read message from queue: %s", message)
                for case in switch(message):
                    if case(MessageApi.ENGINE_READY):
                        self.engine_index = self.installed_engines.index(message.eng)
                        self.engine_menu_index = self.engine_index
                        self.engine_has_levels = message.has_levels
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text='ok engin', xl="ok eng", beep=BeepLevel.BUTTON, duration=1))
                        self.engine_restart = False
                        break
                    if case(MessageApi.ENGINE_STARTUP):
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
                    if case(MessageApi.ENGINE_FAIL):
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text='error', xl=None, beep=BeepLevel.YES, duration=1))
                        self.show_pifi("Error : Engine Faild")
                        break
                    if case(MessageApi.COMPUTER_MOVE):
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
                        DgtDisplay.show(Dgt.DISPLAY_MOVE(move=move, fen=message.fen, beep=BeepLevel.CONFIG, duration=0))
                        DgtDisplay.show(Dgt.LIGHT_SQUARES(squares=(uci_move[0:2], uci_move[2:4])))
                        self.show_pifi("Com : "+ uci_move[0:2] + "-" + uci_move[2:4])
                        self.side = 0x0
                        #self.show_pifi("Com : "+ uci_move[0:2] + "-" + uci_move[2:4], "" if str(ponder) is None else " => " + str(ponder))
                        break
                    if case(MessageApi.START_NEW_GAME):
                        DgtDisplay.show(Dgt.LIGHT_CLEAR())
                        self.last_move = chess.Move.null()
                        self.reset_hint_and_score()
                        self.mode = Mode.GAME
                        self.dgt_clock_menu = Menu.GAME_MENU
                        self.alternative = False
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text="new game", xl="newgam", beep=BeepLevel.CONFIG, duration=1))
                        self.show_pifi("New Game")
                        self.side = 0x0
                        break
                    if case(MessageApi.WAIT_STATE):
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text="you move", xl="youmov", beep=BeepLevel.OKAY, duration=0))
                        self.show_pifi("you move")
                        self.side = 0x0
                        break
                    if case(MessageApi.COMPUTER_MOVE_DONE_ON_BOARD):
                        DgtDisplay.show(Dgt.LIGHT_CLEAR())
                        self.display_move = False
                        self.alternative = False
                        if self.ok_moves_messages:
                            DgtDisplay.show(Dgt.DISPLAY_TEXT(text="ok pico", xl="okpico", beep=BeepLevel.OKAY, duration=0.5))
                            self.show_pifi("you move")
                            self.side= 0x2
                        break
                    if case(MessageApi.USER_MOVE):
                        self.display_move = False
                        self.alternative = False
                        if self.ok_moves_messages:
                            DgtDisplay.show(Dgt.DISPLAY_TEXT(text="ok user", xl="okuser", beep=BeepLevel.OKAY, duration=0.5))
                            self.show_pifi("OK")
                            self.side = 0x1
                        break
                    if case(MessageApi.REVIEW_MODE_MOVE):
                        self.last_move = message.move
                        self.last_fen = message.fen
                        self.display_move = False
                        if self.ok_moves_messages:
                            DgtDisplay.show(Dgt.DISPLAY_TEXT(text="ok move", xl="okmove", beep=BeepLevel.OKAY, duration=0.5))
                        break
                    if case(MessageApi.ALTERNATIVE_MOVE):
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text="alt move", xl="altmov", beep=BeepLevel.BUTTON, duration=0.5))
                        break
                    if case(MessageApi.LEVEL):
                        level = str(message.level)
                        if self.engine_restart:
                            pass
                        elif self.engine_level != self.engine_level_menu:
                            self.engine_level = self.engine_level_menu
                        else:
                            DgtDisplay.show(Dgt.DISPLAY_TEXT(text="level " + level, xl="lvl " + level,
                                            beep=message.beep, duration=1))
                            self.show_pifi("Level : " + str(level))
                        break
                    if case(MessageApi.TIME_CONTROL):
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text=message.time_control_string, xl=None, beep=message.beep, duration=1))
                        self.show_pifi(message.time_control_string)
                        break
                    if case(MessageApi.OPENING_BOOK):
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text=message.book_control_string, xl=None, beep=message.beep, duration=1))
                        self.show_pifi(message.book_control_string)
                        break
                    if case(MessageApi.USER_TAKE_BACK):
                        self.reset_hint_and_score()
                        self.alternative = False
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text="takeback", xl="takbak", beep=BeepLevel.CONFIG, duration=0))
                        self.show_pifi("takeback")
                        break
                    if case(MessageApi.GAME_ENDS):
                        ge = message.result.value
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text=ge, xl=None, beep=BeepLevel.CONFIG, duration=1))
                        self.show_pifi("check mate")
                        break
                    if case(MessageApi.INTERACTION_MODE):
                        self.mode = message.mode
                        self.alternative = False
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text=message.mode.value, xl=None, beep=message.beep, duration=1))
                        self.show_pifi(None,"=>"+str(message.mode.value))
                        break
                    if case(MessageApi.PLAY_MODE):
                        pm = message.play_mode.value
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text=pm, xl=pm[:6], beep=BeepLevel.BUTTON, duration=1))
                        self.show_pifi(None,"=>"+str(xl=pm[:6]))
                        break
                    if case(MessageApi.NEW_SCORE):
                        self.score = message.score
                        self.mate = message.mate
                        if message.mode == Mode.KIBITZ:
                            DgtDisplay.show(Dgt.DISPLAY_TEXT(text=str(self.score).rjust(6), xl=None,
                                            beep=BeepLevel.NO, duration=1))
                            # thinking 
                            self.show_pifi(str(self.score).rjust(6),None, 1)
                        else:
                            # thinking
                            self.show_pifi("thinking")
                            self.thinkerboll = 0 if self.thinkerboll is 2 else self.thinkerboll + 1
                        break
                    if case(MessageApi.BOOK_MOVE):
                        self.score = None
                        self.mate = None
                        self.display_move = False
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text="book", xl=None, beep=BeepLevel.NO, duration=1))
                        self.show_pifi("book")
                        break
                    if case(MessageApi.NEW_PV):
                        self.hint_move = message.pv[0]
                        self.hint_fen = message.fen
                        if message.mode == Mode.ANALYSIS:
                            DgtDisplay.show(Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen,
                                            beep=BeepLevel.NO, duration=0))
                        self.show_pifi(None,"=>"+ str(self.hint_move) + " => " + str(self.hint_fen))
                        break
                    if case(MessageApi.SYSTEM_INFO):
                        self.ip = ' '.join(message.info["ip"].split('.')[2:])
                        #self.show_pifi('ip : ' + str(self.ip))
                        break
                    if case(MessageApi.STARTUP_INFO):
                        self.book_index = message.info["book_index"]
                        self.book_menu_index = self.book_index
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
                        if tc.mode == ClockMode.FIXED_TIME:
                            time_left = time_right = tc.seconds_per_move
                        if self.flip_board:
                            time_left, time_right = time_right, time_left
                        DgtDisplay.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=side))
                        self.side = side
                        self.pifi_lefttime = time_left
                        self.pifi_righttime = time_right
                        break
                    if case(MessageApi.STOP_CLOCK):
                        DgtDisplay.show(Dgt.CLOCK_STOP())
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
                            self.show_pifi('flipping the board')
                            # Flip the board
                            self.flip_board = not self.flip_board
                            # set standard for setup orientation too
                            self.setup_reverse_orientation = self.flip_board
                            fen = fen[::-1]
                        logging.debug("DGT-Fen: " + fen)
                        #self.show_pifi(fen)
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
                            self.show_pifi('Level : ' , str(level))
                            self.fire(Event.LEVEL(level=level, beep=BeepLevel.MAP))
                        elif fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR":  # New game
                            logging.debug("Map-Fen: New game")
                            self.show_pifi("New Game")
                            self.draw_setup_pieces = False
                            self.fire(Event.NEW_GAME())
                        elif fen in book_map:  # Choose opening book
                            self.book_index = book_map.index(fen)
                            b = self.all_books[self.book_index]
                            logging.debug("Map-Fen: Opening book [%s]", b[1])
                            self.show_pifi('Opening book ', str(b[1])[str(b[1]).find('/')+1:] )
                            self.fire(Event.SET_OPENING_BOOK(book=b, book_control_string=b[0], beep=BeepLevel.MAP))
                        elif fen in mode_map:  # Set interaction mode
                            logging.debug("Map-Fen: Interaction mode [%s]", mode_map[fen])
                            self.show_pifi("Interaction mode " , str(mode_map[fen]))
                            self.fire(Event.SET_INTERACTION_MODE(mode=mode_map[fen], beep=BeepLevel.MAP))
                        elif fen in time_control_map:
                            logging.debug("Map-Fen: Time control [%s]", time_control_map[fen].mode)
                            self.show_pifi("Time control " , dgt_xl_time_control_list[ list(time_control_map.keys()).index(fen)] )
                            self.fire(Event.SET_TIME_CONTROL(time_control=time_control_map[fen],
                                      time_control_string=dgt_xl_time_control_list[
                                          list(time_control_map.keys()).index(fen)], beep=BeepLevel.MAP))
                            self.time_control_mode = time_control_map[fen].mode
                            self.time_control_fen = fen
                        
                            self.pifi_lefttime = int(time_control_map[fen].clock_time[chess.WHITE])
                            self.pifi_righttime = time_right = int(time_control_map[fen].clock_time[chess.BLACK])
                        elif fen in shutdown_map:
                            logging.debug("Map-Fen: shutdown")
                            self.show_pifi("shutdown")
                            self.power_off()
                        elif self.drawresign_fen in drawresign_map:
                            logging.debug("Map-Fen: drawresign")
                            self.show_pifi("drawresign")
                            self.fire(Event.DRAWRESIGN(result=drawresign_map[self.drawresign_fen]))
                        else:
                            if self.draw_setup_pieces:
                                DgtDisplay.show(Dgt.DISPLAY_TEXT(text="set pieces", xl="setup", beep=BeepLevel.NO, duration=0))
                                self.show_pifi("set pieces")
                                self.side = 0x0
                                self.draw_setup_pieces = False
                            self.fire(Event.FEN(fen=fen))
                        break
                    if case(MessageApi.DGT_CLOCK_VERSION):
                        DgtDisplay.show(Dgt.CLOCK_VERSION(main_version=message.main_version,
                                        sub_version=message.sub_version, attached=message.attached))
                        break
                    if case(MessageApi.DGT_CLOCK_TIME):
                        DgtDisplay.show(Dgt.CLOCK_TIME(time_left=message.time_left, time_right=message.time_right))
                        break
                    if case(MessageApi.JACK_CONNECTED_ERROR):  # this will only work in case of 2 clocks connected!
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text="err jack", xl="jack", beep=BeepLevel.YES, duration=0))
                        break
                    if case(MessageApi.NO_EBOARD_ERROR):
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text=message.text, xl=message.text_xl, beep=BeepLevel.NO, duration=0))
                        self.show_pifi("NO EBoard")
                        break
                    if case(MessageApi.EBOARD_VERSION):
                        DgtDisplay.show(Dgt.DISPLAY_TEXT(text=message.text, xl=message.text_xl, beep=BeepLevel.NO, duration=0.5))
                        #self.show_pifi("EBoard Version", message.text)
                    if case():  # Default
                        # print(message)
                        pass
            except queue.Empty:
                pass
