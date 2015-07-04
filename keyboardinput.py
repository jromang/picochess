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
                # commands like "go" or "newgame" or "stop"
                # "setup:<legal_fen_string>"
                # "level:<1-20> or "fen:<legal_fen_string>"
                # "print:<legal_fen_string>" or "button:<0-4>"
                # everything else is regarded as a move string
                if cmd.startswith('newgame'):
                    self.fire(Event.NEW_GAME)
                else:
                    # this doesn't work see #99
                    # if cmd.startswith('stop'):
                    #    self.fire(Event.STOP_SEARCH)
                    if cmd.startswith('go'):
                        self.fire(Event.CHANGE_PLAYMODE)
                    elif cmd.startswith('level:'):
                        level = int(cmd.split(':')[1])
                        self.fire(Event.LEVEL, level=level)
                    elif cmd.startswith('print:'):
                        fen = cmd.split(':')[1]
                        print(chess.Board(fen))
                    elif cmd.startswith('setup:'):
                        fen = cmd.split(':')[1]
                        if chess.Board(fen).is_valid(False):
                            self.fire(Event.SETUP_POSITION, fen=fen)
                        else:
                            raise ValueError(fen)
                    # Here starts the simulation of a dgt-board!
                    # Let the user send events like the board would do
                    elif cmd.startswith('fen:'):
                        fen = cmd.split(':')[1]
                        # dgt board only sends the basic fen => be sure
                        # it's same no matter what fen the user entered
                        self.fire(Event.DGT_FEN, fen=fen.split(' ')[0])
                    elif cmd.startswith('button:'):
                        button = cmd.split(':')[1]
                        self.fire(Event.DGT_BUTTON, button=button)
                    # end simulation code
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
                    # emulate the user doing the computer move on vBoard
                    Observable.fire(Event.DGT_FEN, fen=message.game.fen().split(' ')[0])
                    break
                if case(Message.SEARCH_STARTED):
                    print('Computer starts thinking...')
                    break
                if case(Message.SEARCH_STOPPED):
                    print('Computer stopped thinking...')
                    break
                if case(Message.RUN_CLOCK):
                    # print(message.turn, message.time_control)
                    print('run_clock')
                    break
                if case():  # Default
                    pass
