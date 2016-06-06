# TEST file for trying to solve the time waiting problem
# (c) 2016 by LocutusOfPenguin - use at your own risk:-)

from dgthw import *
from logging.handlers import RotatingFileHandler
import time

# Enable logging
handler = RotatingFileHandler('test.log', maxBytes=1024 * 1024, backupCount=9)
logging.basicConfig(level=getattr(logging, 'DEBUG'),
                    format='%(asctime)s.%(msecs)03d %(levelname)5s %(module)10s - %(funcName)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S", handlers=[handler])
logging.getLogger("chess.uci").setLevel(logging.INFO)  # don't want to get so many python-chess uci messages
logging.debug('#'*14 + ' Test für Queue ' + '#'*14)


def main():
    def bl(beeplevel):
        if beeplevel == BeepLevel.YES:
            return True
        if beeplevel == BeepLevel.NO:
            return False
        return bool(15 & beeplevel.value)

    dgthardware = DgtHw()
    dgthardware.start()

    bl_button = bl(BeepLevel.BUTTON)
    text1 = Dgt.DISPLAY_TEXT(l=None, m='text 1', s=None, wait=False, beep=bl_button, duration=1)
    text2 = Dgt.DISPLAY_TEXT(l=None, m='text 2', s=None, wait=False, beep=bl_button, duration=1)
    text3 = Dgt.DISPLAY_TEXT(l=None, m='text 3', s=None, wait=True, beep=bl_button, duration=0.5)
    text4 = Dgt.DISPLAY_TEXT(l=None, m='text 4', s=None, wait=True, beep=bl_button, duration=0.5)
    time0 = Dgt.DISPLAY_TIME(force=True, wait=True)
    strt0 = Dgt.CLOCK_START(time_left=5, time_right=3, side=0x04, wait=True, callback=None)

    # test button - should be quick on second button press!
    nomove = Dgt.DISPLAY_TEXT(l=None, m='no move', s='nomove', wait=False, beep=bl_button, duration=1)
    endclock = time0

    logging.debug('TEST 1 - 2 msg - but no problem')
    DisplayDgt.show(text1)
    time.sleep(2)
    DisplayDgt.show(text2)
    time.sleep(2)

    logging.debug('TEST 2 - Now with display_time, should wait')
    DisplayDgt.show(time0)
    DisplayDgt.show(text3)
    time.sleep(2)

    logging.debug('TEST 3 - Now with 0.5s waiting text')
    DisplayDgt.show(text4)
    time.sleep(1)

    logging.debug('TEST 4 - just a serialnr')
    DisplayDgt.show(Dgt.SERIALNR())  # test a different message

    # button press1
    DisplayDgt.show(nomove)
    DisplayDgt.show(endclock)
    time.sleep(1)
    # button press 2
    DisplayDgt.show(nomove)
    DisplayDgt.show(endclock)

    # Test with clock_start
    DisplayDgt.show(text1)
    DisplayDgt.show(strt0)
    DisplayDgt.show(text3)

    # Event loop
    logging.info('evt_queue ready')
    while True:
        try:
            event = evt_queue.get()
        except queue.Empty:
            pass
        else:
            logging.debug('received event from evt_queue: %s', event)

            print(event)
            evt_queue.task_done()

if __name__ == '__main__':
    main()
