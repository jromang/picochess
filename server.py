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
                                                       "play_mode"] == PlayMode.USER_WHITE else user_name
            game.headers["White"] = engine_name if cls.shared["game_info"][
                                                       "play_mode"] == PlayMode.USER_BLACK else user_name

            comp_color = "Black" if cls.shared["game_info"]["play_mode"] == PlayMode.USER_WHITE else "White"
            user_color = "Black" if cls.shared["game_info"]["play_mode"] == PlayMode.USER_BLACK else "White"
            game.headers[comp_color + "Elo"] = "2900"
            game.headers[user_color + "Elo"] = "-"


def update_headers(cls):
    g = pgn.Game()
    create_game_header(cls, g)
    exp = pgn.StringExporter(headers=True, comments=False, variations=False)
    pgn_str = g.accept(exp)
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
            exporter = pgn.StringExporter(headers=True, comments=False, variations=False)
            pgn_str = game.accept(exporter)
            r = {'type': 'broadcast', 'msg': 'Received position from Spectators!', 'pgn': pgn_str, 'fen': fen}
            EventHandler.write_to_clients(r)
        elif action == 'move':
            WebServer.fire(Event.REMOTE_MOVE(move=self.get_argument("source") + self.get_argument("target"), fen=self.get_argument("fen")))


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
        logging.info('evt_queue ready')
        IOLoop.instance().start()


class WebDisplay(DisplayMsg, threading.Thread):
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
        for case in switch(message):
            if case(MessageApi.BOOK_MOVE):
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'Book move'})
                break
            if case(MessageApi.START_NEW_GAME):
                EventHandler.write_to_clients({'event': 'NewGame'})
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'New game'})
                update_headers(self)
                break
            if case(MessageApi.SEARCH_STARTED):
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'Thinking..'})
                break
            if case(MessageApi.UCI_OPTION_LIST):
                self.shared['uci_options'] = message.options
                break
            if case(MessageApi.SYSTEM_INFO):
                self.shared['system_info'] = message.info
                self.shared['system_info']['old_engine'] = self.shared['system_info']['engine_name']
                update_headers(self)
                break
            if case(MessageApi.ENGINE_READY):
                self.shared['system_info']['engine_name'] = message.engine_name
                if not message.has_levels and "level" in self.shared["game_info"]:
                    del self.shared['game_info']['level']
                update_headers(self)
                break
            if case(MessageApi.STARTUP_INFO):
                self.shared['game_info'] = message.info
                break
            if case(MessageApi.OPENING_BOOK):  # Process opening book
                self.create_game_info()
                self.shared['game_info']['book_text'] = message.book_text
                break
            if case(MessageApi.INTERACTION_MODE):  # Process interaction mode
                self.create_game_info()
                self.shared['game_info']['mode'] = message.mode
                if self.shared['game_info']['mode'] == Mode.REMOTE:
                    self.shared['system_info']['engine_name'] = "Remote Player"
                else:
                    self.shared['system_info']['engine_name'] = self.shared['system_info']['old_engine']
                update_headers(self)
                break
            if case(MessageApi.PLAY_MODE):  # Process play mode
                self.create_game_info()
                self.shared['game_info']['play_mode'] = message.play_mode
                break
            if case(MessageApi.TIME_CONTROL):
                self.create_game_info()
                self.shared['game_info']['time_text'] = message.time_text
                break
            if case(MessageApi.LEVEL):
                self.shared['game_info']['level'] = message.level
                update_headers(self)
                break
            if case(MessageApi.JACK_CONNECTED_ERROR):
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'Unplug the jack cable please!'})
                break
            if case(MessageApi.NO_EBOARD_ERROR):
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'Connect an E-Board please!'})
                break
            if case(MessageApi.EBOARD_VERSION):
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'DGT board connected through ' + message.channel})
                break
            if case(MessageApi.DGT_CLOCK_VERSION):
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'DGT clock connected through ' + message.attached})
                break
            if case(MessageApi.COMPUTER_MOVE):
                game = pgn.Game()
                custom_fen = getattr(message.game, 'custom_fen', None)
                if custom_fen:
                    game.setup(custom_fen)
                create_game_header(self, game)

                tmp = game
                move_stack = message.game.move_stack
                for move in move_stack:
                    tmp = tmp.add_variation(move)
                exporter = pgn.StringExporter(headers=True, comments=False, variations=False)

                pgn_str = game.accept(exporter)
                fen = message.game.fen()
                mov = message.result.bestmove.uci()
                msg = 'Computer move: ' + str(message.result.bestmove)
                r = {'pgn': pgn_str, 'fen': fen, 'event': 'newFEN', 'move': mov, 'msg': msg, 'remote_play': False}

                self.shared['last_dgt_move_msg'] = r
                EventHandler.write_to_clients(r)
                break
            if case(MessageApi.USER_MOVE):
                game = pgn.Game()
                custom_fen = getattr(message.game, 'custom_fen', None)
                if custom_fen:
                    game.setup(custom_fen)
                create_game_header(self, game)

                tmp = game
                move_stack = message.game.move_stack
                for move in move_stack:
                    tmp = tmp.add_variation(move)
                exporter = pgn.StringExporter(headers=True, comments=False, variations=False)

                pgn_str = game.accept(exporter)
                fen = message.game.fen()
                msg = 'User move: ' + str(message.move)
                mov = message.move.uci()
                r = {'pgn': pgn_str, 'fen': fen, 'event': 'newFEN', 'move': mov, 'msg': msg, 'remote_play': False}

                self.shared['last_dgt_move_msg'] = r
                EventHandler.write_to_clients(r)
                break
            if case(MessageApi.REVIEW_MOVE):
                game = pgn.Game()
                custom_fen = getattr(message.game, 'custom_fen', None)
                if custom_fen:
                    game.setup(custom_fen)
                create_game_header(self, game)

                tmp = game
                move_stack = message.game.move_stack
                for move in move_stack:
                    tmp = tmp.add_variation(move)
                exporter = pgn.StringExporter(headers=True, comments=False, variations=False)

                pgn_str = game.accept(exporter)
                fen = message.game.fen()
                mov = 'User move: ' + str(message.move)
                r = {'pgn': pgn_str, 'fen': fen, 'event': 'newFEN', 'move': mov, 'remote_play': True}

                self.shared['last_dgt_move_msg'] = r
                EventHandler.write_to_clients(r)
                break
            if case():  # Default
                # print(message)
                pass

    def create_task(self, msg):
        IOLoop.instance().add_callback(callback=lambda: self.task(msg))

    def run(self):
        logging.info('msg_queue ready')
        while True:
            # Check if we have something to display
            message = self.msg_queue.get()
            self.create_task(message)
