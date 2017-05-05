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

from dgt.api import Event, Dgt
from dgt.util import EngineStatus
from utilities import Observable
import logging
import os
import platform
import spur
import paramiko
import chess.uci
from chess import Board
from threading import Timer
import configparser


def get_installed_engines(engine_shell, engine_file: str):
    """create a library list."""
    return read_engine_ini(engine_shell, (engine_file.rsplit(os.sep, 1))[0])


def read_engine_ini(engine_shell=None, engine_path=None):
    """read engine.ini and creates a library list out of it."""
    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        if engine_shell is None:
            if not engine_path:
                program_path = os.path.dirname(os.path.realpath(__file__)) + os.sep
                engine_path = program_path + 'engines' + os.sep + platform.machine()
            config.read(engine_path + os.sep + 'engines.ini')
        else:
            with engine_shell.open(engine_path + os.sep + 'engines.ini', 'r') as file:
                config.read_file(file)
    except FileNotFoundError:
        pass

    library = []
    for section in config.sections():
        parser = configparser.ConfigParser()
        parser.optionxform = str
        level_dict = {}
        if parser.read(engine_path + os.sep + section + '.uci'):
            for p_section in parser.sections():
                level_dict[p_section] = {}
                for option in parser.options(p_section):
                    level_dict[p_section][option] = parser[p_section][option]

        text = Dgt.DISPLAY_TEXT(l=config[section]['large'], m=config[section]['medium'], s=config[section]['small'],
                                wait=True, beep=False, maxtime=0, devs={'ser', 'i2c', 'web'})
        library.append(
            {
                'file': engine_path + os.sep + section,
                'level_dict': level_dict,
                'text': text,
                'name': config[section]['name']
            }
        )
    return library


def write_engine_ini(engine_path=None):
    """read the engine folder and create the engine.ini file."""
    def write_level_ini(engine_filename: str):
        """write the level part for the engine.ini file."""
        def calc_inc(diflevel: int):
            """calculate the increment for (max 20) levels."""
            if diflevel > 1000:
                inc = int(diflevel / 100)
            else:
                inc = int(diflevel / 10)
            if 20 * inc < diflevel:
                inc = int(diflevel / 20)
            return inc

        parser = configparser.ConfigParser()
        parser.optionxform = str
        if not parser.read(engine_path + os.sep + engine_filename + '.uci'):
            if engine.has_limit_strength():
                uelevel = engine.get().options['UCI_Elo']
                elo_1, elo_2 = int(uelevel[2]), int(uelevel[3])
                minlevel, maxlevel = min(elo_1, elo_2), max(elo_1, elo_2)
                lvl_inc = calc_inc(maxlevel - minlevel)
                level = minlevel
                while level < maxlevel:
                    parser['Elo@{:04d}'.format(level)] = {'UCI_LimitStrength' : 'true', 'UCI_Elo' : str(level)}
                    level += lvl_inc
                parser['Elo@{:04d}'.format(maxlevel)] = {'UCI_LimitStrength': 'false', 'UCI_Elo': str(maxlevel)}
            if engine.has_skill_level():
                sklevel = engine.get().options['Skill Level']
                minlevel, maxlevel = int(sklevel[3]), int(sklevel[4])
                minlevel, maxlevel = min(minlevel, maxlevel), max(minlevel, maxlevel)
                for level in range(minlevel, maxlevel+1):
                    parser['Level@{:02d}'.format(level)] = {'Skill Level': str(level)}
            if engine.has_strength():
                sklevel = engine.get().options['Strength']
                minlevel, maxlevel = int(sklevel[3]), int(sklevel[4])
                minlevel, maxlevel = min(minlevel, maxlevel), max(minlevel, maxlevel)
                lvl_inc = calc_inc(maxlevel - minlevel)
                level = minlevel
                count = 0
                while level < maxlevel:
                    parser['Level@{:02d}'.format(count)] = {'Strength': str(level)}
                    level += lvl_inc
                    count += 1
                parser['Level@{:02d}'.format(count)] = {'Strength': str(maxlevel)}
            with open(engine_path + os.sep + engine_filename + '.uci', 'w') as configfile:
                parser.write(configfile)

    def is_exe(fpath: str):
        """check if fpath is an executable."""
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    def name_build(parts: list, maxlength: int, default_name: str):
        """get a (clever formed) cut name for the part list."""
        eng_name = ''
        for token in parts:
            if len(eng_name) + len(token) > maxlength:
                break
            eng_name += token
        return eng_name if eng_name else default_name

    if not engine_path:
        program_path = os.path.dirname(os.path.realpath(__file__)) + os.sep
        engine_path = program_path + 'engines' + os.sep + platform.machine()
    engine_list = sorted(os.listdir(engine_path))
    config = configparser.ConfigParser()
    config.optionxform = str
    for engine_file_name in engine_list:
        if is_exe(engine_path + os.sep + engine_file_name):
            engine = UciEngine(engine_path + os.sep + engine_file_name)
            if engine:
                print(engine_file_name)
                try:
                    if engine.has_levels():
                        write_level_ini(engine_file_name)
                    engine_name = engine.get().name

                    name_parts = engine_name.replace('.', '').split(' ')
                    name_small = name_build(name_parts, 6, engine_file_name[2:])
                    name_medium = name_build(name_parts, 8, name_small)
                    name_large = name_build(name_parts, 11, name_medium)

                    config[engine_file_name] = {}
                    config[engine_file_name]['name'] = engine_name
                    config[engine_file_name]['small'] = name_small
                    config[engine_file_name]['medium'] = name_medium
                    config[engine_file_name]['large'] = name_large

                except AttributeError:
                    pass
                engine.quit()
    with open(engine_path + os.sep + 'engines.ini', 'w') as configfile:
        config.write(configfile)


