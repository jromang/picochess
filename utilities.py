# Copyright (C) 2013-2017 Jean-Francois Romang (jromang@posteo.de)
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

import logging
import queue
import os
import platform
import subprocess
import urllib.request
import socket
import json
import time
import copy
from threading import Timer

import configparser
from dgttranslate import DgtTranslate
from dgtapi import Dgt

# picochess version
version = '085'

evt_queue = queue.Queue()
dispatch_queue = queue.Queue()
serial_queue = queue.Queue()

msgdisplay_devices = []
dgtdisplay_devices = []
dgtdispatch_devices = []


class Observable(object):  # Input devices are observable
    def __init__(self):
        super(Observable, self).__init__()

    @staticmethod
    def fire(event):
        evt_queue.put(copy.deepcopy(event))


class DispatchDgt(object):  # Input devices are observable
    def __init__(self):
        super(DispatchDgt, self).__init__()

    @staticmethod
    def fire(dgt):
        dispatch_queue.put(copy.deepcopy(dgt))


class DisplayMsg(object):  # Display devices (DGT XL clock, Piface LCD, pgn file...)
    def __init__(self):
        super(DisplayMsg, self).__init__()
        self.msg_queue = queue.Queue()
        msgdisplay_devices.append(self)

    @staticmethod
    def show(message):  # Sends a message on each display device
        for display in msgdisplay_devices:
            display.msg_queue.put(copy.deepcopy(message))


class DisplayDgt(object):  # Display devices (DGT XL clock, Piface LCD, pgn file...)
    def __init__(self):
        super(DisplayDgt, self).__init__()
        self.dgt_queue = queue.Queue()
        dgtdisplay_devices.append(self)

    @staticmethod
    def show(message):  # Sends a message on each display device
        for display in dgtdisplay_devices:
            display.dgt_queue.put(copy.deepcopy(message))


# switch/case instruction in python
class switch(object):
    def __init__(self, value):
        if type(value) is int:
            self.value = value
        else:
            self.value = value._type
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.timer_running = False

    def _run(self):
        self.timer_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def is_running(self):
        return self.timer_running

    def start(self):
        if not self.timer_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.timer_running = True
        else:
            logging.info('repeated timer already running - strange!')

    def stop(self):
        if self.timer_running:
            self._timer.cancel()
            self.timer_running = False
        else:
            logging.info('repeated timer already stopped - strange!')


def get_opening_books():
    config = configparser.ConfigParser()
    config.optionxform = str
    program_path = os.path.dirname(os.path.realpath(__file__)) + os.sep
    book_path = program_path + 'books'
    config.read(book_path + os.sep + 'books.ini')

    library = []
    for section in config.sections():
        text = Dgt.DISPLAY_TEXT(l=config[section]['large'], m=config[section]['medium'], s=config[section]['small'],
                                wait=True, beep=False, maxtime=0, devs={'ser', 'i2c', 'web'})
        library.append(
            {
                'file': 'books' + os.sep + section,
                'text': text
            }
        )
    return library


def hours_minutes_seconds(seconds: int):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s


def update_picochess(dgtpi: bool, auto_reboot: bool, dgttranslate: DgtTranslate):
    git = 'git.exe' if platform.system() == 'Windows' else 'git'

    branch = subprocess.Popen([git, 'rev-parse', '--abbrev-ref', 'HEAD'],
                              stdout=subprocess.PIPE).communicate()[0].decode(encoding='UTF-8').rstrip()
    if branch == 'stable' or branch == 'master':
        # Fetch remote repo
        output = subprocess.Popen([git, 'remote', 'update'],
                                  stdout=subprocess.PIPE).communicate()[0].decode(encoding='UTF-8')
        logging.debug(output)
        # Check if update is needed - but first force an english environment for it
        force_en_env = os.environ.copy()
        force_en_env['LC_ALL'] = 'C'
        output = subprocess.Popen([git, 'status', '-uno'],
                                  stdout=subprocess.PIPE, env=force_en_env).communicate()[0].decode(encoding='UTF-8')
        logging.debug(output)
        if 'up-to-date' not in output:
            DispatchDgt.fire(dgttranslate.text('Y00_update'))
            # Update
            logging.debug('updating picochess')
            output = subprocess.Popen(['pip3', 'install', '-r', 'requirements.txt'],
                                      stdout=subprocess.PIPE).communicate()[0].decode(encoding='UTF-8')
            logging.debug(output)
            output = subprocess.Popen([git, 'pull', 'origin', branch],
                                      stdout=subprocess.PIPE).communicate()[0].decode(encoding='UTF-8')
            logging.debug(output)
            if auto_reboot:
                reboot(dgtpi, dev='web')
            else:
                time.sleep(1)  # give time to display the "update" message


def shutdown(dgtpi: bool, dev: str):
    logging.debug('shutting down system requested by ({})'.format(dev))
    time.sleep(2)  # give some time to send out the pgn file or speak the event
    if platform.system() == 'Windows':
        os.system('shutdown /s')
    elif dgtpi:
        os.system('systemctl isolate dgtpistandby.target')
    else:
        os.system('shutdown -h now')


def reboot(dgtpi: bool, dev: str):
    logging.debug('rebooting system requested by ({})'.format(dev))
    time.sleep(2)  # give some time to send out the pgn file or speak the event
    if platform.system() == 'Windows':
        os.system('shutdown /r')
    elif dgtpi:
        os.system('systemctl restart picochess')
    else:
        os.system('reboot')


def get_location():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        int_ip = s.getsockname()[0]
        s.close()

        response = urllib.request.urlopen('https://freegeoip.net/json/')
        j = json.loads(response.read().decode())
        country_name = j['country_name'] + ' ' if 'country_name' in j else ''
        country_code = j['country_code'] + ' ' if 'country_code' in j else ''
        ext_ip = j['ip'] if 'ip' in j else None
        city = j['city'] + ', ' if 'city' in j else ''
        return city + country_name + country_code, ext_ip, int_ip
    except:
        return '?', None, None
