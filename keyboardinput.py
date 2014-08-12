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
                move=chess.Move.from_uci(cmd)
                self.fire(Event.USER_MOVE, move=move)
            except ValueError:
                logging.warning('Invalid user input [%s]', cmd)


class TerminalDisplay(Display, threading.Thread):
    def __init__(self):
        super(TerminalDisplay, self).__init__()

    def run(self):
        while True:
            #Check if we have something to display
            try:
                display_message = self.message_queue.get_nowait()
                if display_message[0] == Message.BOOK_MOVE:
                    print('Book move')
                elif display_message[0] == Message.COMPUTER_MOVE:
                    print('\n' + str(display_message[1][1]))
                    print('Computer move : ' + display_message[1][0])
                elif display_message[0] == Message.START_NEW_GAME:
                    print('New game')
                elif display_message[0] == Message.SEARCH_STARTED:
                    print('Computer is thinking...')
            except queue.Empty:
                pass