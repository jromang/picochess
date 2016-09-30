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

import threading
import chess
from utilities import *

keyboard_last_fen = None


class KeyboardInput(Observable, threading.Thread):
    def __init__(self, dgttranslate, is_pi):
        super(KeyboardInput, self).__init__()
        self.flip_board = False
        self.board_plugged_in = True
        self.rt = RepeatedTimer(1, self.fire_no_board_connection)
        self.dgttranslate = dgttranslate
        self.is_pi = is_pi

    def fire_no_board_connection(self):
        text = self.dgttranslate.text('N00_noboard', 'Board!')
        DisplayMsg.show(Message.NO_EBOARD_ERROR(text=text))

    def run(self):
        logging.info('evt_queue ready')
        print('#' * 42 + ' PicoChess v' + version + ' ' + '#' * 42)
        print('To play a move enter the from-to squares like "e2e4". To play this move on board, enter "go".')
        print('When the computer displays its move, also type "go" to actually do it on the board (see above).')
        print('Other commands are:')
        print('newgame:<w|b>, print:<fen>, setup:<fen>, fen:<fen>, button:<0-5>, lever:<l|r>, plug:<in|off>')
        print('')
        print('This console mode is mainly for development. Better activate picochess together with a DGT-Board ;-)')
        print('#' * 100)
        print('')
        while True:
            raw = input('PicoChess v'+version+':>').strip()
            if not raw:
                continue
            cmd = raw.lower()

            try:
                if cmd.startswith('print:'):
                    fen = raw.split(':')[1]
                    print(chess.Board(fen))
                else:
                    if not self.board_plugged_in and not cmd.startswith('plug:'):
                        print('The command isnt accepted cause the virtual board is not plugged in')
                        continue
                    if cmd.startswith('newgame:'):
                        side = cmd.split(':')[1]
                        if side == 'w':
                            self.flip_board = False
                            self.fire(Event.DGT_FEN(fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'))
                        elif side == 'b':
                            self.flip_board = True
                            self.fire(Event.DGT_FEN(fen='RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr'))
                        else:
                            raise ValueError(side)
                    elif cmd.startswith('setup:'):
                        fen = raw.split(':')[1]
                        uci960 = False  # make it easy for the moment
                        bit_board = chess.Board(fen, uci960)
                        if bit_board.is_valid():
                            self.fire(Event.SETUP_POSITION(fen=bit_board.fen(), uci960=uci960))
                        else:
                            raise ValueError(fen)
                    # Here starts the simulation of a dgt-board!
                    # Let the user send events like the board would do
                    elif cmd.startswith('fen:'):
                        fen = raw.split(':')[1]
                        # dgt board only sends the basic fen => be sure
                        # it's same no matter what fen the user entered
                        self.fire(Event.DGT_FEN(fen=fen.split(' ')[0]))
                    elif cmd.startswith('button:'):
                        button = int(cmd.split(':')[1])
                        if button not in range(6):
                            raise ValueError(button)
                        if button == 5:  # make it to power button
                            button = 0x11
                        self.fire(Event.DGT_BUTTON(button=button))
                    elif cmd.startswith('lever:'):
                        lever = cmd.split(':')[1]
                        if lever not in ('l', 'r'):
                            raise ValueError(lever)
                        button = 0x40 if lever == 'r' else -0x40
                        self.fire(Event.DGT_BUTTON(button=button))
                    elif cmd.startswith('plug:'):
                        plug = cmd.split(':')[1]
                        if plug not in ('in', 'off'):
                            raise ValueError(plug)
                        if plug == 'in':
                            self.board_plugged_in = True
                            self.rt.stop()
                            text_l, text_m, text_s = 'VirtBoard  ', 'V-Board ', 'vboard'
                            text = Dgt.DISPLAY_TEXT(l=text_l, m=text_m, s=text_s,
                                                    wait=True, beep=False, maxtime=1, devs={'ser', 'i2c', 'web'})
                            DisplayMsg.show(Message.EBOARD_VERSION(text=text, channel='console'))
                        if plug == 'off':
                            self.board_plugged_in = False
                            self.rt.start()
                    elif cmd.startswith('go'):
                        if keyboard_last_fen is not None:
                            self.fire(Event.DGT_FEN(fen=keyboard_last_fen))
                        else:
                            print('last move already send to virtual board')
                    # end simulation code
                    else:
                        # move => fen => virtual board sends fen
                        move = chess.Move.from_uci(cmd)
                        self.fire(Event.KEYBOARD_MOVE(move=move, flip_board=self.flip_board))
            except ValueError as e:
                logging.warning('Invalid user input [%s]', raw)


class TerminalDisplay(DisplayMsg, threading.Thread):
    def __init__(self):
        super(TerminalDisplay, self).__init__()

    def run(self):
        global keyboard_last_fen
        logging.info('msg_queue ready')
        while True:
            # Check if we have something to display
            message = self.msg_queue.get()
            for case in switch(message):
                if case(MessageApi.COMPUTER_MOVE):
                    print('\n' + message.fen)
                    print(message.game)
                    print(message.game.fen() + '\n')
                    keyboard_last_fen = message.game.fen().split(' ')[0]
                    break
                if case(MessageApi.COMPUTER_MOVE_DONE_ON_BOARD):
                    keyboard_last_fen = None
                    break
                if case(MessageApi.USER_MOVE):
                    print('\n' + message.fen)
                    print(message.game)
                    print(message.game.fen() + '\n')
                    keyboard_last_fen = None
                    break
                if case(MessageApi.START_NEW_GAME):
                    keyboard_last_fen = None
                    break
                if case(MessageApi.SEARCH_STARTED):
                    if message.engine_status == EngineStatus.THINK:
                        print('Computer starts thinking')
                    if message.engine_status == EngineStatus.PONDER:
                        print('Computer starts pondering')
                    if message.engine_status == EngineStatus.WAIT:
                        print('Computer starts waiting - hmmm')
                    break
                if case(MessageApi.SEARCH_STOPPED):
                    if message.engine_status == EngineStatus.THINK:
                        print('Computer stops thinking')
                    if message.engine_status == EngineStatus.PONDER:
                        print('Computer stops pondering')
                    if message.engine_status == EngineStatus.WAIT:
                        print('Computer stops waiting - hmmm')
                    break
                if case(MessageApi.KEYBOARD_MOVE):
                    keyboard_last_fen = message.fen
                    break
                if case():  # Default
                    pass
