# TEST file for trying to solve the time waiting problem
# (c) 2016 by LocutusOfPenguin - use at your own risk:-)

from utilities import *
import time
from threading import Timer, Thread, Lock


class DgtIface(DisplayDgt, Thread):
    def __init__(self):
        super(DgtIface, self).__init__()

        self.enable_dgt_3000 = False
        self.enable_dgt_pi = False
        self.clock_found = False
        self.time_left = None
        self.time_right = None

        self.timer = None
        self.timer_running = False
        self.clock_running = False
        self.duration_factor = 3  # This is for testing the duration - remove it lateron!
        # delayed task array
        self.tasks = []
        self.do_process = True
        self.lock = Lock()

    def display_text_on_clock(self, text, beep=False):
        raise NotImplementedError()

    def display_move_on_clock(self, move, fen, side, beep=False):
        raise NotImplementedError()

    def display_time_on_clock(self, force=False):
        raise NotImplementedError()

    def stop_clock(self):
        raise NotImplementedError()

    def resume_clock(self, side):
        raise NotImplementedError()

    def start_clock(self, time_left, time_right, side):
        raise NotImplementedError()

    def stopped_timer(self):
        self.timer_running = False
        self.do_process = True
        if self.clock_running:
            logging.debug('showing the running clock again')
            self.display_time_on_clock(force=False)
        else:
            logging.debug('clock not running - ignored duration')
        logging.debug('tasks in stop: {}'.format(self.tasks))
        if self.tasks:
            message = self.tasks.pop(0)
            self.process_message(message)

    def process_message(self, message):
        with self.lock:
            logging.debug('processing: {}'.format(message))
            for case in switch(message):
                if case(DgtApi.DISPLAY_MOVE):
                    self.display_move_on_clock(message.move, message.fen, message.side, message.beep)
                    break
                if case(DgtApi.DISPLAY_TEXT):
                    text = message.m
                    self.display_text_on_clock(text, message.beep)
                    break
                if case(DgtApi.DISPLAY_TIME):
                    self.display_time_on_clock(message.force)
                    break
                if case(DgtApi.CLOCK_STOP):
                    self.clock_running = False
                    self.stop_clock()
                    Observable.fire(Event.DGT_CLOCK_CALLBACK(callback=message.callback))
                    break
                if case(DgtApi.CLOCK_START):
                    self.clock_running = (message.side != 0x04)
                    # log times
                    l_hms = hours_minutes_seconds(message.time_left)
                    r_hms = hours_minutes_seconds(message.time_right)
                    logging.debug('last time received from clock l:{} r:{}'.format(self.time_left, self.time_right))
                    logging.debug('sending time to clock l:{} r:{}'.format(l_hms, r_hms))

                    self.start_clock(message.time_left, message.time_right, message.side)
                    Observable.fire(Event.DGT_CLOCK_CALLBACK(callback=message.callback))
                    break
                if case():  # Default
                    print(message)
                    pass

    def run(self):
        logging.info('dgt_queue ready')
        while True:
            # Check if we have something to display
            try:
                message = self.dgt_queue.get()
                logging.debug("received command from dgt_queue: %s", message)

                # special code 1
                if hasattr(message, 'duration') and message.duration > 0:
                    if self.timer_running:
                        if hasattr(message, 'wait') and message.wait:
                            logging.debug('waiting for former duration to be over')
                            while self.timer_running:
                                time.sleep(0.1)
                        else:
                            logging.debug('ignore former duration')
                            self.timer.cancel()

                    self.timer = Timer(message.duration * self.duration_factor, self.stopped_timer)
                    self.timer.start()
                    logging.debug('showing {} for {} secs'.format(message, message.duration * self.duration_factor))
                    self.timer_running = True

                # special code 2
                self.do_process = True
                if self.timer_running:
                    if hasattr(message, 'wait'):
                        if message.wait:
                            self.tasks.append(message)
                            logging.debug('tasks delayed: {}'.format(self.tasks))
                            self.do_process = False
                        else:
                            if self.tasks:
                                logging.debug('delete following tasks: {}'.format(self.tasks))
                                self.tasks = []

                # now continue
                if self.do_process:
                    self.process_message(message)
                else:
                    logging.debug('tasks delayed: {}'.format(message))
            except queue.Empty:
                pass
