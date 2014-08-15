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
# import web
from web.picoweb import picoweb as pw

_workers = ThreadPool(5)

class EventHandler(WebSocketHandler):
    clients = set()
    # @staticmethod
    # def echo_now():
    #     for client in NowHandler.clients:
    #         client.write_message(time.ctime())

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
        # app = Flask(pw)
        #
        # @app.route('/')
        # def index():
        #     return """
        # <span id="now">loading<span>
        # <script type="text/javascript">
        # window.WebSocket=window.WebSocket || window.MozWebSocket || false;
        # if(!window.WebSocket){
        #     alert("No WebSocket Support");
        # }else {
        #     var ws=new WebSocket("ws://"+location.host+"/event");
        #     var now_el=document.getElementById("now");
        #     ws.onmessage=function(e){
        #         now_el.innerHTML=e.data;
        #     }
        #     ws.onclose=function(){
        #         now_el.innerHTML='closed';
        #     }
        #
        # }
        # </script>
        # """
        wsgi_app = tornado.wsgi.WSGIContainer(pw)
        application = tornado.web.Application([
            (r'/event', EventHandler),
            (r'.*', tornado.web.FallbackHandler, {'fallback': wsgi_app})
        ])
        # picoweb.run(debug=True)
        # PeriodicCallback(NowHandler.echo_now, 1000).start()

        application.listen(5000)
        # IOLoop.instance().start()

    def run(self):
        IOLoop.instance().start()


class WebDisplay(Display, threading.Thread):
    def __init__(self):
        super(WebDisplay, self).__init__()

    # def on_complete(self, res):
    #     # self.write("Test {0}<br/>".format(res))
    #     self.finish()

    @staticmethod
    def run_background(func, callback, args=(), kwds = None):
        if not kwds:
            kwds = {}

        def _callback(result):
            IOLoop.instance().add_callback(lambda: callback(result))

        _workers.apply_async(func, args, kwds, _callback)

    def task(self, message):
        if message == Message.BOOK_MOVE:
            EventHandler.write_to_clients({'msg': 'Book move'})
        elif message == Message.COMPUTER_MOVE:
            # print('\n' + str(message.game))
            # print('Computer move : ' + message.move)
            # for m in message.game:
            #     print (m)
            # print(str(message.game.fen()))
            EventHandler.write_to_clients({'msg': 'Computer move: '+message.move, 'move': message.move, 'fen': message.game.fen()})

        elif message == Message.START_NEW_GAME:
            # print('New game')
            # NowHandler.write_to_clients('New game')
            # NowHandler.write_to_clients({'msg': 'Computer move', 'move': message.move, 'fen':message.game.fen()})
            EventHandler.write_to_clients({'msg': 'New game'})

        elif message == Message.SEARCH_STARTED:
            # print('Computer is thinking...')
            EventHandler.write_to_clients({'msg': 'New game'})
        # else:
        #     print ('Message %s' % message)
        #     print ('Message_fen %s' % message.game.fen())


    def create_task(self, msg):
        IOLoop.instance().add_callback(callback=lambda: self.task(msg))

    def run(self):
        while True:
            #Check if we have something to display
            try:
                message = self.message_queue.get()
                self.create_task(message)

                # self.run_background(self.blocking_task, self.on_complete, (message,))


                # if message == Message.BOOK_MOVE:
                #     print('Book move')
                # elif message == Message.COMPUTER_MOVE:
                #     print('\n' + str(message.game))
                #     print('Computer move : ' + message.move)
                # elif message == Message.START_NEW_GAME:
                #     print('New game')
                # elif message == Message.SEARCH_STARTED:
                #     print('Computer is thinking...')
            except queue.Empty:
                pass