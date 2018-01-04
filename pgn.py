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

import threading
import base64
import datetime
import logging
import os
import queue
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import mimetypes
import requests

import chess
import chess.pgn
from utilities import DisplayMsg
from dgt.api import Message
from dgt.util import GameResult, PlayMode, Mode


class Emailer(object):

    """Handle eMail with subject, body and an attached file."""

    def __init__(self, email=None, mailgun_key=None):
        if email:  # check if email address is provided by picochess.ini
            self.email = email
        else:
            self.email = False
        self.smtp_server = None
        self.smtp_encryption = None
        self.smtp_user = None
        self.smtp_pass = None
        self.smtp_from = None

        if email and mailgun_key:
            self.mailgun_key = base64.b64decode(str.encode(mailgun_key)).decode('utf-8')
        else:
            self.mailgun_key = False

    def _use_smtp(self, subject, body, path):
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
        conn = False
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
                with open(path) as fpath:
                    msg = MIMEText(fpath.read(), _subtype=subtype)
            elif maintype == 'image':
                with open(path, 'rb') as fpath:
                    msg = MIMEImage(fpath.read(), _subtype=subtype)
            elif maintype == 'audio':
                with open(path, 'rb') as fpath:
                    msg = MIMEAudio(fpath.read(), _subtype=subtype)
            else:
                with open(path, 'rb') as fpath:
                    msg = MIMEBase(maintype, subtype)
                    msg.set_payload(fpath.read())
                encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
            outer.attach(msg)

            logging.debug('SMTP Mail delivery: trying to connect to ' + self.smtp_server)
            conn = SMTP(self.smtp_server)  # contact smtp server
            conn.set_debuglevel(False)  # no debug info from smtp lib
            if self.smtp_user is not None and self.smtp_pass is not None:
                logging.debug('SMTP Mail delivery: trying to log to SMTP Server')
                conn.login(self.smtp_user, self.smtp_pass)  # login at smtp server

            logging.debug('SMTP Mail delivery: trying to send email')
            conn.sendmail(self.smtp_from, self.email, outer.as_string())
            logging.debug('SMTP Mail delivery: successfuly delivered message to SMTP server')
        except Exception as smtp_exc:
            logging.error('SMTP Mail delivery: Failed')
            logging.error('SMTP Mail delivery: ' + str(smtp_exc))
        finally:
            if conn:
                conn.close()
            logging.debug('SMTP Mail delivery: Ended')

    def _use_mailgun(self, subject, body):
        out = requests.post('https://api.mailgun.net/v3/picochess.org/messages',
                            auth=('api', self.mailgun_key),
                            data={'from': 'Your PicoChess computer <no-reply@picochess.org>',
                                  'to': self.email,
                                  'subject': subject,
                                  'text': body})
        logging.debug(out)

    def set_smtp(self, sserver=None, sencryption=None, suser=None, spass=None, sfrom=None):
        """Store information for SMTP based mail delivery."""
        self.smtp_server = sserver
        self.smtp_encryption = sencryption
        self.smtp_user = suser
        self.smtp_pass = spass
        self.smtp_from = sfrom

    def send(self, subject: str, body: str, path: str):
        """Send the email out."""
        if self.email:  # check if email adress to send the pgn to is provided
            if self.mailgun_key:  # check if we have mailgun-key available to send the pgn successful
                self._use_mailgun(subject=subject, body=body)
            if self.smtp_server:  # check if smtp server adress provided
                self._use_smtp(subject=subject, body=body, path=path)


class PgnDisplay(DisplayMsg, threading.Thread):

    """Deal with DisplayMessages related to pgn."""

    def __init__(self, file_name: str, emailer: Emailer):
        super(PgnDisplay, self).__init__()
        self.file_name = file_name
        self.emailer = emailer

        self.engine_name = '?'
        self.old_engine = '?'
        self.user_name = '?'
        self.location = '?'
        self.level_text = None
        self.level_name = ''
        self.user_elo = '-'
        self.engine_elo = '-'
        self.startime = datetime.datetime.now().strftime('%H:%M:%S')

    def _save_and_email_pgn(self, message):
        logging.debug('Saving game to [%s]', self.file_name)
        pgn_game = chess.pgn.Game().from_board(message.game)

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
            engine_level = ' ({})'.format(self.level_text.m)

        if self.level_name.startswith('Elo@'):
            comp_elo = int(self.level_name[4:])
            engine_level = ''
        else:
            comp_elo = self.engine_elo

        if message.play_mode == PlayMode.USER_WHITE:
            pgn_game.headers['White'] = self.user_name
            pgn_game.headers['Black'] = self.engine_name + engine_level
            pgn_game.headers['WhiteElo'] = self.user_elo
            pgn_game.headers['BlackElo'] = comp_elo
        if message.play_mode == PlayMode.USER_BLACK:
            pgn_game.headers['White'] = self.engine_name + engine_level
            pgn_game.headers['Black'] = self.user_name
            pgn_game.headers['WhiteElo'] = comp_elo
            pgn_game.headers['BlackElo'] = self.user_elo

        pgn_game.headers['Time'] = self.startime

        # Save to file
        file = open(self.file_name, 'a')
        exporter = chess.pgn.FileExporter(file)
        pgn_game.accept(exporter)
        file.flush()
        file.close()
        self.emailer.send('Game PGN', str(pgn_game), self.file_name)

    def _process_message(self, message):
        if False:  # switch-case
            pass

        elif isinstance(message, Message.SYSTEM_INFO):
            self.engine_name = message.info['engine_name']
            self.old_engine = self.engine_name
            self.user_name = message.info['user_name']
            self.user_elo = message.info['user_elo']

        elif isinstance(message, Message.IP_INFO):
            self.location = message.info['location']

        elif isinstance(message, Message.STARTUP_INFO):
            self.level_text = message.info['level_text']
            self.level_name = message.info['level_name']

        elif isinstance(message, Message.LEVEL):
            self.level_text = message.level_text
            self.level_name = message.level_name

        elif isinstance(message, Message.INTERACTION_MODE):
            if message.mode == Mode.REMOTE:
                self.old_engine = self.engine_name
                self.engine_name = 'Remote Player'
            else:
                self.engine_name = self.old_engine

        elif isinstance(message, Message.ENGINE_STARTUP):
            for index in range(0, len(message.installed_engines)):
                eng = message.installed_engines[index]
                if eng['file'] == message.file:
                    self.engine_elo = eng['elo']
                    break

        elif isinstance(message, Message.ENGINE_READY):
            self.old_engine = self.engine_name = message.engine_name
            self.engine_elo = message.eng['elo']
            if not message.has_levels:
                self.level_text = None
                self.level_name = ''

        elif isinstance(message, Message.GAME_ENDS):
            if message.game.move_stack:
                self._save_and_email_pgn(message)

        elif isinstance(message, Message.START_NEW_GAME):
            self.startime = datetime.datetime.now().strftime('%H:%M:%S')

        else:  # Default
            pass

    def run(self):
        """Call by threading.Thread start() function."""
        logging.info('msg_queue ready')
        while True:
            # Check if we have something to display
            try:
                message = self.msg_queue.get()
                self._process_message(message)
            except queue.Empty:
                pass
