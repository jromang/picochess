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

from timecontrol import *
import math

from dgtiface import *
from engine import get_installed_engines
import threading
from configobj import ConfigObj


class DgtDisplay(Observable, DisplayMsg, threading.Thread):
    def __init__(self, disable_ok_message, ponder_time, dgttranslate, dgtmenu, time_control):
        super(DgtDisplay, self).__init__()
        self.show_ok_message = not disable_ok_message
        self.ponder_time = ponder_time
        self.dgttranslate = dgttranslate
        self.dgtmenu = dgtmenu
        self.time_control = time_control

        self.flip_board = False
        self.dgt_fen = '8/8/8/8/8/8/8/8'
        self.engine_finished = False
        self.ip = None
        self.drawresign_fen = None
        self.show_setup_pieces_msg = True
        self.show_move_or_value = 0
        self.leds_are_on = False

        self.engine_restart = False
        self._reset_moves_and_score()

    def _reset_menu_results(self):
        # dont override "menu_mode_result", otherwise wQ a5-f5 wont work anymore (=> if's)
        pass
        # self.menu_time_mode_result = None
        # self.menu_setup_whitetomove_result = None
        # self.menu_setup_reverse_result = None
        # self.menu_setup_uci960_result = None
        # self.menu_top_result = None
        # self.menu_system_result = None
        # self.menu_engine_name_result = None
        # self.menu_system_sound_beep_result = None
        # self.menu_system_language_lang_result = None
        # self.menu_system_voice_type_result = None
        # self.menu_system_voice_mute_result = None
        # self.menu_system_voice_lang_result = None
        # self.menu_system_voice_speak_result = None
        # self.menu_system_display_pondertime_result = None
        # self.menu_system_display_okmessage_result = None
        # self.menu_inside_flag = False

    def _power_off(self, dev='web'):
        DisplayDgt.show(self.dgttranslate.text('Y10_goodbye'))
        self.engine_restart = True
        self.fire(Event.SHUTDOWN(dev=dev))

    def _reboot(self, dev='web'):
        DisplayDgt.show(self.dgttranslate.text('Y10_pleasewait'))
        self.engine_restart = True
        self.fire(Event.REBOOT(dev=dev))

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
            score.rd = ClockIcons.DOT
        except ValueError:
            pass
        return score

    def hint_side(self):
        side = ClockSide.LEFT if (self.hint_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
        return side

    def inside_menu(self):
        return self.dgtmenu.inside_menu()

    def _process_button0(self, dev):
        logging.debug('({}) clock: handle button 0 press'.format(dev))
        if self.inside_menu():
            text = self.dgtmenu.up()  # button0 can exit the menu, so check
            if text:
                DisplayDgt.show(text)
            else:
                self.exit_display()
        else:
            if self.last_move:
                side = ClockSide.LEFT if (self.last_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                text = Dgt.DISPLAY_MOVE(move=self.last_move, fen=self.last_fen, side=side, wait=False, maxtime=1,
                                        beep=self.dgttranslate.bl(BeepLevel.BUTTON), devs={'ser', 'i2c', 'web'})
            else:
                text = self.dgttranslate.text('B10_nomove')
            DisplayDgt.show(text)
            self.exit_display(wait=True)

    def _process_button1(self, dev):
        logging.debug('({}) clock: handle button 1 press'.format(dev))
        if self.inside_menu():
            DisplayDgt.show(self.dgtmenu.left())  # button1 cant exit the menu
        else:
            text = self._combine_depth_and_score()
            text.beep = self.dgttranslate.bl(BeepLevel.BUTTON)
            # text.maxtime = 0
            DisplayDgt.show(text)
            self.exit_display(wait=True)

    def _process_button2(self, dev):
        logging.debug('({}) clock: handle button 2 press'.format(dev))
        if self.inside_menu():
            pass  # button2 doesnt have any function in menu
        else:
            if self.engine_finished:
                # @todo Protect against multi entrance of Alt-move
                self.engine_finished = False  # This is not 100% ok, but for the moment better as nothing
                self.fire(Event.ALTERNATIVE_MOVE())
            else:
                if self.dgtmenu.menu_mode_result in (Mode.ANALYSIS, Mode.KIBITZ, Mode.PONDER):
                    text = self.dgttranslate.text('B00_nofunction')
                    DisplayDgt.show(text)
                else:
                    self.fire(Event.PAUSE_RESUME())

    def _process_button3(self, dev):
        logging.debug('({}) clock: handle button 3 press'.format(dev))
        if self.inside_menu():
            DisplayDgt.show(self.dgtmenu.right())  # button3 cant exit the menu
        else:
            if self.hint_move:
                side = self.hint_side()
                text = Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen, side=side, wait=False, maxtime=1,
                                        beep=self.dgttranslate.bl(BeepLevel.BUTTON), devs={'ser', 'i2c', 'web'})
            else:
                text = self.dgttranslate.text('B10_nomove')
            DisplayDgt.show(text)
            self.exit_display(wait=True)

    def _process_button4(self, dev):
        logging.debug('({}) clock: handle button 4 press'.format(dev))
        text = self.dgtmenu.down()
        if text:
            DisplayDgt.show(text)
        else:
            pass
        # if self.inside_menu():
        #     DisplayDgt.show(self.dgtmenu.down())
        # else:
        #     self.menu_inside_flag = True
        #     text = self.dgttranslate.text(self.dgtmenu.menu_top_index.value)
        #     DisplayDgt.show(text)

    def _process_lever(self, right_side_down, dev):
        logging.debug('({}) clock: handle lever press - right_side_down: {}'.format(dev, right_side_down))
        if not self.inside_menu():
            self.play_move = chess.Move.null()
            self.play_fen = None
            self.play_turn = None
            self.fire(Event.SWITCH_SIDES(engine_finished=self.engine_finished))

    def _drawresign(self):
        _, _, _, rnk_5, rnk_4, _, _, _ = self.dgt_fen.split('/')
        return '8/8/8/' + rnk_5 + '/' + rnk_4 + '/8/8/8'

    def exit_display(self, wait=False, force=True):
        if self.play_move and self.dgtmenu.menu_mode_result in (Mode.NORMAL, Mode.REMOTE):
            side = ClockSide.LEFT if (self.play_turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
            text = Dgt.DISPLAY_MOVE(move=self.play_move, fen=self.play_fen, side=side, wait=wait, maxtime=1,
                                    beep=self.dgttranslate.bl(BeepLevel.BUTTON), devs={'ser', 'i2c', 'web'})
        else:
            text = Dgt.DISPLAY_TIME(force=force, wait=True, devs={'ser', 'i2c', 'web'})
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
                self.menu_engine_name_index = self.installed_engines.index(message.eng)
                self.engine_has_960 = message.has_960
                if self.show_ok_message or not message.ok_text:
                    DisplayDgt.show(message.eng_text)
                self.engine_restart = False
                self.exit_display(force=True)
                break
            if case(MessageApi.ENGINE_STARTUP):
                self.installed_engines = get_installed_engines(message.shell, message.file)
                for index in range(0, len(self.installed_engines)):
                    eng = self.installed_engines[index]
                    if eng['file'] == message.file:
                        self.menu_engine_name_index = index
                        self.engine_has_960 = message.has_960
                        self.engine_level_index = message.level_index
                break
            if case(MessageApi.ENGINE_FAIL):
                DisplayDgt.show(self.dgttranslate.text('Y00_erroreng'))
                break
            if case(MessageApi.COMPUTER_MOVE):
                if self.leds_are_on:  # can happen in case of a book move
                    logging.warning('REV2 lights still on')
                    DisplayDgt.show(Dgt.LIGHT_CLEAR())
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
                disp = Dgt.DISPLAY_MOVE(move=move, fen=message.fen, side=side, wait=message.wait, maxtime=0,
                                        beep=self.dgttranslate.bl(BeepLevel.CONFIG), devs={'ser', 'i2c', 'web'})
                DisplayDgt.show(disp)
                DisplayDgt.show(Dgt.LIGHT_SQUARES(uci_move=move.uci()))
                self.leds_are_on = True
                break
            if case(MessageApi.START_NEW_GAME):
                if self.leds_are_on:
                    DisplayDgt.show(Dgt.LIGHT_CLEAR())
                    self.leds_are_on = False
                self._reset_moves_and_score()
                # self.mode_index = Mode.NORMAL  # @todo
                self._reset_menu_results()
                self.engine_finished = False
                self.show_setup_pieces_msg = False
                if message.newgame:
                    pos960 = message.game.chess960_pos()
                    game_text = 'C10_newgame' if pos960 is None or pos960 == 518 else 'C10_ucigame'
                    DisplayDgt.show(self.dgttranslate.text(game_text, str(pos960)))
                if self.dgtmenu.menu_mode_result in (Mode.NORMAL, Mode.OBSERVE, Mode.REMOTE):
                    time_left, time_right = message.time_control.current_clock_time(flip_board=self.flip_board)
                    DisplayDgt.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=ClockSide.NONE,
                                                    wait=True, devs={'ser', 'i2c', 'web'}))
                break
            if case(MessageApi.COMPUTER_MOVE_DONE_ON_BOARD):
                if self.leds_are_on:
                    DisplayDgt.show(Dgt.LIGHT_CLEAR())
                    self.leds_are_on = False
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
                if self.leds_are_on:  # can happen in case of a sliding move
                    logging.warning('REV2 lights still on')
                    DisplayDgt.show(Dgt.LIGHT_CLEAR())
                    self.leds_are_on = False
                self.last_move = message.move
                self.last_fen = message.fen
                self.last_turn = message.turn
                self.engine_finished = False
                if self.show_ok_message:
                    DisplayDgt.show(self.dgttranslate.text('K05_okuser'))
                break
            if case(MessageApi.REVIEW_MOVE):
                if self.leds_are_on:  # can happen in case of a sliding move
                    logging.warning('REV2 lights still on')
                    DisplayDgt.show(Dgt.LIGHT_CLEAR())
                    self.leds_are_on = False
                self.last_move = message.move
                self.last_fen = message.fen
                self.last_turn = message.turn
                if self.show_ok_message:
                    DisplayDgt.show(self.dgttranslate.text('K05_okmove'))
                break
            if case(MessageApi.ALTERNATIVE_MOVE):
                if self.leds_are_on:
                    DisplayDgt.show(Dgt.LIGHT_CLEAR())
                    self.leds_are_on = False
                DisplayDgt.show(self.dgttranslate.text('B05_altmove'))
                break
            if case(MessageApi.LEVEL):
                if self.engine_restart:
                    pass
                else:
                    DisplayDgt.show(message.level_text)
                    # self._exit_display(force=False)
                    self.exit_display(force=True)
                break
            if case(MessageApi.TIME_CONTROL):
                if self.show_ok_message or not message.ok_text:
                    DisplayDgt.show(message.time_text)
                tc = self.time_control = message.time_control
                time_left, time_right = tc.current_clock_time(flip_board=self.flip_board)
                DisplayDgt.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=ClockSide.NONE,
                                                wait=True, devs={'ser', 'i2c', 'web'}))
                self.exit_display(force=True)
                break
            if case(MessageApi.OPENING_BOOK):
                if self.show_ok_message or not message.ok_text:
                    DisplayDgt.show(message.book_text)
                self.exit_display(force=True)
                break
            if case(MessageApi.TAKE_BACK):
                if self.leds_are_on:
                    DisplayDgt.show(Dgt.LIGHT_CLEAR())
                    self.leds_are_on = False
                self._reset_moves_and_score()
                self.engine_finished = False
                DisplayDgt.show(self.dgttranslate.text('C00_takeback'))
                break
            if case(MessageApi.GAME_ENDS):
                if not self.engine_restart:  # filter out the shutdown/reboot process
                    ge = message.result.value
                    text = self.dgttranslate.text(ge)
                    text.beep = self.dgttranslate.bl(BeepLevel.CONFIG)
                    text.maxtime = 0.5
                    DisplayDgt.show(text)
                    # self.show_setup_pieces_msg = True @todo Does that work?
                break
            if case(MessageApi.INTERACTION_MODE):
                self.menu_mode_index = message.mode
                self.dgtmenu.menu_mode_result = message.mode  # needed, otherwise Q-placing wont work correctly
                self.engine_finished = False
                if self.show_ok_message or not message.ok_text:
                    DisplayDgt.show(message.mode_text)
                self.exit_display(force=True)
                break
            if case(MessageApi.PLAY_MODE):
                DisplayDgt.show(message.play_mode_text)
                break
            if case(MessageApi.NEW_SCORE):
                if message.mate is None:
                    score = int(message.score)
                    if message.turn == chess.BLACK:
                        score *= -1
                    text = self.dgttranslate.text('N10_score', score)
                else:
                    text = self.dgttranslate.text('N10_mate', str(message.mate))
                self.score = text
                if message.mode == Mode.KIBITZ and not self.inside_menu():
                    DisplayDgt.show(self._combine_depth_and_score())
                break
            if case(MessageApi.BOOK_MOVE):
                self.score = self.dgttranslate.text('N10_score', None)
                DisplayDgt.show(self.dgttranslate.text('N10_bookmove'))
                break
            if case(MessageApi.NEW_PV):
                self.hint_move = message.pv[0]
                self.hint_fen = message.game.fen()
                self.hint_turn = message.game.turn
                if message.mode == Mode.ANALYSIS and not self.inside_menu():
                    side = self.hint_side()
                    disp = Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen, side=side, wait=True, maxtime=0,
                                            beep=self.dgttranslate.bl(BeepLevel.NO), devs={'ser', 'i2c', 'web'})
                    DisplayDgt.show(disp)
                break
            if case(MessageApi.NEW_DEPTH):
                self.depth = message.depth
                break
            if case(MessageApi.IP_INFO):
                self.ip = message.info['int_ip']
                break
            if case(MessageApi.STARTUP_INFO):
                self.menu_mode_index = message.info['interaction_mode']
                self.dgtmenu.menu_mode_result = message.info['interaction_mode']
                self.dgtmenu.menu_book_index = message.info['book_index']
                self.all_books = message.info['books']
                tc = self.time_control = message.info['time_control']
                self.dgtmenu.menu_time_mode_index = tc.mode
                # try to find the index from the given time_control (tc)
                # if user gave a non-existent tc value stay at standard
                index = 0
                if tc.mode == TimeMode.FIXED:
                    for val in self.dgtmenu.tc_fixed_map.values():
                        if val == tc:
                            self.tc_fixed_index = index
                            break
                        index += 1
                elif tc.mode == TimeMode.BLITZ:
                    for val in self.dgtmenu.tc_blitz_map.values():
                        if val == tc:
                            self.tc_blitz_index = index
                            break
                        index += 1
                elif tc.mode == TimeMode.FISCHER:
                    for val in self.dgtmenu.tc_fisch_map.values():
                        if val == tc:
                            self.tc_fisch_index = index
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
                tc = self.time_control = message.time_control
                if tc.mode == TimeMode.FIXED:
                    time_left = time_right = tc.seconds_per_move
                else:
                    time_left, time_right = tc.current_clock_time(flip_board=self.flip_board)
                    if time_left < 0:
                        time_left = 0
                    if time_right < 0:
                        time_right = 0
                side = ClockSide.LEFT if (message.turn == chess.WHITE) != self.flip_board else ClockSide.RIGHT
                DisplayDgt.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=side,
                                                wait=False, devs=message.devs))
                break
            if case(MessageApi.CLOCK_STOP):
                DisplayDgt.show(Dgt.CLOCK_STOP(devs=message.devs))
                break
            if case(MessageApi.DGT_BUTTON):
                button = int(message.button)
                if not self.engine_restart:
                    if button == 0:
                        self._process_button0(message.dev)
                    elif button == 1:
                        self._process_button1(message.dev)
                    elif button == 2:
                        self._process_button2(message.dev)
                    elif button == 3:
                        self._process_button3(message.dev)
                    elif button == 4:
                        self._process_button4(message.dev)
                    elif button == 0x11:
                        self._power_off(message.dev)
                    elif button == 0x40:
                        self._process_lever(right_side_down=True, dev=message.dev)
                    elif button == -0x40:
                        self._process_lever(right_side_down=False, dev=message.dev)
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
                    self.menu_setup_reverse_index = self.flip_board
                    fen = fen[::-1]
                logging.debug("DGT-Fen [%s]", fen)
                if fen == self.dgt_fen:
                    logging.debug('ignore same fen')
                    break
                self.dgt_fen = fen
                self.drawresign_fen = self._drawresign()
                # Fire the appropriate event
                if fen in level_map:
                    eng = self.installed_engines[self.menu_engine_name_index]
                    level_dict = eng['level_dict']
                    if level_dict:
                        inc = math.ceil(len(level_dict) / 8)
                        self.engine_level_index = min(inc * level_map.index(fen), len(level_dict) - 1)
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
                        self.menu_book_index = book_index
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
                            self.menu_engine_name_index = engine_index
                            eng = self.installed_engines[self.menu_engine_name_index]
                            level_dict = eng['level_dict']
                            logging.debug("Map-Fen: Engine name [%s]", eng['name'])
                            eng_text = eng['text']
                            eng_text.beep = self.dgttranslate.bl(BeepLevel.MAP)
                            eng_text.maxtime = 1
                            if level_dict:
                                if self.engine_level_index is None or len(level_dict) <= self.engine_level_index:
                                    self.engine_level_index = len(level_dict) - 1
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
                elif fen in self.dgtmenu.tc_fixed_map:
                    logging.debug('Map-Fen: Time control fixed')
                    self.menu_time_mode_index = TimeMode.FIXED
                    self.tc_fixed_index = list(self.dgtmenu.tc_fixed_map.keys()).index(fen)
                    text = self.dgttranslate.text('M10_tc_fixed', self.dgtmenu.tc_fixed_list[self.tc_fixed_index])
                    self.fire(Event.SET_TIME_CONTROL(time_control=self.dgtmenu.tc_fixed_map[fen],
                                                     time_text=text, ok_text=False))
                    self._reset_menu_results()
                elif fen in self.dgtmenu.tc_blitz_map:
                    logging.debug('Map-Fen: Time control blitz')
                    self.menu_time_mode_index = TimeMode.BLITZ
                    self.tc_blitz_index = list(self.dgtmenu.tc_blitz_map.keys()).index(fen)
                    text = self.dgttranslate.text('M10_tc_blitz', self.dgtmenu.tc_blitz_list[self.tc_blitz_index])
                    self.fire(Event.SET_TIME_CONTROL(time_control=self.dgtmenu.tc_blitz_map[fen],
                                                     time_text=text, ok_text=False))
                    self._reset_menu_results()
                elif fen in self.dgtmenu.tc_fisch_map:
                    logging.debug('Map-Fen: Time control fischer')
                    self.menu_time_mode_index = TimeMode.FISCHER
                    self.tc_fisch_index = list(self.dgtmenu.tc_fisch_map.keys()).index(fen)
                    text = self.dgttranslate.text('M10_tc_fisch', self.dgtmenu.tc_fisch_list[self.tc_fisch_index])
                    self.fire(Event.SET_TIME_CONTROL(time_control=self.dgtmenu.tc_fisch_map[fen],
                                                     time_text=text, ok_text=False))
                    self._reset_menu_results()
                elif fen in shutdown_map:
                    logging.debug('Map-Fen: shutdown')
                    self._power_off()
                elif fen in reboot_map:
                    logging.debug('Map-Fen: reboot')
                    self._reboot()
                elif self.drawresign_fen in drawresign_map:
                    if not self.inside_menu():
                        logging.debug('Map-Fen: drawresign')
                        self.fire(Event.DRAWRESIGN(result=drawresign_map[self.drawresign_fen]))
                elif '/pppppppp/8/8/8/8/PPPPPPPP/' in fen:  # check for the lines 2-7 cause could be an uci960 pos too
                    bit_board = chess.Board(fen + ' w - - 0 1')
                    pos960 = bit_board.chess960_pos(ignore_castling=True)
                    if pos960 is not None:
                        if pos960 == 518 or self.engine_has_960:
                            logging.debug('Map-Fen: New game')
                            self.fire(Event.NEW_GAME(pos960=pos960))
                        else:
                            # self._reset_moves_and_score()
                            DisplayDgt.show(self.dgttranslate.text('Y00_error960'))
                else:
                    if not self.inside_menu():
                        if self.show_setup_pieces_msg:
                            DisplayDgt.show(self.dgttranslate.text('N00_setpieces'))
                        self.fire(Event.FEN(fen=fen))
                    else:
                        # @todo perhaps resent this fen after menu exit?
                        logging.debug('inside the menu. fen "{}" ignored'.format(fen))
                break
            if case(MessageApi.DGT_CLOCK_VERSION):
                if message.dev == 'ser':  # send the "board connected message" to serial clock
                    DisplayDgt.show(message.text)
                time_left, time_right = self.time_control.current_clock_time(flip_board=self.flip_board)
                DisplayDgt.show(Dgt.CLOCK_START(time_left=time_left, time_right=time_right, side=ClockSide.NONE,
                                                wait=True, devs={message.dev}))
                DisplayDgt.show(Dgt.CLOCK_VERSION(main=message.main, sub=message.sub, dev=message.dev))
                break
            if case(MessageApi.DGT_CLOCK_TIME):
                DisplayDgt.show(Dgt.CLOCK_TIME(time_left=message.time_left, time_right=message.time_right, dev=message.dev))
                break
            if case(MessageApi.DGT_SERIAL_NR):
                # logging.debug('Serial number {}'.format(message.number))  # actually used for watchdog (once a second)
                if self.dgtmenu.menu_mode_result == Mode.PONDER and not self.inside_menu():
                    if self.show_move_or_value >= self.ponder_time:
                        if self.hint_move:
                            side = self.hint_side()
                            text = Dgt.DISPLAY_MOVE(move=self.hint_move, fen=self.hint_fen, side=side, wait=True, maxtime=1,
                                                    beep=self.dgttranslate.bl(BeepLevel.NO), devs={'ser', 'i2c', 'web'})
                        else:
                            text = self.dgttranslate.text('N10_nomove')
                    else:
                        text = self._combine_depth_and_score()
                    text.wait = True
                    DisplayDgt.show(text)
                    self.show_move_or_value = (self.show_move_or_value + 1) % (self.ponder_time * 2)
                break
            if case(MessageApi.DGT_JACK_CONNECTED_ERROR):  # this will only work in case of 2 clocks connected!
                DisplayDgt.show(self.dgttranslate.text('Y00_errorjack'))
                break
            if case(MessageApi.DGT_EBOARD_VERSION):
                DisplayDgt.show(message.text)
                DisplayDgt.show(Dgt.DISPLAY_TIME(force=True, wait=True, devs={'i2c'}))
                break
            if case(MessageApi.DGT_NO_EBOARD_ERROR):
                DisplayDgt.show(message.text)
                break
            if case(MessageApi.DGT_NO_CLOCK_ERROR):
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
                if repr(message) != MessageApi.DGT_SERIAL_NR:
                    logging.debug("received message from msg_queue: %s", message)
                self._process_message(message)
            except queue.Empty:
                pass
