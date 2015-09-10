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
    def __init__(self):
        self.excludemoves = set()

    def all(self, game):
        searchmoves = set(game.legal_moves) - self.excludemoves
        if not searchmoves:
            self.reset()
            return set(game.legal_moves)
        return searchmoves

    def book(self, bookreader, game):
        try:
            bm = bookreader.weighted_choice(game, self.excludemoves)
        except IndexError:
            return None

        book_move = bm.move()
        self.add(book_move)
        g = copy.deepcopy(game)
        g.push(book_move)
        try:
            bp = bookreader.weighted_choice(g)
            book_ponder = bp.move()
        except IndexError:
            book_ponder = None
        return chess.uci.BestMove(book_move, book_ponder)

    def add(self, move):
        self.excludemoves.add(move)

    def reset(self):
        self.excludemoves = set()


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
    book_move = mover.book(reader, game)
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
m = Mover()
# print(m.all(board))
# print('')
# m.add(random.choice(list(m.all(board))))
# print(m.all(board))
# print('')

print(m.book(reader, board))
print('')
print(m.book(reader, board))
print('')
print(m.book(reader, board))
print('')
print(m.book(reader, board))
print('')  # after 1.f4, should result in "None" cause only 4 moves in bin-file
print(m.book(reader, board))

m.reset()
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
