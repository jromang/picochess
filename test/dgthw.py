# TEST file for trying to solve the time waiting problem
# (c) 2016 by LocutusOfPenguin - use at your own risk:-)

from dgtiface import *
from utilities import *
from threading import Lock


class DgtHw(DgtIface):
    def __init__(self):
        super(DgtHw, self).__init__()
        self.lock = Lock()

    def display_text_on_clock(self, text, beep=False):
        logging.info(text)
        print(text)

    def display_move_on_clock(self, move, fen, side, beep=False):
        logging.info(move)
        print(move)

    def display_time_on_clock(self, force=False):
        if self.clock_running or force:
            logging.info('clock now displaying time')
        else:
            logging.debug('DGT clock isnt running - no need for endClock')
        print('clock_time')

    def stop_clock(self):
        self.resume_clock(0x04)

    def resume_clock(self, side):
        l_hms = self.time_left
        r_hms = self.time_right
        if l_hms is None or r_hms is None:
            logging.debug('time values not set - abort function')
            return

        lr = rr = 0
        if side == 0x01:
            lr = 1
        if side == 0x02:
            rr = 1
        with self.lock:
            print(lr, l_hms[0], l_hms[1], l_hms[2], rr, r_hms[0], r_hms[1], r_hms[2])
            self.clock_running = (side != 0x04)

    def start_clock(self, time_left, time_right, side):
        self.time_left = hours_minutes_seconds(time_left)
        self.time_right = hours_minutes_seconds(time_right)
        self.resume_clock(side)
