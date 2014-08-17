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

_workers = ThreadPool(5)

class EventHandler(WebSocketHandler):
    clients = set()

    def open(self):
        EventHandler.clients.add(self)

    def on_close(self):
        EventHandler.clients.remove(self)

    @classmethod
    def write_to_clients(cls, msg):
        # print "Writing to clients"
        for client in cls.clients:
            client.write_message(msg)


class WebServer(Observable, threading.Thread):
    def __init__(self):
        WebDisplay().start()
        super(WebServer, self).__init__()
        wsgi_app = tornado.wsgi.WSGIContainer(pw)
        application = tornado.web.Application([
            (r'/event', EventHandler),
            (r'.*', tornado.web.FallbackHandler, {'fallback': wsgi_app})
        ])

        application.listen(5000)

    def run(self):
        IOLoop.instance().start()


class WebDisplay(Display, threading.Thread):
    def __init__(self):
        super(WebDisplay, self).__init__()

    @staticmethod
    def run_background(func, callback, args=(), kwds = None):
        if not kwds:
            kwds = {}

        def _callback(result):
            IOLoop.instance().add_callback(lambda: callback(result))

        _workers.apply_async(func, args, kwds, _callback)

    @staticmethod
    def task(message):
        if message == Message.BOOK_MOVE:
            EventHandler.write_to_clients({'msg': 'Book move'})
        elif message == Message.COMPUTER_MOVE:
            EventHandler.write_to_clients({'msg': 'Computer move: '+message.move, 'move': message.move, 'fen': message.game.fen()})

        elif message == Message.START_NEW_GAME:
            EventHandler.write_to_clients({'msg': 'New game'})

        elif message == Message.SEARCH_STARTED:
            EventHandler.write_to_clients({'msg': 'Thinking..'})

        elif message == Message.USER_MOVE:
            # print (message.game.move_stack)
            # exporter = pgn.StringExporter()
            # message.game.export(exporter, headers=False, comments=False, variations=False)
            EventHandler.write_to_clients({'msg': 'User move: '+str(message.move), 'move': str(message.move), 'fen': message.game.fen()})


    def create_task(self, msg):
        IOLoop.instance().add_callback(callback=lambda: self.task(msg))

    def run(self):
        while True:
            #Check if we have something to display
            try:
                message = self.message_queue.get()
                self.create_task(message)
            except queue.Empty:
                pass