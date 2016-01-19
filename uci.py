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
from threading import Timer


class Informer(chess.uci.InfoHandler):
    def __init__(self):
        super(Informer, self).__init__()
        self.dep = 0
        self.allow_score = True
        self.allow_pv = True

    def on_go(self):
        self.dep = 0
        self.allow_score = True
        self.allow_pv = True
        super().on_go()

    def depth(self, dep):
        self.dep = dep
        super().depth(dep)

    def _reset_allow_score(self):
        logging.debug('score-lock stopped')
        self.allow_score = True

    def _reset_allow_pv(self):
        logging.debug('pv-lock stopped')
        self.allow_pv = True

    def _allow_fire_score(self):
        if self.allow_score:
            self.allow_score = False
            Timer(0.2, self._reset_allow_score).start()
            logging.debug('score-lock started')
            return True
        else:
            logging.debug('score-lock still active')
            return False

    def _allow_fire_pv(self):
        if self.allow_pv:
            self.allow_pv = False
            Timer(0.2, self._reset_allow_pv).start()
            logging.debug('pv-lock started')
            return True
        else:
            logging.debug('pv-lock still active')
            return False

    def score(self, cp, mate, lowerbound, upperbound):
        if self._allow_fire_score():
            Observable.fire(Event.NEW_SCORE, score=cp, mate=mate)
        super().score(cp, mate, lowerbound, upperbound)

    def pv(self, moves):
        if self._allow_fire_pv():
            Observable.fire(Event.NEW_PV, pv=moves)
        super().pv(moves)


class Engine(object):

    def __init__(self, path, hostname=None, username=None, key_file=None, password=None):
        super(Engine, self).__init__()
        try:
            self.path = None
            if hostname:
                logging.info("Connecting to [%s]", hostname)
                if key_file:
                    shell = spur.SshShell(hostname=hostname, username=username, private_key_file=key_file,
                                          missing_host_key=paramiko.AutoAddPolicy())
                else:
                    shell = spur.SshShell(hostname=hostname, username=username, password=password,
                                          missing_host_key=paramiko.AutoAddPolicy())
                self.engine = chess.uci.spur_spawn_engine(shell, [path])
            else:
                path = which(path)
                if not path:
                    logging.error("Engine not found")
                    self.engine = None
                else:
                    self.engine = chess.uci.popen_engine(path)
                    self.path = path
            if self.engine:
                handler = Informer()
                self.engine.info_handlers.append(handler)
                self.engine.uci()
            self.options = {}
            self.future = None
            self.show_best = True

            self.res = None
            self.status = EngineStatus.WAIT

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
                
                elo_1, elo_2 = float(self.engine.options['UCI_Elo'][2]), float(self.engine.options['UCI_Elo'][3])
                min_elo, max_elo = min(elo_1, elo_2), max(elo_1, elo_2)
                set_elo = min(int(min_elo + (max_elo-min_elo) * (float(level)) / 19.0), int(max_elo))
                self.option('UCI_Elo', str(set_elo))
            pass
        else:
            logging.warning("Engine does not support skill levels")
            return False
        return True

    def has_levels(self):
        return ('Skill Level' in self.engine.options) or ('UCI_LimitStrength' in self.engine.options)

    def has_chess960(self):
        return 'UCI_Chess960' in self.engine.options

    def get_path(self):
        return self.path  # path is only "not none" if its a local engine - see __init__

    def position(self, game):
        self.engine.position(game)

    def quit(self):
        return self.engine.quit()

    def terminate(self):
        return self.engine.terminate()

    def kill(self):
        return self.engine.kill()

    def popen_engine(self, path):
        self.engine = chess.uci.popen_engine(path)

    def uci(self):
        self.engine.uci()

    def stop(self, show_best=False):
        if self.status == EngineStatus.WAIT:
            logging.info('Engine already stopped')
            return self.res
        self.show_best = show_best
        self.engine.stop()
        return self.future.result()

    def go(self, time_dict):
        if self.status != EngineStatus.WAIT:
            logging.warning('Search think still not waiting - strange!')
        self.status = EngineStatus.THINK
        self.show_best = True
        time_dict['async_callback'] = self.callback

        Display.show(Message.SEARCH_STARTED(engine_status=self.status))
        self.future = self.engine.go(**time_dict)
        return self.future

    def ponder(self):
        if self.status != EngineStatus.WAIT:
            logging.warning('Search ponder still not waiting - strange!')
        self.status = EngineStatus.PONDER
        self.show_best = False

        Display.show(Message.SEARCH_STARTED(engine_status=self.status))
        self.future = self.engine.go(ponder=True, infinite=True, async_callback=self.callback)
        return self.future

    def callback(self, command):
        self.res = command.result()
        Display.show(Message.SEARCH_STOPPED(engine_status=self.status, result=self.res))
        if self.show_best:
            Observable.fire(Event.BEST_MOVE, result=self.res, inbook=False)
        else:
            logging.debug('Event Best_Move not fired')
        self.status = EngineStatus.WAIT

    def is_thinking(self):
        return self.status == EngineStatus.THINK

    def is_pondering(self):
        return self.status == EngineStatus.PONDER

    def is_waiting(self):
        return self.status == EngineStatus.WAIT
