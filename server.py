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

import chess
import chess.pgn as pgn

import tornado.web
import tornado.wsgi
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from utilities import Observable, DisplayMsg, switch, hours_minutes_seconds, RepeatedTimer
import logging
from dgt.api import MessageApi, Event, Message
from dgt.util import GameResult, PlayMode, Mode, ClockSide
from web.picoweb import picoweb as pw

from dgt.iface import DgtIface
from dgt.translate import DgtTranslate
from dgt.board import DgtBoard

# This needs to be reworked to be session based (probably by token)
# Otherwise multiple clients behind a NAT can all play as the 'player'
client_ips = []


class ServerRequestHandler(tornado.web.RequestHandler):
    def initialize(self, shared=None):
        self.shared = shared

    def data_received(self, chunk):
        pass


class ChannelHandler(ServerRequestHandler):
    def process_console_command(self, raw):
        cmd = raw.lower()

        try:
            # Here starts the simulation of a dgt-board!
            # Let the user send events like the board would do
            if cmd.startswith('fen:'):
                fen = raw.split(':')[1].strip()
                # dgt board only sends the basic fen => be sure it's same no matter what fen the user entered
                fen = fen.split(' ')[0]
                bit_board = chess.Board()  # valid the fen
                bit_board.set_board_fen(fen)
                Observable.fire(Event.KEYBOARD_FEN(fen=fen))
            # end simulation code
            elif cmd.startswith('go'):
                if 'last_dgt_move_msg' in self.shared:
                    fen = self.shared['last_dgt_move_msg']['fen'].split(' ')[0]
                    Observable.fire(Event.KEYBOARD_FEN(fen=fen))
            else:
                # Event.KEYBOARD_MOVE tranfers "move" to "fen" and then continues with "Message.DGT_FEN"
                move = chess.Move.from_uci(cmd)
                Observable.fire(Event.KEYBOARD_MOVE(move=move))
        except (ValueError, IndexError):
            logging.warning('Invalid user input [%s]', raw)

    def post(self):
        action = self.get_argument('action')

        if action == 'broadcast':
            fen = self.get_argument('fen')
            pgn_str = self.get_argument('pgn')
            result = {'event': 'Broadcast', 'msg': 'Position from Spectators!', 'pgn': pgn_str, 'fen': fen}
            EventHandler.write_to_clients(result)
        elif action == 'move':
            uci_move = self.get_argument('source') + self.get_argument('target')
            Observable.fire(Event.REMOTE_MOVE(uci_move=uci_move, fen=self.get_argument('fen')))
        elif action == 'clockbutton':
            Observable.fire(Event.KEYBOARD_BUTTON(button=self.get_argument('button'), dev='web'))
        elif action == 'command':
            self.process_console_command(self.get_argument('command'))


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
        real_ip = x_real_ip if x_real_ip else self.request.remote_ip
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
    def get(self, *args, **kwargs):
        action = self.get_argument('action')
        if action == 'get_last_move':
            if 'last_dgt_move_msg' in self.shared:
                self.write(self.shared['last_dgt_move_msg'])


class InfoHandler(ServerRequestHandler):
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
        if action == 'get_clock_text':
            if 'clock_text' in self.shared:
                self.write(self.shared['clock_text'])


class ChessBoardHandler(ServerRequestHandler):
    def get(self):
        self.render('web/picoweb/templates/clock.html')


class WebServer(threading.Thread):
    def __init__(self, port: int, dgttranslate: DgtTranslate, dgtboard: DgtBoard):
        shared = {}

        WebDisplay(shared).start()
        WebVr(shared, dgttranslate, dgtboard).start()
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


