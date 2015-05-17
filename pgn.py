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
import datetime
import logging
import requests
from utilities import *
import sys
import os
import re
from email.mime.text import MIMEText


class PgnDisplay(Display, threading.Thread):
    def __init__(self, pgn_file_name, email=None, 
                    fromIniSmtp_Server=None, fromINISmtp_User=None,
                    fromINISmtp_Pass=None, fromINISmtp_Enc=False):
        super(PgnDisplay, self).__init__()
        self.file_name = pgn_file_name
        # store information for SMTP based Mail delivery
        self.email = email
        self.smtp_server = fromIniSmtp_Server
        self.smtp_encryption = fromINISmtp_Enc
        self.smtp_user = fromINISmtp_User
        self.smtp_pass = fromINISmtp_Pass

    def run(self):
        while True:
            #Check if we have something to display
            try:
                message = self.message_queue.get()
                if message == Message.GAME_ENDS and message.moves:
                    logging.debug('Saving game to [' + self.file_name+']')
                    game = node = chess.pgn.Game()
                    for move in message.moves:
                        node = node.add_main_variation(move)
                    # Headers
                    game.headers["Event"] = 'PicoChess game'
                    game.headers["Site"] = get_location()
                    game.headers["Date"] = datetime.date.today().strftime('%Y.%m.%d')
                    if message.result == GameResult.ABORT:
                        game.headers["Result"] = "*"
                    elif message.result in (GameResult.STALEMATE, GameResult.SEVENTYFIVE_MOVES, GameResult.FIVEFOLD_REPETITION):
                        game.headers["Result"] = "1/2-1/2"
                    elif message.result in (GameResult.MATE, GameResult.TIME_CONTROL):
                        game.headers["Result"] = "0-1" if message.color == chess.WHITE else "1-0"
                    if message.mode == Mode.PLAY_WHITE:
                        game.headers["White"] = self.email.split('@')[0] if self.email else 'Player'
                        game.headers["Black"] = "PicoChess"
                    if message.mode == Mode.PLAY_BLACK:
                        game.headers["White"] = "PicoChess"
                        game.headers["Black"] = self.email.split('@')[0] if self.email else 'Player'
                    # Save to file
                    if message.result != GameResult.ABORT:
                        file = open(self.file_name, "a")
                        exporter = chess.pgn.FileExporter(file)
                        game.export(exporter)
                        file.close()
                    # Send email
                    if self.email:

                        if self.smtp_server: # check if smtp server adress provided
                            logging.debug("SMTP Mail delivery: Started")
                            # change to smtp based mail delivery
                            # depending on encrypted mail delivery, we need to import the right lib
                            if self.smtp_encryption:
                                # lib with ssl encryption
                                logging.debug("SMTP Mail delivery: Import SSL SMTP Lib")
                                from smtplib import SMTP_SSL as SMTP
                            else: 
                                # lib without encryption (SMTP-port 21)
                                logging.debug("SMTP Mail delivery: Import standard SMTP Lib (no SSL encryption)")
                                from smtplib import SMTP
                            try:
                                msg = MIMEText(str(game), 'plain')  # pack the game to Email body
                                msg['Subject']= "Game PGN"          # put subject to mail
                                msg['From'] = "Your PicoChess computer <no-reply@picochess.org>"
                                logging.debug("SMTP Mail delivery: trying to connect to " + self.smtp_server)
                                conn = SMTP(self.smtp_server)       # contact smtp server
                                conn.set_debuglevel(False)          # no debug info from smtp lib
                                logging.debug("SMTP Mail delivery: trying to log to SMTP Server")
                                logging.debug("SMTP Mail delivery: Username=" + self.smtp_user + ", Pass=" + self.smtp_pass)
                                conn.login(self.smtp_user, self.smtp_pass) # login at smtp server
                                try:
                                    logging.debug("SMTP Mail delivery: trying to send email")
                                    conn.sendmail('no-reply@picochess.org', self.email, msg.as_string())
                                    logging.debug("SMTP Mail delivery: successfuly delivered message to SMTP server")
                                except Exception as exec:
                                    logging.error("SMTP Mail delivery: Failed")
                                    logging.error("SMTP Mail delivery: " + str(exec))
                                finally:
                                    conn.close()
                                    logging.debug("SMTP Mail delivery: Ended")
                            except Exception as exec:
                                logging.error("SMTP Mail delivery: Failed")
                                logging.error("SMTP Mail delivery: " + str(exec))
                        # smtp based system end
            except queue.Empty:
                pass
