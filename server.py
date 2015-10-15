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

from flask import Flask
import tornado.web
import tornado.wsgi
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from multiprocessing.pool import ThreadPool
from utilities import *
import queue
from web.picoweb import picoweb as pw
import chess.pgn as pgn
import json
import datetime

_workers = ThreadPool(5)

# This needs to be reworked to be session based (probably by token)
# Otherwise multiple clients behind a NAT can all play as the 'player'
client_ips = []


def create_game_header(cls, game):
    game.headers["Result"] = "*"
    game.headers["White"] = "None"
    game.headers["Black"] = "None"
    game.headers["Event"] = "PicoChess game"
    game.headers["Date"] = datetime.datetime.now().date().strftime('%Y-%m-%d')
    game.headers["Round"] = "?"

    game.headers["Site"] = "picochess.org"
    user_name = "User"
    engine_name = "Picochess"
    if 'system_info' in cls.shared:
        if "location" in cls.shared['system_info']:
            game.headers["Site"] = cls.shared['system_info']['location']
        if "user_name" in cls.shared['system_info']:
            user_name = cls.shared['system_info']['user_name']
        if "engine_name" in cls.shared['system_info']:
            engine_name = cls.shared['system_info']['engine_name']

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


def update_headers(cls):
    g = pgn.Game()
    create_game_header(cls, g)
    exp = pgn.StringExporter()
    g.export(exp, headers=True, comments=False, variations=False)
    pgn_str = str(exp)
    EventHandler.write_to_clients({'event': 'header', 'header': pgn_str})


