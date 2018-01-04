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

import platform
import configparser
import os
from uci.engine import UciShell, UciEngine


def write_engine_ini(engine_path=None):
    """Read the engine folder and create the engine.ini file."""
    def write_level_ini(engine_filename: str):
        """Write the level part for the engine.ini file."""
        def calc_inc(diflevel: int):
            """Calculate the increment for (max 20) levels."""
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
            options = engine.get_options()
            if engine.has_limit_strength():
                uelevel = options['UCI_Elo']
                minelo = uelevel.min
                maxelo = uelevel.max
                minlevel, maxlevel = min(minelo, maxelo), max(minelo, maxelo)
                lvl_inc = calc_inc(maxlevel - minlevel)
                level = minlevel
                while level < maxlevel:
                    parser['Elo@{:04d}'.format(level)] = {'UCI_LimitStrength': 'true', 'UCI_Elo': str(level)}
                    level += lvl_inc
                parser['Elo@{:04d}'.format(maxlevel)] = {'UCI_LimitStrength': 'false', 'UCI_Elo': str(maxlevel)}
            if engine.has_skill_level():
                sklevel = options['Skill Level']
                minlevel = sklevel.min
                maxlevel = sklevel.max
                minlevel, maxlevel = min(minlevel, maxlevel), max(minlevel, maxlevel)
                for level in range(minlevel, maxlevel + 1):
                    parser['Level@{:02d}'.format(level)] = {'Skill Level': str(level)}
            if engine.has_handicap_level():
                sklevel = options['Handicap Level']
                minlevel = sklevel.min
                maxlevel = sklevel.max
                minlevel, maxlevel = min(minlevel, maxlevel), max(minlevel, maxlevel)
                for level in range(minlevel, maxlevel + 1):
                    parser['Level@{:02d}'.format(level)] = {'Handicap Level': str(level)}
            if engine.has_strength():
                sklevel = options['Strength']
                minlevel = sklevel.min
                maxlevel = sklevel.max
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
        """Check if fpath is an executable."""
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    def name_build(parts: list, maxlength: int, default_name: str):
        """Get a (clever formed) cut name for the part list."""
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
    uci_shell = UciShell()
    for engine_file_name in engine_list:
        if is_exe(engine_path + os.sep + engine_file_name):
            engine = UciEngine(file=engine_path + os.sep + engine_file_name, uci_shell=uci_shell)
            if engine:
                print(engine_file_name)
                try:
                    if engine.has_levels():
                        write_level_ini(engine_file_name)
                    engine_name = engine.get_name()

                    name_parts = engine_name.replace('.', '').split(' ')
                    name_small = name_build(name_parts, 6, engine_file_name[2:])
                    name_medium = name_build(name_parts, 8, name_small)
                    name_large = name_build(name_parts, 11, name_medium)

                    config[engine_file_name] = {}

                    # config[engine_file_name][';available options'] = 'itsDefaultValue'
                    engine_options = engine.get_options()
                    for option in engine_options:
                        config[engine_file_name][str(';' + option)] = str(engine_options[option].default)

                    comp_elo = 2500
                    engine_elo = {'stockfish': 3360, 'texel': 3050, 'rodent': 2920,
                                  'zurichess': 2790, 'wyld': 2630, 'sayuri': 1850}
                    for name, elo in engine_elo.items():
                        if engine_name.lower().startswith(name):
                            comp_elo = elo
                            break

                    config[engine_file_name]['name'] = engine_name
                    config[engine_file_name]['small'] = name_small
                    config[engine_file_name]['medium'] = name_medium
                    config[engine_file_name]['large'] = name_large
                    config[engine_file_name]['elo'] = str(comp_elo)

                except AttributeError:
                    pass
                engine.quit()
    with open(engine_path + os.sep + 'engines.ini', 'w') as configfile:
        config.write(configfile)
