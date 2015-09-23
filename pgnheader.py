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
import datetime

def create_game_header(cls, game):
    game.headers["Result"] = "*"
    game.headers["White"] = "None"
    game.headers["Black"] = "None"
    game.headers["Event"] = "PicoChess game"
    game.headers["Date"] = datetime.datetime.now().date().strftime('%Y-%m-%d')
    game.headers["Round"] = "?"

    if 'system_info' in cls.shared:
        if "location" in cls.shared['system_info']:
            game.headers["Site"] = cls.shared['system_info']['location']
        if "user_name" in cls.shared['system_info']:
            user_name = cls.shared['system_info']['user_name']
        if "engine_name" in cls.shared['system_info']:
            engine_name = cls.shared['system_info']['engine_name']
    else:
        game.headers["Site"] = "picochess.org"
        user_name = "User"
        engine_name = "Picochess"

    if 'game_info' in cls.shared:
        if "play_mode" in cls.shared["game_info"]:
            if "level" in cls.shared["game_info"]:
                engine_name += " (Level {0})".format(cls.shared["game_info"]["level"])
            game.headers["Black"] = engine_name if cls.shared["game_info"][
                                                       "play_mode"] == PlayMode.PLAY_WHITE else user_name
            game.headers["White"] = engine_name if cls.shared["game_info"][
                                                       "play_mode"] == PlayMode.PLAY_BLACK else user_name

            comp_color = "Black" if cls.shared["game_info"]["play_mode"] == PlayMode.PLAY_WHITE else "White"
            user_color = "Black" if cls.shared["game_info"]["play_mode"] == PlayMode.PLAY_BLACK else "White"
            game.headers[comp_color + "Elo"] = "2900"
            game.headers[user_color + "Elo"] = "-"

    # http://www6.chessclub.com/help/PGN-spec saying: not valid!
    # must be set in TimeControl-tag and with other format anyway
    # if "time_control_string" in self.shared["game_info"]:
    #    game.headers["Event"] = "Time " + self.shared["game_info"]["time_control_string"]



