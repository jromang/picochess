# Copyright (C) 2013-2016 Jean-Francois Romang (jromang@posteo.de)
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

import threading
import base64
import chess
import chess.pgn
import datetime
import logging
import requests
from utilities import *

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import mimetypes


class Emailer(object):
    def __init__(self, net, email=None, mailgun_key=None,
                 smtp_server=None, smtp_user=None,
                 smtp_pass=None, smtp_encryption=False, smtp_from=None):
        if email and net:  # check if email address is provided by picochess.ini and network traffic is allowed
            self.email = email
        else:
            self.email = False
        # store information for SMTP based mail delivery
        self.smtp_server = smtp_server
        self.smtp_encryption = smtp_encryption
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        # store information for mailgun mail delivery
        if email and mailgun_key:
            self.mailgun_key = base64.b64decode(str.encode(mailgun_key)).decode('utf-8')
        else:
            self.mailgun_key = False
        self.smtp_from = smtp_from

    def send(self, subject, body, path):
        if self.email:  # check if email adress to send the pgn to is provided
            if self.mailgun_key:  # check if we have mailgun-key available to send the pgn successful
                out = requests.post('https://api.mailgun.net/v3/picochess.org/messages',
                                    auth=('api', self.mailgun_key),
                                    data={'from': 'Your PicoChess computer <no-reply@picochess.org>',
                                          'to': self.email,
                                          'subject': subject,
                                          'text': body})
                logging.debug(out)
            if self.smtp_server:  # check if smtp server adress provided
                # if self.smtp_server is not provided than don't try to send email via smtp service
                logging.debug('SMTP Mail delivery: Started')
                # change to smtp based mail delivery
                # depending on encrypted mail delivery, we need to import the right lib
                if self.smtp_encryption:
                    # lib with ssl encryption
                    logging.debug('SMTP Mail delivery: Import SSL SMTP Lib')
                    from smtplib import SMTP_SSL as SMTP
                else:
                    # lib without encryption (SMTP-port 21)
                    logging.debug('SMTP Mail delivery: Import standard SMTP Lib (no SSL encryption)')
                    from smtplib import SMTP
                try:
                    outer = MIMEMultipart()
                    outer['Subject'] = subject  # put subject to mail
                    outer['From'] = 'Your PicoChess computer <{}>'.format(self.smtp_from)
                    outer['To'] = self.email
                    outer.attach(MIMEText(body, 'plain'))  # pack the pgn to Email body

                    ctype, encoding = mimetypes.guess_type(path)
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    if maintype == 'text':
                        with open(path) as fp:
                            msg = MIMEText(fp.read(), _subtype=subtype)
                    elif maintype == 'image':
                        with open(path, 'rb') as fp:
                            msg = MIMEImage(fp.read(), _subtype=subtype)
                    elif maintype == 'audio':
                        with open(path, 'rb') as fp:
                            msg = MIMEAudio(fp.read(), _subtype=subtype)
                    else:
                        with open(path, 'rb') as fp:
                            msg = MIMEBase(maintype, subtype)
                            msg.set_payload(fp.read())
                        encoders.encode_base64(msg)
                    msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
                    outer.attach(msg)

                    logging.debug('SMTP Mail delivery: trying to connect to ' + self.smtp_server)
                    conn = SMTP(self.smtp_server)  # contact smtp server
                    conn.set_debuglevel(False)  # no debug info from smtp lib
                    logging.debug('SMTP Mail delivery: trying to log to SMTP Server')
                    conn.login(self.smtp_user, self.smtp_pass)  # login at smtp server
                    try:
                        logging.debug('SMTP Mail delivery: trying to send email')
                        conn.sendmail(self.smtp_from, self.email, outer.as_string())
                        # @todo should check the result from sendmail
                        logging.debug('SMTP Mail delivery: successfuly delivered message to SMTP server')
                    except Exception as e:
                        logging.error('SMTP Mail delivery: Failed')
                        logging.error('SMTP Mail delivery: ' + str(e))
                    finally:
                        conn.close()
                        logging.debug('SMTP Mail delivery: Ended')
                except Exception as e:
                    logging.error('SMTP Mail delivery: Failed')
                    logging.error('SMTP Mail delivery: ' + str(e))


class PgnDisplay(DisplayMsg, threading.Thread):
    def __init__(self, file_name, emailer):
        super(PgnDisplay, self).__init__()
        self.file_name = file_name
        self.emailer = emailer

        self.engine_name = ''
        self.old_engine = ''
        self.user_name = ''
        self.location = ''
        self.level_text = None

    def save_and_email_pgn(self, message):
        logging.debug('Saving game to [' + self.file_name + ']')
        pgn_game = chess.pgn.Game().from_board(message.game.copy())

        # Headers
        pgn_game.headers['Event'] = 'PicoChess game'
        pgn_game.headers['Site'] = self.location
        pgn_game.headers['Date'] = datetime.date.today().strftime('%Y.%m.%d')

        if message.result == GameResult.DRAW:
            pgn_game.headers['Result'] = '1/2-1/2'
        elif message.result in (GameResult.WIN_WHITE, GameResult.WIN_BLACK):
            pgn_game.headers['Result'] = '1-0' if message.result == GameResult.WIN_WHITE else '0-1'
        elif message.result == GameResult.OUT_OF_TIME:
            pgn_game.headers['Result'] = '0-1' if message.game.turn == chess.WHITE else '1-0'

        if self.level_text is None:
            engine_level = ''
        else:
            engine_level = " ({})".format(self.level_text.m)

        if message.play_mode == PlayMode.USER_WHITE:
            pgn_game.headers['White'] = self.user_name
            pgn_game.headers['Black'] = self.engine_name + engine_level
            pgn_game.headers['WhiteElo'] = '-'
            pgn_game.headers['BlackElo'] = '2900'
        if message.play_mode == PlayMode.USER_BLACK:
            pgn_game.headers['White'] = self.engine_name + engine_level
            pgn_game.headers['Black'] = self.user_name
            pgn_game.headers['WhiteElo'] = '2900'
            pgn_game.headers['BlackElo'] = '-'

        # Save to file
        file = open(self.file_name, 'a')
        exporter = chess.pgn.FileExporter(file)
        pgn_game.accept(exporter)
        file.flush()
        file.close()
        self.emailer.send('Game PGN', str(pgn_game), self.file_name)

    def run(self):
        logging.info('msg_queue ready')
        while True:
            # Check if we have something to display
            try:
                message = self.msg_queue.get()
                for case in switch(message):
                    if case(MessageApi.SYSTEM_INFO):
                        self.engine_name = message.info['engine_name']
                        self.old_engine = self.engine_name
                        self.user_name = message.info['user_name']
                        self.location = message.info['location']
                        break
                    if case(MessageApi.STARTUP_INFO):
                        self.level_text = message.info['level_text']
                        break
                    if case(MessageApi.LEVEL):
                        self.level_text = message.level_text
                        break
                    if case(MessageApi.INTERACTION_MODE):
                        if message.mode == Mode.REMOTE:
                            self.old_engine = self.engine_name
                            self.engine_name = 'Remote Player'
                        else:
                            self.engine_name = self.old_engine
                        break
                    if case(MessageApi.ENGINE_READY):
                        self.engine_name = message.engine_name
                        if not message.has_levels:
                            self.level_text = None
                        break
                    if case(MessageApi.GAME_ENDS):
                        if message.game.move_stack:
                            self.save_and_email_pgn(message)
                        break
                    if case():  # Default
                        # print(message)
                        pass
            except queue.Empty:
                pass
