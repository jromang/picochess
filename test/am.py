#!/usr/bin/env python3
import sys
import os
import random
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../libs"))

import chess
import chess.polyglot
import chess.uci


class Mover:
    def __init__(self, bookreader):
        self.bookreader = bookreader
        self.excludemoves = set()

    def all(self, game):
        searchmoves = set(game.legal_moves) - self.excludemoves
        return searchmoves

    def book(self, game):
        try:
            bm = self.bookreader.weighted_choice(game, self.excludemoves)
        except IndexError:
            return None

        book_move = bm.move()
        self.add(book_move)
        g = copy.deepcopy(game)
        g.push(book_move)
        try:
            bp = self.bookreader.weighted_choice(g)
            book_ponder = bp.move()
        except IndexError:
            book_ponder = None
        return chess.uci.BestMove(book_move, book_ponder)

    def add(self, move):
        self.excludemoves.add(move)


class Informer(chess.uci.InfoHandler):
    def on_go(self):
        # print('onGO called')
        super().on_go()
        pass

    def on_bestmove(self, bestmove, ponder):
        # print('onBEST called')
        # print(bestmove)
        # print(ponder)
        m.add(bestmove)
        super().on_bestmove(bestmove, ponder)


def think(mover, game):
    """
    Starts a new search on the current game.
    If a move is found in the opening book, fire an event in a few seconds.
    :return:
    """
    book_move = mover.book(game)
    if book_move:
        print('Book Result:')
        print(book_move)
    else:
        engine.position(game)

        uci_dict = {}
        uci_dict['searchmoves'] = mover.all(game)
        uci_dict['wtime'] = 2000
        uci_dict['btime'] = 2000
        result = engine.go(**uci_dict)
        print('Search Result:')
        print(result)

engine = chess.uci.popen_engine("../engines/stockfish")
engine.uci()

handler = Informer()
engine.info_handlers.append(handler)

board = chess.Board()
board.push_san('f4')

reader = chess.polyglot.open_reader("../books/g-fun.bin")

print('Mover:')
m = Mover(reader)
# print(m.all(board))
# print('')
# m.add(random.choice(list(m.all(board))))
# print(m.all(board))
# print('')

print(m.book(board))
print('')
print(m.book(board))
print('')
print(m.book(board))
print('')
print(m.book(board))
print('')  # after 1.f4, should result in "None" cause only 4 moves in bin-file
print(m.book(board))

m = Mover(reader)  # restart with an empty ignore-list
print('Thinker:')
think(m, board)
think(m, board)
think(m, board)
think(m, board)

think(m, board)
think(m, board)
think(m, board)
think(m, board)
print('end')
