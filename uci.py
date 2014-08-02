import abc
from observable import *
import logging
import os.path
import spur
import paramiko
import subprocess


class UCIEngine(Observable, metaclass=abc.ABCMeta):

    def __init__(self, path, hostname=None, username=None, key_file=None):
        Observable.__init__(self)
        logger = logging.getLogger(__name__)
        try:
            if hostname:
                logger.info("Connecting to [%s]", hostname)
                shell = spur.SshShell(
                    hostname=hostname,
                    username=username,
                    private_key_file=key_file,
                    missing_host_key=paramiko.AutoAddPolicy())
                self.process = shell.spawn([path], stdout=subprocess.PIPE, store_pid=True, allow_error=True)

            elif not os.path.isfile(path):
                logger.error("Engine not found [%s]", path)
                shell = spur.LocalShell()
                self.process = shell.spawn(path, stdout=subprocess.PIPE, store_pid=True)
        except OSError:
            logger.exception("OS error in starting engine")


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