class Informer(chess.uci.InfoHandler):

    """internal uci engine info handler."""

    def __init__(self):
        super(Informer, self).__init__()
        self.allow_score = True
        self.allow_pv = True
        self.allow_depth = True

    def on_go(self):
        self.allow_score = True
        self.allow_pv = True
        self.allow_depth = True
        super().on_go()

    def _reset_allow_score(self):
        self.allow_score = True

    def _reset_allow_pv(self):
        self.allow_pv = True

    def _reset_allow_depth(self):
        self.allow_depth = True

    def _allow_fire_score(self):
        if self.allow_score:
            self.allow_score = False
            Timer(0.5, self._reset_allow_score).start()
            return True
        else:
            return False

    def _allow_fire_pv(self):
        if self.allow_pv:
            self.allow_pv = False
            Timer(0.5, self._reset_allow_pv).start()
            return True
        else:
            return False

    def _allow_fire_depth(self):
        if self.allow_depth:
            self.allow_depth = False
            Timer(0.5, self._reset_allow_depth).start()
            return True
        else:
            return False

    def score(self, cp, mate, lowerbound, upperbound):
        if self._allow_fire_score():
            Observable.fire(Event.NEW_SCORE(score=cp, mate=mate))
        super().score(cp, mate, lowerbound, upperbound)

    def pv(self, moves):
        if self._allow_fire_pv() and moves:
            Observable.fire(Event.NEW_PV(pv=moves))
        super().pv(moves)

    def depth(self, dep):
        if self._allow_fire_depth():
            Observable.fire(Event.NEW_DEPTH(depth=dep))
        super().depth(dep)