class ChannelHandler(tornado.web.RequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def real_ip(self):
        x_real_ip = self.request.headers.get("X-Real-IP")
        real_ip = self.request.remote_ip if not x_real_ip else x_real_ip
        return real_ip

    def post(self):
        action = self.get_argument("action")

        if action == 'broadcast':
            fen = self.get_argument("fen")

            move_stack = self.get_argument("moveStack")
            move_stack = json.loads(move_stack)
            game = pgn.Game()

            create_game_header(self, game)

            tmp = game
            for move in move_stack:
                tmp = tmp.add_variation(tmp.board().parse_san(move))
            exporter = pgn.StringExporter()
            game.export(exporter, headers=True, comments=False, variations=False)
            r = {'type': 'broadcast', 'msg': 'Received position from Spectators!', 'pgn': str(exporter), 'fen': fen}
            EventHandler.write_to_clients(r)
        elif action == 'move':
            WebServer.fire(Event.REMOTE_MOVE, move= (self.get_argument("source") + self.get_argument("target")), fen= self.get_argument("fen"))


class EventHandler(WebSocketHandler):
    clients = set()

    def initialize(self, shared=None):
        self.shared = shared

    def real_ip(self):
        x_real_ip = self.request.headers.get("X-Real-IP")
        real_ip = self.request.remote_ip if not x_real_ip else x_real_ip
        return real_ip

    def open(self):
        EventHandler.clients.add(self)
        client_ips.append(self.real_ip())
        update_headers(self)

    def on_close(self):
        EventHandler.clients.remove(self)
        client_ips.remove(self.real_ip())

    @classmethod
    def write_to_clients(cls, msg):
        for client in cls.clients:
            client.write_message(msg)


class DGTHandler(tornado.web.RequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self, *args, **kwargs):
        action = self.get_argument("action")
        if action == "get_last_move":
            self.write(self.shared['last_dgt_move_msg'])


class InfoHandler(tornado.web.RequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self, *args, **kwargs):
        action = self.get_argument("action")
        if action == "get_system_info":
            if 'system_info' in self.shared:
                self.write(self.shared['system_info'])


class PGNHandler(tornado.web.RequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self, *args, **kwargs):
        action = self.get_argument("action")
        if action == "get_pgn_file":
            self.set_header('Content-Type', 'text/pgn')
            self.set_header('Content-Disposition', 'attachment; filename=game.pgn')
            self.write(self.shared['last_dgt_move_msg']['pgn'])


class WebServer(Observable, threading.Thread):
    def __init__(self, port=80):
        shared = {}

        WebDisplay(shared).start()
        super(WebServer, self).__init__()
        wsgi_app = tornado.wsgi.WSGIContainer(pw)

        application = tornado.web.Application([
            (r'/event', EventHandler, dict(shared=shared)),
            (r'/dgt', DGTHandler, dict(shared=shared)),
            (r'/pgn', PGNHandler, dict(shared=shared)),
            (r'/info', InfoHandler, dict(shared=shared)),

            (r'/channel', ChannelHandler, dict(shared=shared)),
            (r'.*', tornado.web.FallbackHandler, {'fallback': wsgi_app})
        ])
        application.listen(port)

    def run(self):
        IOLoop.instance().start()


class WebDisplay(Display, threading.Thread):
    def __init__(self, shared):
        super(WebDisplay, self).__init__()
        self.shared = shared

    @staticmethod
    def run_background(func, callback, args=(), kwds=None):
        if not kwds:
            kwds = {}

        def _callback(result):
            IOLoop.instance().add_callback(lambda: callback(result))

        _workers.apply_async(func, args, kwds, _callback)

    def create_game_info(self):
        if 'game_info' not in self.shared:
            self.shared['game_info'] = {}

    def create_system_info(self):
        if 'system_info' not in self.shared:
            self.shared['system_info'] = {}

    def task(self, message):
        if message == Message.BOOK_MOVE:
            EventHandler.write_to_clients({'event': 'Message', 'msg': 'Book move'})

        elif message == Message.START_NEW_GAME:
            EventHandler.write_to_clients({'event': 'NewGame'})
            EventHandler.write_to_clients({'event': 'Message', 'msg': 'New game'})
            update_headers(self)

        elif message == Message.SEARCH_STARTED:
            EventHandler.write_to_clients({'event': 'Message', 'msg': 'Thinking..'})

        elif message == Message.UCI_OPTION_LIST:
            self.shared['uci_options'] = message.options

        elif message == Message.SYSTEM_INFO:
            self.shared['system_info'] = message.info
            self.shared['system_info']['old_engine'] = self.shared['system_info']['engine_name']
            update_headers(self)

        elif message == Message.ENGINE_NAME:
            self.shared['system_info']['engine_name'] = message.ename
            update_headers(self)

        elif message == Message.STARTUP_INFO:
            self.shared['game_info'] = message.info

        elif message == Message.OPENING_BOOK:  # Process opening book
            self.create_game_info()
            self.shared['game_info']['book'] = message.book

        elif message == Message.INTERACTION_MODE:  # Process interaction mode
            self.create_game_info()
            self.shared['game_info']['mode'] = message.mode
            if self.shared['game_info']['mode'] == Mode.REMOTE:
                self.shared['system_info']['engine_name'] = "Remote Player"
            else:
                self.shared['system_info']['engine_name'] = self.shared['system_info']['old_engine']
            update_headers(self)

        elif message == Message.PLAY_MODE:  # Process play mode
            self.create_game_info()
            self.shared['game_info']['play_mode'] = message.play_mode

        elif message == Message.TIME_CONTROL:
            self.create_game_info()
            self.shared['game_info']['time_control_string'] = message.time_control_string

        elif message == Message.LEVEL:
            self.shared['game_info']['level'] = message.level
            update_headers(self)

        elif message == Message.COMPUTER_MOVE or message == Message.USER_MOVE or message == Message.REVIEW_MODE_MOVE:
            game = pgn.Game()
            custom_fen = getattr(message.game, 'custom_fen', None)
            if custom_fen:
                game.setup(custom_fen)
            create_game_header(self, game)

            tmp = game
            move_stack = message.game.move_stack
            for move in move_stack:
                tmp = tmp.add_variation(move)
            exporter = pgn.StringExporter()

            game.export(exporter, headers=True, comments=False, variations=False)
            fen = message.game.fen()
            pgn_str = str(exporter)
            r = {'pgn': pgn_str, 'fen': fen, 'event': "newFEN"}

            if message == Message.COMPUTER_MOVE:
                r['move'] = message.result.bestmove.uci()
                r['msg'] = 'Computer move: ' + str(message.result.bestmove)
            elif message == Message.USER_MOVE:
                r['move'] = message.move.uci()
                r['msg'] = 'User move: ' + str(message.move)

            if message == Message.REMOTE_MODE_MOVE:
                r['move'] = 'User move: ' + str(message.move)
                r['remote_play'] = True

            self.shared['last_dgt_move_msg'] = r
            EventHandler.write_to_clients(r)

    def create_task(self, msg):
        IOLoop.instance().add_callback(callback=lambda: self.task(msg))

    def run(self):
        while True:
            # Check if we have something to display
            message = self.message_queue.get()
            self.create_task(message)
