# Copyright (C) 2013-2014 Jean-Francois Romang (jromang@posteo.de)
#                         Shivkumar Shivaji ()
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

from utilities import *
import logging
import os
import spur
import paramiko
import io
import threading
from collections import deque


def which(program):
    """ Find an executable file on the system path.
    :param program: Name or full path of the executable file
    :return: Full path of the executable file, or None if it was not found
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep) + [os.path.dirname(os.path.realpath(__file__))]:
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    logging.warning("Engine executable [%s] not found", program)
    return None


class Engine(Observable):

    def __init__(self, path, hostname=None, username=None, key_file=None, password=None):
        Observable.__init__(self)
        self.out = io.BytesIO()
        self.uciok_lock = threading.Lock()
        self.uciok_lock.acquire()
        self.name = ""
        self.options = {}
        self.send_best_move = threading.Event()  # Send BEST_MOVE events only when this is set
        self.send_best_move.set()
        try:
            if hostname:
                logging.info("Connecting to [%s]", hostname)
                if key_file:
                    shell = spur.SshShell(hostname=hostname, username=username, private_key_file=key_file, missing_host_key=paramiko.AutoAddPolicy())
                else:
                    shell = spur.SshShell(hostname=hostname, username=username, password=password, missing_host_key=paramiko.AutoAddPolicy())
                self.process = shell.spawn([path], stdout=self, store_pid=True, allow_error=True)
            else:
                path = which(path)
                if not path:
                    logging.error("Engine not found")
                    self.process = None
                else:
                    shell = spur.LocalShell()
                    self.process = shell.spawn(path, stdout=self, store_pid=True)
            self.send("uci")
            self.uciok_lock.acquire() #Wait until uciok
        except OSError:
            logging.exception("OS error in starting engine")

    def send(self, command):
        logging.debug("->Engine [%s]", command)
        self.process.stdin_write(bytes((command+'\n').encode('utf-8')))

    def write(self, b):
        if b == b'\n':
            line = self.out.getvalue().replace(b'\r', b'').decode("utf-8")
            logging.debug("<-Engine [%s]", line)
            if line:
                self.parse(line)
            self.out = io.BytesIO()
        else:
            self.out.write(b)

    def parse(self, line):
        logging.debug("Parsing [%s]", line)
        tokens = line.split()
        if tokens[0] == 'uciok':
            self.uciok_lock.release()
        if tokens[0] == 'id' and tokens[1] == 'name':
            self.name = ' '.join(tokens[2:])
        if tokens[0] == 'option' and tokens[1] == 'name':
            option_name = ' '.join(tokens[2:tokens.index('type')])
            option_type = tokens[tokens.index('type')+1]
            try:
                option_default = None if not 'default' in tokens else tokens[tokens.index('default')+1]
                option_min = None if not 'min' in tokens else tokens[tokens.index('min')+1]
                option_max = None if not 'max' in tokens else tokens[tokens.index('max')+1]
            except IndexError:
                option_default = option_min = option_max = None
                logging.warning("Error when parsing UCI option [%s]", option_name)
            self.options[option_name] = (option_type, option_default, option_min, option_max)
        if tokens[0] == 'bestmove':
            if self.send_best_move.is_set():
                self.fire(Event.BEST_MOVE, move=tokens[1])
            self.send_best_move.set()

    def set_option(self, name, value):
        self.send("setoption name " + name + " value " + str(value))

    def set_level(self, level):
        """ Sets the engine playing strength, between 0 and 20. """
        if level < 0 or level > 20:
            logging.error('Level not in range (0,20) :[%i]', level)
        if 'Skill Level' in self.options:  # Stockfish uses 'Skill Level' option
            self.set_option("Skill Level", level)
        elif 'UCI_LimitStrength' in self.options:  # Generic 'UCI_LimitStrength' option for other engines
            if level == 20:
                self.set_option('UCI_LimitStrength', 'false')
            else:
                self.set_option('UCI_LimitStrength', 'true')
                min_elo = float(self.options['UCI_Elo'][2])
                max_elo = float(self.options['UCI_Elo'][3])
                set_elo = min(int(min_elo + (max_elo-min_elo) * (float(level)) / 19.0), int(self.options['UCI_Elo'][3]))
                self.set_option('UCI_Elo', str(set_elo))
            pass
        else:
            logging.warning("Engine does not support skill levels")

    def set_position(self, game):
        cmd = 'position startpos moves'
        for m in game.move_stack:
            cmd += ' ' + m.uci()
        self.send(cmd)

    def stop(self, ignore_best_move=False):
        if ignore_best_move:
            self.send_best_move.clear()
        else:
            self.send_best_move.set()
        self.send('stop')
        self.send_best_move.wait(2.0)  # If stop() is called with ignore_best_move=True and the engine is not searching,
                                       # the program could be locked here. So we have a timeout for safety.
        if not self.send_best_move.is_set():  # There was no bestmove : send a waring, this should not happen.
            logging.warning('No bestmove after stop()')
            self.send_best_move.set()

    def go(self, time_string):
        self.send('go ' + time_string)