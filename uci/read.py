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
from dgt.api import Dgt


def read_engine_ini(engine_shell=None, engine_path=None):
    """Read engine.ini and creates a library list out of it."""
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
        if engine_shell is None:
            success = parser.read(engine_path + os.sep + section + '.uci')
        else:
            try:
                with engine_shell.open(engine_path + os.sep + section + '.uci', 'r') as file:
                    parser.read_file(file)
                success = True
            except FileNotFoundError:
                success = False
        if success:
            for p_section in parser.sections():
                level_dict[p_section] = {}
                for option in parser.options(p_section):
                    level_dict[p_section][option] = parser[p_section][option]

        confsect = config[section]
        text = Dgt.DISPLAY_TEXT(l=confsect['large'], m=confsect['medium'], s=confsect['small'], wait=True, beep=False,
                                maxtime=0, devs={'ser', 'i2c', 'web'})
        library.append(
            {
                'file': engine_path + os.sep + section,
                'level_dict': level_dict,
                'text': text,
                'name': confsect['name'],
                'elo': confsect['elo']
            }
        )
    return library
