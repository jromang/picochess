# Copyright (C) 2013-2018 Jean-Francois Romang (jromang@posteo.de)
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
from threading import Timer, Thread, Lock
from copy import deepcopy

from utilities import DisplayDgt, DispatchDgt, dispatch_queue
from dgt.api import Dgt, DgtApi
from dgt.menu import DgtMenu


class Dispatcher(DispatchDgt, Thread):

    """A dispatcher taking the dispatch_queue and fill dgt_queue with the commands in time."""

    def __init__(self, dgtmenu: DgtMenu):
        super(Dispatcher, self).__init__()

        self.dgtmenu = dgtmenu
        self.devices = set()
        self.maxtimer = {}
        self.maxtimer_running = {}
        self.clock_connected = {}
        self.time_factor = 1  # This is for testing the duration - remove it lateron!
        self.tasks = {}  # delayed task array

        self.display_hash = {}  # Hash value of clock's display
        self.process_lock = {}

    def register(self, device: str):
        """Register new device to send DgtApi messsages."""
        logging.debug('device %s registered', device)
        self.devices.add(device)
        self.maxtimer[device] = None
        self.maxtimer_running[device] = False
        self.clock_connected[device] = False
        self.process_lock[device] = Lock()
        self.tasks[device] = []
        self.display_hash[device] = None

    def is_prio_device(self, dev, connect):
        """Return the most prio registered device."""
        logging.debug('(%s) clock connected: %s', dev, connect)
        if not connect:
            return False
        if 'i2c' in self.devices:
            return 'i2c' == dev
        if 'ser' in self.devices:
            return 'ser' == dev
        return 'web' == dev

    def _stopped_maxtimer(self, dev: str):
        self.maxtimer_running[dev] = False
        self.dgtmenu.disable_picochess_displayed(dev)

        if dev not in self.devices:
            logging.debug('delete not registered (%s) tasks', dev)
            self.tasks[dev] = []
            return
        if self.tasks[dev]:
            logging.debug('processing delayed (%s) tasks: %s', dev, self.tasks[dev])
        else:
            logging.debug('(%s) max timer finished - returning to time display', dev)
            DisplayDgt.show(Dgt.DISPLAY_TIME(force=False, wait=True, devs={dev}))
        while self.tasks[dev]:
            logging.debug('(%s) tasks has %i members', dev, len(self.tasks[dev]))
            try:
                message = self.tasks[dev].pop(0)
            except IndexError:
                break
            with self.process_lock[dev]:
                self._process_message(message, dev)
            if self.maxtimer_running[dev]:  # run over the task list until a maxtime command was processed
                remaining = len(self.tasks[dev])
                if remaining:
                    logging.debug('(%s) tasks stopped on %i remaining members', dev, remaining)
                else:
                    logging.debug('(%s) tasks completed', dev)
                break

    def _process_message(self, message, dev: str):
        do_handle = True
        if repr(message) in (DgtApi.CLOCK_START, DgtApi.CLOCK_STOP, DgtApi.DISPLAY_TIME):
            self.display_hash[dev] = None  # Cant know the clock display if command changing the running status
        else:
            if repr(message) in (DgtApi.DISPLAY_MOVE, DgtApi.DISPLAY_TEXT):
                if self.display_hash[dev] == hash(message) and not message.beep:
                    do_handle = False
                else:
                    self.display_hash[dev] = hash(message)

        if do_handle:
            logging.debug('(%s) handle DgtApi: %s', dev, message)
            if repr(message) == DgtApi.CLOCK_VERSION:
                logging.debug('(%s) clock registered', dev)
                self.clock_connected[dev] = True

            clk = (DgtApi.DISPLAY_MOVE, DgtApi.DISPLAY_TEXT, DgtApi.DISPLAY_TIME,
                   DgtApi.CLOCK_SET, DgtApi.CLOCK_START, DgtApi.CLOCK_STOP)
            if repr(message) in clk and not self.clock_connected[dev]:
                logging.debug('(%s) clock still not registered => ignore %s', dev, message)
                return
            if hasattr(message, 'maxtime'):
                if repr(message) == DgtApi.DISPLAY_TEXT:
                    if message.maxtime == 2.1:  # 2.1=picochess message
                        self.dgtmenu.enable_picochess_displayed(dev)
                    if self.dgtmenu.inside_updt_menu():
                        if message.maxtime == 0.1:  # 0.1=eBoard error
                            logging.debug('(%s) inside update menu => board errors not displayed', dev)
                            return
                        if message.maxtime == 1.1:  # 1.1=eBoard connect
                            logging.debug('(%s) inside update menu => board connect not displayed', dev)
                            return
                if message.maxtime > 0.1:  # filter out "all the time" show and "eBoard error" messages
                    self.maxtimer[dev] = Timer(message.maxtime * self.time_factor, self._stopped_maxtimer, [dev])
                    self.maxtimer[dev].start()
                    logging.debug('(%s) showing %s for %.1f secs', dev, message, message.maxtime * self.time_factor)
                    self.maxtimer_running[dev] = True
            if repr(message) == DgtApi.CLOCK_START and self.dgtmenu.inside_updt_menu():
                logging.debug('(%s) inside update menu => clock not started', dev)
                return
            message.devs = {dev}  # on new system, we only have ONE device each message - force this!
            DisplayDgt.show(message)
        else:
            logging.debug('(%s) hash ignore DgtApi: %s', dev, message)

    def stop_maxtimer(self, dev):
        """Stop the maxtimer."""
        if self.maxtimer_running[dev]:
            self.maxtimer[dev].cancel()
            self.maxtimer[dev].join()
            self.maxtimer_running[dev] = False
            self.dgtmenu.disable_picochess_displayed(dev)

    def run(self):
        """Call by threading.Thread start() function."""
        logging.info('dispatch_queue ready')
        while True:
            # Check if we have something to display
            try:
                msg = dispatch_queue.get()
                logging.debug('received command from dispatch_queue: %s devs: %s', msg, ','.join(msg.devs))

                for dev in msg.devs & self.devices:
                    message = deepcopy(msg)
                    if self.maxtimer_running[dev]:
                        if hasattr(message, 'wait'):
                            if message.wait:
                                self.tasks[dev].append(message)
                                logging.debug('(%s) tasks delayed: %s', dev, self.tasks[dev])
                                continue
                            else:
                                logging.debug('ignore former maxtime - dev: %s', dev)
                                self.stop_maxtimer(dev)
                                if self.tasks[dev]:
                                    logging.debug('delete following (%s) tasks: %s', dev, self.tasks[dev])
                                    while self.tasks[dev]:  # but do the last CLOCK_START()
                                        command = self.tasks[dev].pop()
                                        if repr(command) == DgtApi.CLOCK_START:  # clock might be in set mode
                                            logging.debug('processing (last) delayed clock start command')
                                            with self.process_lock[dev]:
                                                self._process_message(command, dev)
                                            break
                                    self.tasks[dev] = []
                        else:
                            logging.debug('command doesnt change the clock display => (%s) max timer ignored', dev)
                    else:
                        logging.debug('(%s) max timer not running => processing command: %s', dev, message)

                    with self.process_lock[dev]:
                        self._process_message(message, dev)
            except queue.Empty:
                pass
