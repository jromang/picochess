import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+os.sep+'..')
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+os.sep+'../libs')
import configargparse
import chess
import chess.polyglot
import dgt
import logging
import uci
import threading
import copy
from utilities import *
from timecontrol import TimeControl
from time import sleep
import unittest
import time

class Timer(object):
   def __init__(self, clock_time):
       self.flag = False
       # self.color = WHITE
       self.clock_time = clock_time
       # self.clock_time = {chess.WHITE: float(minutes_per_game * 60), chess.BLACK: float(minutes_per_game * 60)}  # Player remaining time, in seconds
       self.active_color = None

   def out_of_time(self):
       """Fires an OUT_OF_TIME event"""
       self.flag = True

   def run(self, color):
       self.active_color = color
       self.start_time = time.time()
       self.timer = threading.Timer(self.clock_time[color], self.out_of_time)
       self.timer.start()

   def stop(self):
        """Stop the clocks"""
        if self.active_color is not None:
            self.timer.cancel()
            self.timer.join()
            print("Active color is {0}".format(self.active_color))
            print("Previous time is {0}".format(self.clock_time[self.active_color]))

            self.clock_time[self.active_color] -= time.time() - self.start_time - 1
            print("Current time is {0}".format(self.clock_time[self.active_color]))
            self.active_color = None

        # self.color = BLACK if self.color == WHITE else WHITE

class PicoChessTimeTests(unittest.TestCase):

    def test_out_of_time(self):
        # log = logging.getLogger('')
        # log.setLevel(logging.DEBUG)
        # format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        #
        # ch = logging.StreamHandler(sys.stdout)
        # ch.setFormatter(format)
        # log.addHandler(ch)
        print('In out of time test')
        flag = False
        minutes_per_game = 0.05
        clock_time = {chess.WHITE: float(minutes_per_game * 60), chess.BLACK: float(minutes_per_game * 60)}  # Player remaining time, in seconds

        t = Timer(clock_time)
        color = chess.WHITE

        for i in range(0,10):
            # t = TimeControl(ClockMode.BLITZ, minutes_per_game=5)

            print('Starting clock')
            t.run(color)
            # t.run(0.05)
            print("Clock time is {0}".format(t.clock_time[color]))
            # sleep(t.clock_time[color]/100)
            print("About to sleep for {0} seconds".format(t.clock_time[color]/20))
            sleep(t.clock_time[color]/20)

            print('Stopping clock')
            t.stop()

            if t.flag:
                print("Reached out of time, should not happen")
                # log.ERROR('Reached out of time, should  not happen')
                flag = t.flag
                self.assertFalse(True)
            else:
                print("Not out of time, continuing test")
            print ("Clock map is ")
            print(t.clock_time)
            print("Clock time is {0}".format(t.clock_time[color]))

            t = Timer(t.clock_time)
            color = chess.WHITE if color == chess.BLACK else chess.BLACK


        self.assertTrue(True)

if __name__ == "__main__":
    p = PicoChessTimeTests()
    p.test_out_of_time()

