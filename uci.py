import abc
from observable import *
import logging
import os
import spur
import paramiko
import subprocess


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


class UCIEngine(Observable, metaclass=abc.ABCMeta):

    def __init__(self, path, hostname=None, username=None, key_file=None):
        Observable.__init__(self)
        try:
            if hostname:
                logging.info("Connecting to [%s]", hostname)
                shell = spur.SshShell(
                    hostname=hostname,
                    username=username,
                    private_key_file=key_file,
                    missing_host_key=paramiko.AutoAddPolicy())
                self.process = shell.spawn([path], stdout=subprocess.PIPE, store_pid=True, allow_error=True)
            else:
                path = which(path)
                if not path:
                    logging.error("Engine not found")
                    shell = spur.LocalShell()
                    self.process = shell.spawn(path, stdout=subprocess.PIPE, store_pid=True)
        except OSError:
            logging.exception("OS error in starting engine")


    @abc.abstractmethod
    def set_level(self, level):
        """
        Set the engine level (from 1 to 20) ; this method is specific to each UCI engine.
        You could for example use the 'UCI_LimitStrength' option for some engines, or
        the 'Skill level' for Stockfish.
        :param level:
        :return:
        """
        return


class Stockfish(UCIEngine):
    def __init__(self, path):
        UCIEngine.__init__(self, path)

    def set_level(self, level):
        #TODO: set 'Skill Level' UCI option
        return