class UciEngine(object):

    """handle the uci engine communication."""

    def __init__(self, file: str, hostname=None, username=None, key_file=None, password=None, home=''):
        super(UciEngine, self).__init__()
        try:
            self.shell = None
            if hostname:
                logging.info("connecting to [%s]", hostname)
                if key_file:
                    shell = spur.SshShell(hostname=hostname, username=username, private_key_file=key_file,
                                          missing_host_key=paramiko.AutoAddPolicy())
                else:
                    shell = spur.SshShell(hostname=hostname, username=username, password=password,
                                          missing_host_key=paramiko.AutoAddPolicy())
                self.shell = shell
                self.engine = chess.uci.spur_spawn_engine(shell, [home + os.sep + file])
            else:
                self.engine = chess.uci.popen_engine(file)

            self.file = file
            if self.engine:
                handler = Informer()
                self.engine.info_handlers.append(handler)
                self.engine.uci()
            else:
                logging.error("engine executable [%s] not found", file)
            self.options = {}
            self.future = None
            self.show_best = True

            self.res = None
            self.status = EngineStatus.WAIT
            self.level_support = False

        except OSError:
            logging.exception('OS error in starting engine')
        except TypeError:
            logging.exception('engine executable not found')

    def get(self):
        return self.engine

    def option(self, name, value):
        self.options[name] = value

    def send(self):
        self.engine.setoption(self.options)

    def level(self, options: dict):
        self.options = options

    def has_levels(self):
        return self.level_support or self.has_skill_level() or self.has_limit_strength() or self.has_strength()

    def has_skill_level(self):
        return 'Skill Level' in self.engine.options

    def has_limit_strength(self):
        return 'UCI_LimitStrength' in self.engine.options

    def has_strength(self):
        return 'Strength' in self.engine.options

    def has_chess960(self):
        return 'UCI_Chess960' in self.engine.options

    def get_file(self):
        return self.file

    def get_shell(self):
        return self.shell  # shell is only "not none" if its a local engine - see __init__

    def position(self, game: Board):
        self.engine.position(game)

    def quit(self):
        return self.engine.quit()

    def terminate(self):
        return self.engine.terminate()

    def kill(self):
        return self.engine.kill()

    def uci(self):
        self.engine.uci()

    def stop(self, show_best=False):
        if self.is_waiting():
            logging.info('engine already stopped')
            return self.res
        self.show_best = show_best
        self.engine.stop()
        return self.future.result()

    def go(self, time_dict: dict):
        if not self.is_waiting():
            logging.warning('engine (still) not waiting - strange!')
        self.status = EngineStatus.THINK
        self.show_best = True
        time_dict['async_callback'] = self.callback

        Observable.fire(Event.START_SEARCH(engine_status=self.status))
        self.future = self.engine.go(**time_dict)
        return self.future

    def ponder(self):
        if not self.is_waiting():
            logging.warning('engine (still) not waiting - strange!')
        self.status = EngineStatus.PONDER
        self.show_best = False

        Observable.fire(Event.START_SEARCH(engine_status=self.status))
        self.future = self.engine.go(ponder=True, infinite=True, async_callback=self.callback)
        return self.future

    def callback(self, command):
        self.res = command.result()

        Observable.fire(Event.STOP_SEARCH(engine_status=self.status))
        if self.show_best:
            Observable.fire(Event.BEST_MOVE(move=self.res.bestmove, ponder=self.res.ponder, inbook=False))
        else:
            logging.debug('event best_move not fired')
        self.status = EngineStatus.WAIT

    def is_thinking(self):
        return self.status == EngineStatus.THINK

    def is_pondering(self):
        return self.status == EngineStatus.PONDER

    def is_waiting(self):
        return self.status == EngineStatus.WAIT

    def startup(self, options: dict, show=True):
        parser = configparser.ConfigParser()
        parser.optionxform = str
        if not options and parser.read(self.get_file() + '.uci'):
            options = dict(parser[parser.sections().pop()])
        self.level_support = bool(options)
        if parser.read(os.path.dirname(self.get_file()) + os.sep + 'engines.uci'):
            pc_opts = dict(parser[parser.sections().pop()])
            pc_opts.update(options)
            options = pc_opts

        logging.debug("setting engine with options %s", options)
        self.level(options)
        self.send()
        if show:
            logging.debug('Loaded engine [%s]', self.get().name)
            logging.debug('Supported options [%s]', self.get().options)
