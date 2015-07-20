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
import spur
import paramiko
import chess.uci


class Informer(chess.uci.InfoHandler, Observable):
    def __init__(self):
        super(Informer, self).__init__()
        self.mate_found = False

    def on_go(self):
        self.mate_found = False
        super().on_go()

    def on_bestmove(self,bestmove, ponder):
        self.fire(Event.BEST_MOVE, move=bestmove, ponder=ponder)
        super().on_bestmove(bestmove, ponder)

    def score(self,cp, mate, lowerbound, upperbound):
        if mate is None or not self.mate_found:
            self.fire(Event.SCORE, score=cp, mate=mate)
        if mate is not None:
            self.mate_found = True
        super().score(cp, mate, lowerbound, upperbound)

    def pv(self,moves):
        if not self.mate_found:
            self.fire(Event.NEW_PV, pv=moves)
        super().pv(moves)


class Engine:

    def __init__(self, path, hostname=None, username=None, key_file=None, password=None):
        try:
            if hostname:
                logging.info("Connecting to [%s]", hostname)
                if key_file:
                    shell = spur.SshShell(hostname=hostname, username=username, private_key_file=key_file, missing_host_key=paramiko.AutoAddPolicy())
                else:
                    shell = spur.SshShell(hostname=hostname, username=username, password=password, missing_host_key=paramiko.AutoAddPolicy())
                self.engine = chess.uci.spur_spwan_engine(shell, [path])
            else:
                path = which(path)
                if not path:
                    logging.error("Engine not found")
                    self.engine = None
                else:
                    self.engine = chess.uci.popen_engine(path)
                    self.engine.uci()
                    handler = Informer()
                    self.engine.info_handlers.append(handler)
            self.options = {}
            self.future = None
        except OSError:
            logging.exception("OS error in starting engine")

    def get(self):
        return self.engine

    def option(self, name, value):
        self.options[name] = value

    def send(self):
        self.engine.setoption(self.options)

    def level(self, level):
        """ Sets the engine playing strength, between 0 and 20. """
        if level < 0 or level > 20:
            logging.error('Level not in range (0,20) :[%i]', level)
            return False
        if 'Skill Level' in self.engine.options:  # Stockfish uses 'Skill Level' option
            self.option("Skill Level", level)
        elif 'UCI_LimitStrength' in self.engine.options:  # Generic 'UCI_LimitStrength' option for other engines
            if level == 20:
                self.option('UCI_LimitStrength', 'false')
            else:
                self.option('UCI_LimitStrength', 'true')
                min_elo = float(self.engine.options['UCI_Elo'][2])
                max_elo = float(self.engine.options['UCI_Elo'][3])
                set_elo = min(int(min_elo + (max_elo-min_elo) * (float(level)) / 19.0), int(max_elo))
                self.option('UCI_Elo', str(set_elo))
            pass
        else:
            logging.warning("Engine does not support skill levels")
            return False
        return True

    def position(self, game):
        self.engine.position(game)

    def stop(self):
        self.engine.stop()
        return self.future.result()

    def go(self, time_dict):
        self.future = self.engine.go(**time_dict)
        return self.future

    def ponder(self):
        self.future = self.engine.go(ponder=True, infinite=True, async_callback=True)
        return self.future

