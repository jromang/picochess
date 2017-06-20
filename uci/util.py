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

import platform
import configparser
import os
from dgt.api import Dgt
from uci.engine import UciEngine


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
                program_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
                engine_path = program_path + os.sep + 'engines' + os.sep + platform.machine()
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
                    parser['Elo@{:04d}'.format(level)] = {'UCI_LimitStrength': 'true', 'UCI_Elo': str(level)}
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
        program_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        engine_path = program_path + os.sep + 'engines' + os.sep + platform.machine()
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
