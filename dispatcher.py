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

from utilities import DisplayDgt, DispatchDgt, dispatch_queue
import logging
import queue
from dgt.api import Dgt, DgtApi
from dgt.menu import DgtMenu
from threading import Timer, Thread, Lock


class Dispatcher(DispatchDgt, Thread):

    """a dispatcher taking the dispatch_queue and fill dgt_queue with the commands in time."""

    def __init__(self, dgtmenu: DgtMenu):
        super(Dispatcher, self).__init__()

        self.dgtmenu = dgtmenu
        self.devices = set()
        self.maxtimer = {}
        self.maxtimer_running = {}
        self.time_factor = 3  # This is for testing the duration - remove it lateron!
        self.tasks = {}  # delayed task array

        self.display_hash = {}  # Hash value of clock's display
        self.process_lock = {}

    def register(self, device: str):
        self.devices.add(device)
        self.maxtimer[device] = None
        self.maxtimer_running[device] = False
        self.process_lock[device] = Lock()
        self.tasks[device] = []
        self.display_hash[device] = None

    def _stopped_maxtimer(self, dev):
        self.maxtimer_running[dev] = False
        self.dgtmenu.disable_picochess_displayed(dev)

        if dev not in self.devices:
            logging.debug('delete not registered (%s) tasks', dev)
            self.tasks[dev] = []
            return
        DisplayDgt.show(Dgt.DISPLAY_TIME(force=False, wait=True, devs={dev}))
        if self.tasks[dev]:
            logging.debug('processing delayed (%s) tasks: %s', dev, self.tasks[dev])
        while self.tasks[dev]:
            logging.debug('(%s) tasks has %i members', dev, len(self.tasks[dev]))
            message = self.tasks[dev].pop(0)
            with self.process_lock[dev]:
                self._process_message(message, dev)
            if self.maxtimer_running[dev]:  # run over the task list until a maxtime command was processed
                break

    def _process_message(self, message, dev):
        do_handle = True
        if repr(message) in (DgtApi.CLOCK_START, DgtApi.CLOCK_STOP, DgtApi.CLOCK_TIME):
            self.display_hash[dev] = None  # Cant know the clock display if command changing the running status
        else:
            if repr(message) in (DgtApi.DISPLAY_MOVE, DgtApi.DISPLAY_TEXT):
                if self.display_hash[dev] == hash(message) and not message.beep:
                    do_handle = False
                else:
                    logging.debug('(%s) clock display hash old: %s new: %s', dev, self.display_hash[dev], hash(message))
                    self.display_hash[dev] = hash(message)

        devstr = ','.join(message.devs)
        if do_handle:
            logging.debug('(%s) handle DgtApi: %s devs: %s', dev, message, devstr)
            if hasattr(message, 'maxtime') and message.maxtime > 0:
                if repr(message) == DgtApi.DISPLAY_TEXT and message.maxtime == 2:
                    self.dgtmenu.enable_picochess_displayed(dev)
                self.maxtimer[dev] = Timer(message.maxtime * self.time_factor, self._stopped_maxtimer, [dev])
                self.maxtimer[dev].start()
                logging.debug('(%s) showing %s for %.1f secs devs: %s',
                              dev, message, message.maxtime * self.time_factor, devstr)
                self.maxtimer_running[dev] = True
            message.devs = {dev}  # on new system, we only have ONE device each message - force this!
            DisplayDgt.show(message)
        else:
            logging.debug('(%s) hash ignore DgtApi: %s devs: %s', dev, message, devstr)

    def run(self):
        """called from threading.Thread by its start() function."""
        logging.info('dispatch_queue ready')
        while True:
            # Check if we have something to display
            try:
                message = dispatch_queue.get()
                logging.debug('received command from dispatch_queue: %s devs: %s', message, ','.join(message.devs))

                for dev in message.devs & self.devices:
                    if self.maxtimer_running[dev]:
                        if hasattr(message, 'wait'):
                            if message.wait:
                                self.tasks[dev].append(message)
                                logging.debug('(%s) tasks delayed: %s', dev, self.tasks[dev])
                                continue
                            else:
                                logging.debug('ignore former maxtime - dev: %s', dev)
                                self.maxtimer[dev].cancel()
                                self.maxtimer[dev].join()
                                self.maxtimer_running[dev] = False
                                self.dgtmenu.disable_picochess_displayed(dev)
                                if self.tasks[dev]:
                                    logging.debug('delete following (%s) tasks: %s', dev, self.tasks[dev])
                                    self.tasks[dev] = []
                        else:
                            logging.debug('command doesnt change the clock display => max timer (%s) ignored', dev)
                    else:
                        logging.debug('max timer (%s) not running => process command', dev)

                    with self.process_lock[dev]:
                        self._process_message(message, dev)
            except queue.Empty:
                pass
