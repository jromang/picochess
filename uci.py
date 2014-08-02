from observable import *
import logging
import os
import spur
import paramiko
import io
import threading


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
        for path in os.environ["PATH"].split(os.pathsep):
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
        logging.debug("->[%s]", command)
        self.process.stdin_write(bytes((command+'\n').encode('utf-8')))

    def write(self, b):
        if b == b'\n':
            line = self.out.getvalue().decode("utf-8")
            logging.debug("<-[%s]", line)
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
            option_default = None if not 'default' in tokens else tokens[tokens.index('default')+1]
            option_min = None if not 'min' in tokens else tokens[tokens.index('min')+1]
            option_max = None if not 'max' in tokens else tokens[tokens.index('max')+1]
            self.options[option_name] = (option_type, option_default, option_min, option_max)
        if tokens[0] == 'bestmove':
            self.fire(type='bestmove', move=tokens[1])

    def set_option(self, name, value):
        self.send("setoption name " + name + " value " + str(value))

    def set_level(self, level):
        if 'Skill Level' in self.options: #Stockfish
            self.set_option("Skill Level", level)
        elif 'UCI_LimitStrength' in self.options:
            if level == 20:
                self.set_option('UCI_LimitStrength', 'false')
            else:
                self.set_option('UCI_LimitStrength', 'true')
                min_elo = float(self.options['UCI_Elo'][2])
                max_elo = float(self.options['UCI_Elo'][3])
                set_elo = int(min_elo + (max_elo-min_elo) * float(level) / 19.0)
                self.set_option('UCI_Elo', str(set_elo))
            pass
        else:
            logging.warning("Engine does not support skill levels")