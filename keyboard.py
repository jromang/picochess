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
import time
import logging
from utilities import *

keyboard_last_fen = None


class KeyboardInput(Observable, threading.Thread):
    def __init__(self):
        super(KeyboardInput, self).__init__()

    def run(self):
        logging.info('evt_queue ready')
        print('#' * 42 + ' PicoChess v' + version + ' ' + '#' * 42)
        print('To play a move enter the from-to squares like "e2e4". To play this move on board, enter "go".')
        print('When the computer displays its move, also type "go" to actually do it on the board (see above).')
        print('Other commands are: newgame:<w|b>, print:<fen>, setup:<fen>, fen:<fen>, button:<0-4>, lever:<l|r>')
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
                if cmd.startswith('newgame:'):
                    side = cmd.split(':')[1]
                    if side == 'w':
                        self.fire(Event.DGT_FEN(fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'))
                    elif side == 'b':
                        self.fire(Event.DGT_FEN(fen='RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr'))
                    else:
                        raise ValueError(raw)
                else:
                    if cmd.startswith('print:'):
                        fen = raw.split(':')[1]
                        print(chess.Board(fen))
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
                        if button not in range(5):
                            raise ValueError(button)
                        self.fire(Event.DGT_BUTTON(button=button))
                    elif cmd.startswith('lever:'):
                        lever = cmd.split(':')[1]
                        if lever not in ('l', 'r'):
                            raise ValueError(lever)
                        button = 0x40 if lever == 'r' else -0x40
                        self.fire(Event.DGT_BUTTON(button=button))
                    elif cmd.startswith('go'):
                        if keyboard_last_fen is not None:
                            self.fire(Event.DGT_FEN(fen=keyboard_last_fen.split(' ')[0]))
                        else:
                            print('last move already send to virtual board')
                    # end simulation code
                    else:
                        # move => fen => virtual board sends fen
                        move = chess.Move.from_uci(cmd)
                        self.fire(Event.KEYBOARD_MOVE(move=move))
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
                    print('\n' + str(message.game))
                    print(message.game.fen())
                    keyboard_last_fen = message.game.fen()
                    break
                if case(MessageApi.COMPUTER_MOVE_DONE_ON_BOARD):
                    keyboard_last_fen = None
                    break
                if case(MessageApi.USER_MOVE):
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
                    print(message.fen)
                    keyboard_last_fen = message.fen
                    break
                if case():  # Default
                    pass
