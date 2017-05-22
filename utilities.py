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
import urllib.request
import socket
import json
import time
import copy
import configparser

from threading import Timer
from subprocess import Popen, PIPE
from re import compile, sub

from dgt.translate import DgtTranslate
from dgt.api import Dgt

# picochess version
version = '088'

evt_queue = queue.Queue()
dispatch_queue = queue.Queue()
serial_queue = queue.Queue()

msgdisplay_devices = []
dgtdisplay_devices = []
dgtdispatch_devices = []


class Observable(object):

    """Input devices are observable."""

    def __init__(self):
        super(Observable, self).__init__()

    @staticmethod
    def fire(event):
        """Put an event on the Queue."""
        evt_queue.put(copy.deepcopy(event))


class DispatchDgt(object):

    """Input devices are observable."""

    def __init__(self):
        super(DispatchDgt, self).__init__()

    @staticmethod
    def fire(dgt):
        """Put an event on the Queue."""
        dispatch_queue.put(copy.deepcopy(dgt))


class DisplayMsg(object):

    """Display devices (DGT XL clock, Piface LCD, pgn file...)."""

    def __init__(self):
        super(DisplayMsg, self).__init__()
        self.msg_queue = queue.Queue()
        msgdisplay_devices.append(self)

    @staticmethod
    def show(message):
        """Sends a message on each display device."""
        for display in msgdisplay_devices:
            display.msg_queue.put(copy.deepcopy(message))


class DisplayDgt(object):

    """Display devices (DGT XL clock, Piface LCD, pgn file...)."""

    def __init__(self):
        super(DisplayDgt, self).__init__()
        self.dgt_queue = queue.Queue()
        dgtdisplay_devices.append(self)

    @staticmethod
    def show(message):
        """Sends a message on each display device."""
        for display in dgtdisplay_devices:
            display.dgt_queue.put(copy.deepcopy(message))


class RepeatedTimer(object):

    """Call function on a given interval."""

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
        """Return the running status."""
        return self.timer_running

    def start(self):
        """Start the RepeatedTimer."""
        if not self.timer_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.timer_running = True
        else:
            logging.info('repeated timer already running - strange!')

    def stop(self):
        """Stop the RepeatedTimer."""
        if self.timer_running:
            self._timer.cancel()
            self.timer_running = False
        else:
            logging.info('repeated timer already stopped - strange!')


def get_opening_books():
    """Build an opening book lib."""
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
    """Return the match method once, then stop."""
    if seconds < 0:
        logging.warning('negative time %i', seconds)
        return 0, 0, 0
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return hours, mins, secs


def get_tags():
    """Get the last 5 tags from git."""
    git = 'git.exe' if platform.system() == 'Windows' else 'git'
    tags = [compile(r'[^\d]+').sub('', tags)
            for tags in Popen([git, 'tag'], stdout=PIPE).communicate()[0].decode(encoding='UTF-8').split('\n')[-4:-1]]
    return tags  # returns something like ['085', '086', '087']


def update_picochess(dgtpi: bool, auto_reboot: bool, dgttranslate: DgtTranslate):
    """Update picochess from git."""
    def do_command(command):
        return Popen(command, stdout=PIPE).communicate()[0].decode(encoding='UTF-8')

    git = 'git.exe' if platform.system() == 'Windows' else 'git'

    branch = do_command([git, 'rev-parse', '--abbrev-ref', 'HEAD']).rstrip()
    if branch == 'stable' or branch == 'master':
        output = do_command([git, 'remote', 'update'])  # Fetch remote repo
        logging.debug('git remote:')
        logging.debug(output)
        output = do_command([git, 'status', '--porcelain', '-uno'])
        if output:
            logging.debug('git status:')
            logging.debug(output)
            DispatchDgt.fire(dgttranslate.text('Y25_update'))
            output = do_command([git, 'pull', 'origin', branch])
            logging.debug('git pull:')
            logging.debug(output)
            output = do_command(['pip3', 'install', '-r', 'requirements.txt'])
            logging.debug('pip3 install:')
            logging.debug(output)
            if auto_reboot:
                reboot(dgtpi, dev='web')
            else:
                time.sleep(2)  # give time to display the "update" message
        else:
            logging.debug('no update available')


def shutdown(dgtpi: bool, dev: str):
    """Shutdown picochess."""
    logging.debug('shutting down system requested by (%s)', dev)
    time.sleep(3)  # give some time to send out the pgn file or speak the event
    if platform.system() == 'Windows':
        os.system('shutdown /s')
    elif dgtpi:
        os.system('systemctl isolate dgtpistandby.target')
    else:
        os.system('shutdown -h now')


def reboot(dgtpi: bool, dev: str):
    """Reboot picochess."""
    logging.debug('rebooting system requested by (%s)', dev)
    time.sleep(3)  # give some time to send out the pgn file or speak the event
    if platform.system() == 'Windows':
        os.system('shutdown /r')
    elif dgtpi:
        os.system('systemctl restart picochess')
    else:
        os.system('reboot')


def get_location():
    """Return the location of the user and the external and interal ip adr."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        int_ip = sock.getsockname()[0]
        sock.close()

        response = urllib.request.urlopen('https://freegeoip.net/json/')
        j = json.loads(response.read().decode())
        country_name = j['country_name'] + ' ' if 'country_name' in j else ''
        country_code = j['country_code'] + ' ' if 'country_code' in j else ''
        ext_ip = j['ip'] if 'ip' in j else None
        city = j['city'] + ', ' if 'city' in j else ''
        return city + country_name + country_code, ext_ip, int_ip
    except:
        return '?', None, None
