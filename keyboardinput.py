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

import threading
import chess
import logging
from utilities import *


class KeyboardInput(Observable, threading.Thread):
    def __init__(self):
        super(KeyboardInput, self).__init__()

    def run(self):
        while True:
            cmd = input('PicoChess v'+version+':>')

            try:
                # commands like "mode:analysis" or "mode:remote"
                # "go" or "newgame" or "setup:<legal_fen_string>"
                # "level:<1-20> or "fen:<legal_fen_string>"
                # "print:<legal_fen_string>" or "button:<0-4>"
                # everything else is regarded as a move string
                if cmd.startswith('mode:'):
                    mode = cmd.split(':')[1]
                    if mode.lower() == 'analysis':
                        mode = Mode.ANALYSIS
                    elif mode.lower() == 'remote':
                        mode = Mode.REMOTE
                    logging.warning("Mode: {0}".format(mode))
                    self.fire(Event.SET_MODE, mode=mode)
                else:
                    # this doesn't work see #99
                    # if cmd.startswith('stop'):
                    #    self.fire(Event.STOP_SEARCH)
                    if cmd.startswith('newgame'):
                        self.fire(Event.NEW_GAME)
                    elif cmd.startswith('go'):
                        self.fire(Event.CHANGE_PLAYMODE)
                    elif cmd.startswith('level:'):
                        level = int(cmd.split(':')[1])
                        self.fire(Event.LEVEL, level=level)
                    elif cmd.startswith('fen:'):
                        fen = cmd.split(':')[1]
                        # dgt board only sends the basic fen
                        # be sure, its same no matter what fen the user entered
                        self.fire(Event.FEN, fen=fen.split(' ')[0])
                    elif cmd.startswith('print:'):
                        fen = cmd.split(':')[1]
                        print(chess.Board(fen))
                    elif cmd.startswith('button:'):
                        button = cmd.split(':')[1]
                        self.fire(Event.BUTTON_PRESSED, button=button)
                    elif cmd.startswith('setup:'):
                        fen = cmd.split(':')[1]
                        if chess.Board(fen).is_valid(False):
                            self.fire(Event.SETUP_POSITION, fen=fen)
                        else:
                            raise ValueError(fen)
                    else:
                        move = chess.Move.from_uci(cmd)
                        self.fire(Event.KEYBOARD_MOVE, move=move)
            except ValueError:
                logging.warning('Invalid user input [%s]', cmd)


class TerminalDisplay(Display, threading.Thread):
    def __init__(self):
        super(TerminalDisplay, self).__init__()

    def run(self):
        while True:
            # Check if we have something to display
            message = self.message_queue.get()
            for case in switch(message):
                if case(Message.COMPUTER_MOVE):
                    print('\n' + str(message.game))
                    print(message.game.fen())
                    break
                if case(Message.SEARCH_STARTED):
                    print('Computer is thinking...')
                    break
                if case(Message.SEARCH_STOPPED):
                    print('Computer stopped thinking...')
                    break

                if case(Dgt.DISPLAY_MOVE):
                    print('DGT clock mov:' + str(message.move))
                    break
                if case(Dgt.DISPLAY_TEXT):
                    print('DGT clock txt:' +message.text)
                    break
                if case(Dgt.CLOCK_START):
                    print('DGT clock time started')
                    break
                if case(Dgt.CLOCK_STOP):
                    print('DGT clock time stopped')
                    break
                if case():  # Default
                    pass
