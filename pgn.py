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

import threading
import base64
import chess
import chess.pgn
import logging
import requests
from utilities import *


class PgnDisplay(Display, threading.Thread):
    def __init__(self, pgn_file_name, email=None, key=None):
        super(PgnDisplay, self).__init__()
        self.file_name = pgn_file_name
        self.email = email
        if email and key:
            self.key = base64.b64decode(str.encode(key)).decode("utf-8")

    def run(self):
        while True:
            #Check if we have something to display
            try:
                message = self.message_queue.get()
                if message == Message.GAME_ENDS and message.moves:
                    logging.debug('Saving game to [' + self.file_name+']')
                    game = node = chess.pgn.Game()
                    game.headers["Result"] = "*"
                    for move in message.moves:
                        node = node.add_main_variation(move)
                    # Save to file
                    file = open(self.file_name, "a")
                    exporter = chess.pgn.FileExporter(file)
                    game.export(exporter)
                    file.close()
                    # Send email
                    if self.email:
                        out = requests.post("https://api.mailgun.net/v2/picochess.org/messages",
                                            auth=("api", self.key),
                                            data={"from": "Your PicoChess computer <no-reply@picochess.org>",
                                            "to": self.email,
                                            "subject": "Game PGN",
                                            "text": str(game)})
                        logging.debug(out)
            except queue.Empty:
                pass
