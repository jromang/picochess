import abc
from observable import *
import logging
import os.path


class UCIEngine(Observable, metaclass=abc.ABCMeta):

    def __init__(self, path):
        Observable.__init__(self)
        logger = logging.getLogger(__name__)
        if not os.path.isfile(path):
            logger.error("Engine not found [%s]", path)

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