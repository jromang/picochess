#!/usr/bin/env python


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

            WebDisplay.create_game_header(game)

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
    def __init__(self):
        shared = {}

        WebDisplay(shared).start()
        super(WebServer, self).__init__()
        wsgi_app = tornado.wsgi.WSGIContainer(pw)

        application = tornado.web.Application([
            (r'/event', EventHandler, dict(shared=shared)),
            (r'/dgt', DGTHandler, dict(shared=shared)),
            (r'/pgn', PGNHandler, dict(shared=shared)),

            (r'/channel', ChannelHandler, dict(shared=shared)),
            (r'.*', tornado.web.FallbackHandler, {'fallback': wsgi_app})
        ])

        application.listen(80)

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

    @staticmethod
    def create_game_header(game):
        game.headers["Result"] = "*"
        game.headers["White"] = "User"
        game.headers["WhiteElo"] = "*"
        game.headers["BlackElo"] = "2900"
        game.headers["Black"] = "Picochess"
        game.headers["Event"] = "Game"
        game.headers["Site"] = "Pi"
        game.headers["EventDate"] = "*"

    # @staticmethod
    def task(self, message):
        if message == Message.BOOK_MOVE:
            EventHandler.write_to_clients({'msg': 'Book move'})

        elif message == Message.START_NEW_GAME:
            EventHandler.write_to_clients({'msg': 'New game'})

        elif message == Message.SEARCH_STARTED:
            EventHandler.write_to_clients({'msg': 'Thinking..'})

        elif message == Message.COMPUTER_MOVE or message == Message.USER_MOVE or message == Message.REVIEW_MODE_MOVE:
            game = pgn.Game()
            WebDisplay.create_game_header(game)

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

            self.shared['last_dgt_move_msg'] = r
            EventHandler.write_to_clients(r)

    def create_task(self, msg):
        IOLoop.instance().add_callback(callback=lambda: self.task(msg))

    def run(self):
        while True:
            #Check if we have something to display
            message = self.message_queue.get()
            self.create_task(message)
