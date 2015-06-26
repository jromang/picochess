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

class ChannelHandler(tornado.web.RequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def post(self):
        action = self.get_argument("action")
        # print("action: {0}".format(action))
        # $.post("/channel", { action: "broadcast", fen: currentPosition.fen, pgn: pgnEl[0].innerText}, function (data) {
        if action == 'broadcast':
            fen = self.get_argument("fen")
            # print("fen: {0}".format(fen))

            move_stack = self.get_argument("moveStack")
            move_stack = json.loads(move_stack)
            game = pgn.Game()

            self.create_game_header(game)

            tmp = game
            # move_stack = message.game.move_stack
            for move in move_stack:
                tmp = tmp.add_variation(tmp.board().parse_san(move))

            # print (message.game.move_stack)
            exporter = pgn.StringExporter()
            game.export(exporter, headers=True, comments=False, variations=False)
            # print ("PGN: ")
            # print (str(exporter))
            # r = {'move': str(message.move), , 'fen': message.game.fen()}

            # print("pgn: {0}".format(pgn))

            r = {'type': 'broadcast', 'msg': 'Received position from Spectators!', 'pgn': str(exporter), 'fen':fen}
            EventHandler.write_to_clients(r)

        # if action == 'pause_cloud_engine':

class EventHandler(WebSocketHandler):
    clients = set()

    def initialize(self, shared=None):
        self.shared = shared

    def open(self):
        EventHandler.clients.add(self)

    def on_close(self):
        EventHandler.clients.remove(self)

    @classmethod
    def write_to_clients(cls, msg):
        # print "Writing to clients"
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
            # print(self.shared['system_info'])
            if 'system_info' in self.shared:
                self.write(self.shared['system_info'])


class PGNHandler(tornado.web.RequestHandler):
    def initialize(self, shared=None):
        self.shared = shared
    def get(self, *args, **kwargs):
        action = self.get_argument("action")
        # print (action)
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
    def run_background(func, callback, args=(), kwds = None):
        if not kwds:
            kwds = {}

        def _callback(result):
            IOLoop.instance().add_callback(lambda: callback(result))

        _workers.apply_async(func, args, kwds, _callback)

    def create_game_header(self, game):
        game.headers["Result"] = "*"
        game.headers["White"] = "None"
        game.headers["Black"] = "None"
        game.headers["Event"] = "PicoChess game"
        game.headers["Date"] = datetime.datetime.now().date().strftime('%Y-%m-%d')
        game.headers["Round"] = "?"

        if 'system_info' in self.shared:
            game.headers["Site"] = self.shared['system_info']['location']
            user_name = self.shared['system_info']['user_name']
            engine_name = self.shared['system_info']['engine_name']
        else:
            game.headers["Site"] = "picochess.org"
            user_name = "User"
            engine_name = "Picochess"

        if 'game_info' in self.shared:
            if "play_mode" in self.shared["game_info"]:
                game.headers["Black"] = engine_name if self.shared["game_info"]["play_mode"] == PlayMode.PLAY_WHITE else user_name
                game.headers["White"] = engine_name if self.shared["game_info"]["play_mode"] == PlayMode.PLAY_BLACK else user_name

                comp_color = "Black" if self.shared["game_info"]["play_mode"] == PlayMode.PLAY_WHITE else "White"
                user_color = "Black" if self.shared["game_info"]["play_mode"] == PlayMode.PLAY_BLACK else "White"
                if "level" in self.shared["game_info"]:
                    game.headers[comp_color+"Elo"] = "Level {0}".format(self.shared["game_info"]["level"])
                    game.headers[user_color+"Elo"] = "-"
                else:
                    game.headers[comp_color+"Elo"] = "2900"
                    game.headers[user_color+"Elo"] = "-"

            # http://www6.chessclub.com/help/PGN-spec saying: not valid!
            # must be set in TimeControl-tag and with other format anyway
            # if "time_control_string" in self.shared["game_info"]:
            #    game.headers["Event"] = "Time " + self.shared["game_info"]["time_control_string"]

    # @staticmethod
    def create_game_info(self):
        if 'game_info' not in self.shared:
            self.shared['game_info'] = {}

    def task(self, message):
        if message == Message.BOOK_MOVE:
            EventHandler.write_to_clients({'msg': 'Book move'})

        elif message == Message.START_NEW_GAME:
            EventHandler.write_to_clients({'msg': 'New game'})

        elif message == Message.SEARCH_STARTED:
            EventHandler.write_to_clients({'msg': 'Thinking..'})

        elif message == Message.UCI_OPTION_LIST:
            self.shared['uci_options'] = message.options

        elif message == Message.STARTUP_INFO:
            self.shared['game_info'] = message.info

        elif message == Message.SYSTEM_INFO:
            self.shared['system_info'] = message.info

        elif message == Message.OPENING_BOOK:  # Process opening book
            self.create_game_info()
            self.shared['game_info']['book'] = message.book

        elif message == Message.INTERACTION_MODE:  # Process interaction mode
            self.create_game_info()
            self.shared['game_info']['mode'] = message.mode

        elif message == Message.PLAY_MODE:  # Process play mode
            self.create_game_info()
            self.shared['game_info']['play_mode'] = message.play_mode

        elif message == Message.TIME_CONTROL:
            self.create_game_info()
            self.shared['game_info']['time_control_string'] = message.time_control_string

        elif message == Message.LEVEL:
            self.create_game_info()
            self.shared['game_info']['level'] = message.level

        elif message == Message.COMPUTER_MOVE or message == Message.USER_MOVE or message == Message.REVIEW_MODE_MOVE:
            game = pgn.Game()
            custom_fen = getattr(message.game, 'custom_fen', None)
            if custom_fen:
                game.setup(custom_fen)
            self.create_game_header(game)

            tmp = game
            move_stack = message.game.move_stack
            for move in move_stack:
                tmp = tmp.add_variation(move)
            exporter = pgn.StringExporter()

            game.export(exporter, headers=True, comments=False, variations=False)
            fen = message.game.fen()
            pgn_str = str(exporter)
            r = {'move': str(message.move), 'pgn': pgn_str, 'fen': fen}

            if message == Message.COMPUTER_MOVE:
                r['msg']= 'Computer move: '+str(message.move)
            elif message == Message.USER_MOVE:
                r['msg']= 'User move: '+str(message.move)

            if message == Message.REMOTE_MODE_MOVE:
                r['remote_play'] = True

            self.shared['last_dgt_move_msg'] = r
            EventHandler.write_to_clients(r)

    def create_task(self, msg):
        IOLoop.instance().add_callback(callback=lambda: self.task(msg))

    def run(self):
        while True:
            #Check if we have something to display
            message = self.message_queue.get()
            # print(message.options)
            self.create_task(message)
