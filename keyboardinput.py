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
                message = self.message_queue.get_nowait()
                if message == Message.BOOK_MOVE:
                    print('Book move')
                elif message == Message.COMPUTER_MOVE:
                    print('\n' + str(message.game))
                    print('Computer move : ' + message.move)
                elif message == Message.START_NEW_GAME:
                    print('New game')
                elif message == Message.SEARCH_STARTED:
                    print('Computer is thinking...')
            except queue.Empty:
                pass