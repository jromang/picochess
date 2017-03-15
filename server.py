# Copyright (C) 2013-2017 Jean-Francois Romang (jromang@posteo.de)
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

import datetime
import threading
from multiprocessing.pool import ThreadPool

import chess
import chess.pgn as pgn
import tornado.web
import tornado.wsgi
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from utilities import Observable, DisplayMsg, DisplayDgt, switch
import logging
from dgtapi import MessageApi, Event, DgtApi
from dgtutil import GameResult, PlayMode, Mode
from web.picoweb import picoweb as pw


_workers = ThreadPool(5)

# This needs to be reworked to be session based (probably by token)
# Otherwise multiple clients behind a NAT can all play as the 'player'
client_ips = []


class ServerRequestHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass


class ChannelHandler(ServerRequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def post(self):
        action = self.get_argument('action')

        if action == 'broadcast':
            fen = self.get_argument('fen')
            pgn_str = self.get_argument('pgn')
            result = {'event': 'broadcast', 'msg': 'Received position from Spectators!', 'pgn': pgn_str, 'fen': fen}
            EventHandler.write_to_clients(result)
        elif action == 'move':
            uci_move = self.get_argument('source') + self.get_argument('target')
            WebServer.fire(Event.REMOTE_MOVE(uci_move=uci_move, fen=self.get_argument('fen')))


class EventHandler(WebSocketHandler):
    clients = set()

    def initialize(self, shared=None):
        self.shared = shared

    def on_message(self, message):
        pass

    def data_received(self, chunk):
        pass

    def real_ip(self):
        x_real_ip = self.request.headers.get('X-Real-IP')
        real_ip = self.request.remote_ip if not x_real_ip else x_real_ip
        return real_ip

    def open(self):
        EventHandler.clients.add(self)
        client_ips.append(self.real_ip())

    def on_close(self):
        EventHandler.clients.remove(self)
        client_ips.remove(self.real_ip())

    @classmethod
    def write_to_clients(cls, msg):
        for client in cls.clients:
            client.write_message(msg)


class DGTHandler(ServerRequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self, *args, **kwargs):
        action = self.get_argument('action')
        if action == 'get_last_move':
            if 'last_dgt_move_msg' in self.shared:
                self.write(self.shared['last_dgt_move_msg'])


class InfoHandler(ServerRequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self, *args, **kwargs):
        action = self.get_argument('action')
        if action == 'get_system_info':
            if 'system_info' in self.shared:
                self.write(self.shared['system_info'])
        if action == 'get_ip_info':
            if 'ip_info' in self.shared:
                self.write(self.shared['ip_info'])
        if action == 'get_headers':
            if 'headers' in self.shared:
                self.write(self.shared['headers'])


class ChessBoardHandler(ServerRequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def get(self):
        self.render('web/picoweb/templates/clock.html')


class WebServer(Observable, threading.Thread):
    def __init__(self, port=80):
        shared = {}

        WebDisplay(shared).start()
        WebDgt(shared).start()
        super(WebServer, self).__init__()
        wsgi_app = tornado.wsgi.WSGIContainer(pw)

        application = tornado.web.Application([
            (r'/', ChessBoardHandler, dict(shared=shared)),
            (r'/event', EventHandler, dict(shared=shared)),
            (r'/dgt', DGTHandler, dict(shared=shared)),
            (r'/info', InfoHandler, dict(shared=shared)),

            (r'/channel', ChannelHandler, dict(shared=shared)),
            (r'.*', tornado.web.FallbackHandler, {'fallback': wsgi_app})
        ])
        application.listen(port)

    def run(self):
        """called from threading.Thread by its start() function."""
        logging.info('evt_queue ready')
        IOLoop.instance().start()


class WebDgt(DisplayDgt, threading.Thread):
    def __init__(self, shared):
        super(WebDgt, self).__init__()
        self.shared = shared

    @staticmethod
    def run_background(func, callback, args=(), kwds=None):
        if not kwds:
            kwds = {}

        def _callback(result):
            IOLoop.instance().add_callback(lambda: callback(result))

        _workers.apply_async(func, args, kwds, _callback)

    def task(self, message):
        for case in switch(message):
            if case(DgtApi.DISPLAY_MOVE):
                if 'web' in message.devs:
                    bit_board = chess.Board(message.fen)
                    text = bit_board.san(message.move)
                    result = {'event': 'Clock', 'text': text}
                    EventHandler.write_to_clients(result)
                break
            if case(DgtApi.DISPLAY_TEXT):
                if 'web' in message.devs:
                    text = str(message.l)
                    result = {'event': 'Clock', 'text': text}
                    EventHandler.write_to_clients(result)
                break
            if case(DgtApi.DISPLAY_TIME):
                if 'web' in message.devs:
                    text = 'display time'
                    result = {'event': 'Clock', 'text': text}
                    EventHandler.write_to_clients(result)
                break
            if case(DgtApi.LIGHT_CLEAR):
                text = 'clear light'
                result = {'event': 'Clock', 'text': text}
                # EventHandler.write_to_clients(result)
                break
            if case(DgtApi.LIGHT_SQUARES):
                text = 'light: ' + str(message.uci_move)
                result = {'event': 'Clock', 'text': text}
                # EventHandler.write_to_clients(result)
                break
            if case(DgtApi.CLOCK_STOP):
                # text = 'stop clock'
                # result = {'event': 'Clock', 'text': text}
                # EventHandler.write_to_clients(result)
                break
            if case(DgtApi.CLOCK_START):
                # text = 'start clock'
                # result = {'event': 'Clock', 'text': text}
                # EventHandler.write_to_clients(result)
                break
            if case(DgtApi.CLOCK_VERSION):
                # text = 'version: ' + str(message.main) + str(message.sub)
                # result = {'event': 'Clock', 'text': text}
                # EventHandler.write_to_clients(result)
                break
            if case(DgtApi.CLOCK_TIME):
                if message.dev == 'ser':
                    time_l = message.time_left
                    time_r = message.time_right
                    text_l = '{}:{:02d}.{:02d}'.format(time_l[0], time_l[1], time_l[2])
                    text_r = '{}:{:02d}.{:02d}'.format(time_r[0], time_r[1], time_r[2])
                    result = {'event': 'Clock', 'text': text_l + ' ' + text_r}
                    EventHandler.write_to_clients(result)
                break
            if case():  # Default
                pass

    def _create_task(self, msg):
        IOLoop.instance().add_callback(callback=lambda: self.task(msg))

    def run(self):
        """called from threading.Thread by its start() function."""
        logging.info('dgt_queue ready')
        while True:
            # Check if we have something to display
            message = self.dgt_queue.get()
            self._create_task(message)


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

    def _create_game_info(self):
        if 'game_info' not in self.shared:
            self.shared['game_info'] = {}

    def _create_system_info(self):
        if 'system_info' not in self.shared:
            self.shared['system_info'] = {}

    def task(self, message):
        def _oldstyle_fen(game: chess.Board):
            builder = []
            builder.append(game.board_fen())
            builder.append('w' if game.turn == chess.WHITE else 'b')
            builder.append(game.castling_xfen())
            builder.append(chess.SQUARE_NAMES[game.ep_square] if game.ep_square else '-')
            builder.append(str(game.halfmove_clock))
            builder.append(str(game.fullmove_number))
            return ' '.join(builder)

        def _create_game_header(pgn_game: chess.pgn.Game):
            pgn_game.headers['Result'] = '*'
            pgn_game.headers['White'] = 'None'
            pgn_game.headers['Black'] = 'None'
            pgn_game.headers['Event'] = 'PicoChess game'
            pgn_game.headers['Date'] = datetime.datetime.now().date().strftime('%Y-%m-%d')
            pgn_game.headers['Round'] = '?'
            pgn_game.headers['Site'] = 'picochess.org'

            user_name = 'User'
            engine_name = 'Picochess'
            if 'system_info' in self.shared:
                if 'user_name' in self.shared['system_info']:
                    user_name = self.shared['system_info']['user_name']
                if 'engine_name' in self.shared['system_info']:
                    engine_name = self.shared['system_info']['engine_name']

            if 'game_info' in self.shared:
                if 'play_mode' in self.shared['game_info']:
                    if 'level_text' in self.shared['game_info']:
                        engine_name += ' [{0}]'.format(self.shared['game_info']['level_text'].m)
                    pgn_game.headers['Black'] = \
                        engine_name if self.shared['game_info']['play_mode'] == PlayMode.USER_WHITE else user_name
                    pgn_game.headers['White'] = \
                        engine_name if self.shared['game_info']['play_mode'] == PlayMode.USER_BLACK else user_name

                    comp_color = 'Black' if self.shared['game_info']['play_mode'] == PlayMode.USER_WHITE else 'White'
                    user_color = 'Black' if self.shared['game_info']['play_mode'] == PlayMode.USER_BLACK else 'White'
                    pgn_game.headers[comp_color + 'Elo'] = '2900'
                    pgn_game.headers[user_color + 'Elo'] = '-'

            if 'ip_info' in self.shared:
                if 'location' in self.shared['ip_info']:
                    pgn_game.headers['Site'] = self.shared['ip_info']['location']

        def _update_headers():
            pgn_game = pgn.Game()
            _create_game_header(pgn_game)
            self.shared['headers'] = pgn_game.headers
            EventHandler.write_to_clients({'event': 'header', 'headers': pgn_game.headers})

        def _update_title():
            EventHandler.write_to_clients({'event': 'title', 'ip_info': self.shared['ip_info']})

        def _transfer(game: chess.Board):
            pgn_game = pgn.Game().from_board(game)
            _create_game_header(pgn_game)
            return pgn_game.accept(pgn.StringExporter(headers=True, comments=False, variations=False))

        for case in switch(message):
            if case(MessageApi.BOOK_MOVE):
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'Book move'})
                break
            if case(MessageApi.START_NEW_GAME):
                pgn_str = _transfer(message.game)
                fen = message.game.fen()
                result = {'pgn': pgn_str, 'fen': fen}
                self.shared['last_dgt_move_msg'] = result
                pos960 = message.game.chess960_pos()
                if pos960:
                    code_text = '' if pos960 == 518 else ' - chess960 code {}'.format(pos960)
                else:
                    code_text = ' with setup'
                EventHandler.write_to_clients({'event': 'NewGame', 'fen': fen})
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'New game' + code_text})
                _update_headers()
                break
            if case(MessageApi.SEARCH_STARTED):
                EventHandler.write_to_clients({'event': 'Message', 'msg': 'Thinking...'})
                break
            if case(MessageApi.IP_INFO):
                self.shared['ip_info'] = message.info
                _update_headers()
                _update_title()
                break
            if case(MessageApi.SYSTEM_INFO):
                self.shared['system_info'] = message.info
                self.shared['system_info']['old_engine'] = self.shared['system_info']['engine_name']
                _update_headers()
                break
            if case(MessageApi.ENGINE_READY):
                self._create_system_info()
                self.shared['system_info']['engine_name'] = message.engine_name
                if not message.has_levels and 'level_text' in self.shared['game_info']:
                    del self.shared['game_info']['level_text']
                _update_headers()
                break
            if case(MessageApi.STARTUP_INFO):
                self.shared['game_info'] = message.info.copy()
                # change book_index to book_text
                books = message.info['books']
                book_index = message.info['book_index']
                self.shared['game_info']['book_text'] = books[book_index]['text']
                del self.shared['game_info']['book_index']

                if message.info['level_text'] is None:
                    del self.shared['game_info']['level_text']
                break
            if case(MessageApi.OPENING_BOOK):
                self._create_game_info()
                self.shared['game_info']['book_text'] = message.book_text
                break
            if case(MessageApi.INTERACTION_MODE):
                self._create_game_info()
                self.shared['game_info']['interaction_mode'] = message.mode
                if self.shared['game_info']['interaction_mode'] == Mode.REMOTE:
                    self.shared['system_info']['engine_name'] = 'Remote Player'
                else:
                    self.shared['system_info']['engine_name'] = self.shared['system_info']['old_engine']
                _update_headers()
                break
            if case(MessageApi.PLAY_MODE):
                self._create_game_info()
                self.shared['game_info']['play_mode'] = message.play_mode
                break
            if case(MessageApi.TIME_CONTROL):
                self._create_game_info()
                self.shared['game_info']['time_text'] = message.time_text
                break
            if case(MessageApi.LEVEL):
                self._create_game_info()
                self.shared['game_info']['level_text'] = message.level_text
                _update_headers()
                break
            if case(MessageApi.DGT_JACK_CONNECTED_ERROR):
                result = {'event': 'Message', 'msg': 'Unplug the jack cable please!'}
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.DGT_NO_CLOCK_ERROR):
                # result = {'event': 'Message', 'msg': 'Connect a clock please!'}
                # EventHandler.write_to_clients(result)
                break
            if case(MessageApi.DGT_NO_EBOARD_ERROR):
                result = {'event': 'Message', 'msg': 'Connect an E-Board please!'}
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.DGT_EBOARD_VERSION):
                result = {'event': 'Message', 'msg': message.text.l + ' connected through ' + message.channel}
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.DGT_CLOCK_VERSION):
                if message.dev == 'ser':
                    attached = 'serial'
                elif message.dev == 'i2c':
                    attached = 'i2c'
                else:
                    attached = 'virtual'
                result = {'event': 'Message', 'msg': 'DGT clock connected through ' + attached}
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.COMPUTER_MOVE):
                pgn_str = _transfer(message.game)
                fen = _oldstyle_fen(message.game)
                mov = message.move.uci()
                msg = 'Computer move: ' + str(message.move)
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'newFEN', 'move': mov, 'msg': msg, 'review_play': False}
                self.shared['last_dgt_move_msg'] = result
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.USER_MOVE):
                pgn_str = _transfer(message.game)
                fen = _oldstyle_fen(message.game)
                msg = 'User move: ' + str(message.move)
                mov = message.move.uci()
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'newFEN', 'move': mov, 'msg': msg, 'review_play': False}
                self.shared['last_dgt_move_msg'] = result
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.REVIEW_MOVE):
                pgn_str = _transfer(message.game)
                fen = _oldstyle_fen(message.game)
                msg = 'Review move: ' + str(message.move)
                mov = message.move.uci()
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'newFEN', 'move': mov, 'msg': msg, 'review_play': True}
                self.shared['last_dgt_move_msg'] = result
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.GAME_ENDS):
                if message.game.move_stack:
                    result = None
                    if message.result == GameResult.DRAW:
                        result = '1/2-1/2'
                    elif message.result in (GameResult.WIN_WHITE, GameResult.WIN_BLACK):
                        result = '1-0' if message.result == GameResult.WIN_WHITE else '0-1'
                    elif message.result == GameResult.OUT_OF_TIME:
                        result = '0-1' if message.game.turn == chess.WHITE else '1-0'
                    if result:
                        EventHandler.write_to_clients({'event': 'Message', 'msg': 'Game over, Result: ' + result})
                break
            if case():  # Default
                # print(message)
                pass

    def _create_task(self, msg):
        IOLoop.instance().add_callback(callback=lambda: self.task(msg))

    def run(self):
        """called from threading.Thread by its start() function."""
        logging.info('msg_queue ready')
        while True:
            # Check if we have something to display
            message = self.msg_queue.get()
            self._create_task(message)
