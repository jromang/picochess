#!/usr/bin/env python3

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

import os
from configobj import ConfigObj


def write_voice_ini():
    """Read the voices folder and write the result to voices.ini."""
    def get_immediate_subdirectories(a_dir):
        """Return the immediate subdirs."""
        return [name for name in os.listdir(a_dir)
                if os.path.isdir(os.path.join(a_dir, name))]

    program_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    voices_path = program_path + os.sep + 'talker' + os.sep + 'voices'
    config = ConfigObj(voices_path + os.sep + 'voices.ini', indent_type='    ')

    lang_list = get_immediate_subdirectories(voices_path)
    for lang_dir_name in lang_list:
        print(lang_dir_name)
        config[lang_dir_name] = {}
        speak_list = get_immediate_subdirectories(voices_path + os.sep + lang_dir_name)
        for speak_dir_name in speak_list:
            config[lang_dir_name][speak_dir_name] = {}
            config[lang_dir_name][speak_dir_name]['small'] = speak_dir_name[:6]
            config[lang_dir_name][speak_dir_name]['medium'] = speak_dir_name[:8].title()
            config[lang_dir_name][speak_dir_name]['large'] = speak_dir_name[:11].title()
    config.write()


write_voice_ini()