class WebVr(DgtIface):

    """Handle the web (clock) communication."""

    def __init__(self, shared, dgttranslate: DgtTranslate, dgtboard: DgtBoard):
        super(WebVr, self).__init__(dgttranslate, dgtboard)
        self.shared = shared
        self.virtual_timer = None
        self.time_side = ClockSide.NONE
        self.enable_dgt_pi = dgtboard.is_pi
        sub = 2 if dgtboard.is_pi else 0
        DisplayMsg.show(Message.DGT_CLOCK_VERSION(main=2, sub=sub, dev='web', text=None))
        self.clock_show_time = True

    def _create_clock_text(self):
        if 'clock_text' not in self.shared:
            self.shared['clock_text'] = {}

    def _runclock(self):
        if self.time_side == ClockSide.LEFT:
            hours, mins, secs = self.time_left
            time_left = 3600*hours + 60*mins + secs - 1
            if time_left <= 0:
                logging.info('negative/zero time left: %s', time_left)
                self.virtual_timer.stop()
                self.time_left = 0
            self.time_left = hours_minutes_seconds(time_left)
        if self.time_side == ClockSide.RIGHT:
            hours, mins, secs = self.time_right
            time_right = 3600*hours + 60*mins + secs - 1
            if time_right <= 0:
                logging.info('negative/zero time right: %s', time_right)
                self.virtual_timer.stop()
                self.time_right = 0
            self.time_right = hours_minutes_seconds(time_right)
        self._display_time(self.time_left, self.time_right)

    def _display_time(self, time_l, time_r):
        if time_l is None or time_r is None:
            logging.debug('time values not set - abort function')
        elif self.clock_show_time:
            text_l = '{}:{:02d}.{:02d}'.format(time_l[0], time_l[1], time_l[2])
            text_r = '{}:{:02d}.{:02d}'.format(time_r[0], time_r[1], time_r[2])
            icon_d = 'fa-caret-right' if self.time_side == ClockSide.RIGHT else 'fa-caret-left'
            if self.time_side == ClockSide.NONE:
                icon_d = 'fa-sort'
            text = text_l + '&nbsp;<i class="fa ' + icon_d + '"></i>&nbsp;' + text_r
            self._create_clock_text()
            self.shared['clock_text'] = text
            result = {'event': 'Clock', 'msg': text}
            EventHandler.write_to_clients(result)

    def display_move_on_clock(self, message):
        """display a move on the web clock."""
        if self.enable_dgt_3000 or self.enable_dgt_pi:
            bit_board, text = self.get_san(message, not self.enable_dgt_pi)
            points = '...' if message.side == ClockSide.RIGHT else '.'
            if self.enable_dgt_pi:
                text = '{:3d}{:s}{:s}'.format(bit_board.fullmove_number, points, text)
            else:
                text = '{:2d}{:s}{:s}'.format(bit_board.fullmove_number % 100, points, text)
        else:
            text = message.move.uci()
            if message.side == ClockSide.RIGHT:
                text = text.rjust(6)
        if 'web' not in message.devs:
            logging.debug('ignored message cause of devs [%s]', text)
            return
        self.clock_show_time = False
        self._create_clock_text()
        self.shared['clock_text'] = text
        result = {'event': 'Clock', 'msg': text}
        EventHandler.write_to_clients(result)

    def display_text_on_clock(self, message):
        """display a text on the web clock."""
        if self.enable_dgt_pi:
            text = message.l
        else:
            text = message.m if self.enable_dgt_3000 else message.s
        if text is None:
            text = message.m
        if 'web' not in message.devs:
            logging.debug('ignored message cause of devs [%s]', text)
            return
        self.clock_show_time = False
        self._create_clock_text()
        self.shared['clock_text'] = text
        result = {'event': 'Clock', 'msg': text}
        EventHandler.write_to_clients(result)

    def display_time_on_clock(self, message):
        """display the time on the web clock."""
        if 'web' not in message.devs:
            logging.debug('ignored message cause of devs [endText]')
            return
        if self.clock_running or message.force:
            self.clock_show_time = True
            self._display_time(self.time_left, self.time_right)
        else:
            logging.debug('(web) clock isnt running - no need for endText')

    def stop_clock(self, devs: set):
        """stop the time on the web clock."""
        if 'web' not in devs:
            logging.debug('ignored message cause of devs [stopClock]')
            return
        if self.virtual_timer:
            self.virtual_timer.stop()
        self._resume_clock(ClockSide.NONE)

    def _resume_clock(self, side: ClockSide):
        self.clock_running = (side != ClockSide.NONE)
        self.time_side = side

    def start_clock(self, time_left: int, time_right: int, side: ClockSide, devs: set):
        """start the time on the web clock."""
        if 'web' not in devs:
            logging.debug('ignored message cause of devs [startClock]')
            return
        if self.virtual_timer:
            self.virtual_timer.stop()
        if side != ClockSide.NONE:
            self.virtual_timer = RepeatedTimer(1, self._runclock)
            self.virtual_timer.start()
        self._resume_clock(side)
        self.clock_show_time = True
        # simulate the "start_clock" function from dgthw/pi
        self.time_left = hours_minutes_seconds(time_left)
        self.time_right = hours_minutes_seconds(time_right)
        self._display_time(self.time_left, self.time_right)

    def light_squares_revelation_board(self, squares):
        result = {'event': 'Light', 'move': squares}
        EventHandler.write_to_clients(result)

    def clear_light_revelation_board(self):
        result = {'event': 'Clear'}
        EventHandler.write_to_clients(result)

    def _create_task(self, msg):
        IOLoop.instance().add_callback(callback=lambda: self._process_message(msg))


class WebDisplay(DisplayMsg, threading.Thread):
    def __init__(self, shared):
        super(WebDisplay, self).__init__()
        self.shared = shared

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
            EventHandler.write_to_clients({'event': 'Header', 'headers': pgn_game.headers})

        def _update_title():
            EventHandler.write_to_clients({'event': 'Title', 'ip_info': self.shared['ip_info']})

        def _transfer(game: chess.Board):
            pgn_game = pgn.Game().from_board(game)
            _create_game_header(pgn_game)
            return pgn_game.accept(pgn.StringExporter(headers=True, comments=False, variations=False))

        for case in switch(message):
            if case(MessageApi.START_NEW_GAME):
                pgn_str = _transfer(message.game)
                fen = message.game.fen()
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'Game', 'move': '0000', 'play': 'newgame'}
                self.shared['last_dgt_move_msg'] = result
                EventHandler.write_to_clients(result)
                _update_headers()
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
                _update_headers()
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
            if case(MessageApi.DGT_NO_CLOCK_ERROR):
                result = {'event': 'Status', 'msg': 'Error clock'}
                # EventHandler.write_to_clients(result)
                break
            if case(MessageApi.DGT_CLOCK_VERSION):
                if message.dev == 'ser':
                    attached = 'serial'
                elif message.dev == 'i2c':
                    attached = 'i2c-pi'
                else:
                    attached = 'server'
                result = {'event': 'Status', 'msg': 'Ok clock ' + attached}
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.COMPUTER_MOVE):
                game_copy = message.game.copy()
                game_copy.push(message.move)
                pgn_str = _transfer(game_copy)
                fen = _oldstyle_fen(game_copy)
                mov = message.move.uci()
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'Fen', 'move': mov, 'play': 'computer'}
                self.shared['last_dgt_move_msg'] = result  # not send => keep it for COMPUTER_MOVE_DONE
                break
            if case(MessageApi.COMPUTER_MOVE_DONE):
                result = self.shared['last_dgt_move_msg']
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.USER_MOVE_DONE):
                pgn_str = _transfer(message.game)
                fen = _oldstyle_fen(message.game)
                mov = message.move.uci()
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'Fen', 'move': mov, 'play': 'user'}
                self.shared['last_dgt_move_msg'] = result
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.REVIEW_MOVE_DONE):
                pgn_str = _transfer(message.game)
                fen = _oldstyle_fen(message.game)
                mov = message.move.uci()
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'Fen', 'move': mov, 'play': 'review'}
                self.shared['last_dgt_move_msg'] = result
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.ALTERNATIVE_MOVE):
                pgn_str = _transfer(message.game)
                fen = _oldstyle_fen(message.game)
                mov = message.game.peek().uci()
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'Fen', 'move': mov, 'play': 'reload'}
                self.shared['last_dgt_move_msg'] = result
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.SWITCH_SIDES):
                pgn_str = _transfer(message.game)
                fen = _oldstyle_fen(message.game)
                mov = message.move.uci()
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'Fen', 'move': mov, 'play': 'reload'}
                self.shared['last_dgt_move_msg'] = result
                EventHandler.write_to_clients(result)
                break
            if case(MessageApi.TAKE_BACK):
                pgn_str = _transfer(message.game)
                fen = _oldstyle_fen(message.game)
                mov = message.game.peek().uci()
                result = {'pgn': pgn_str, 'fen': fen, 'event': 'Fen', 'move': mov, 'play': 'reload'}
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
                        EventHandler.write_to_clients({'event': 'Message', 'msg': 'Result: ' + result})
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
