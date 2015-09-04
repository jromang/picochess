#!/usr/bin/env python3
import sys
import os
import random
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../libs"))

import chess
import chess.polyglot
import chess.uci


class Tester():
    def __init__(self, bookreader, game):
        self.bookreader = bookreader
        self.game = game
        self.bookmoves = set()
        self.gamemoves = set()

    def setup(self):
        for entry in self.bookreader.find_all(self.game):
            self.bookmoves.add(entry)

        for move in self.game.legal_moves:
            self.gamemoves.add(move)

    def all(self):
        return self.gamemoves

    def weighted_choice(self):
        total_weights = sum(entry.weight for entry in self.bookmoves)
        if not total_weights:
            return None
        choice = random.randint(0, total_weights - 1)
        current_sum = 0
        for entry in self.bookmoves:
            current_sum += entry.weight
            if current_sum > choice:
                return entry
        assert False

    def book(self):
        bm = self.weighted_choice()
        if bm:
            self.bookmoves.discard(bm)
            book_move = bm.move()
            g = copy.deepcopy(self.game)
            g.push(book_move)
            try:
                bp = self.bookreader.weighted_choice(g)
                book_ponder = bp.move()
            except IndexError:
                book_ponder = None
            return chess.uci.BestMove(book_move, book_ponder)
        return None

    def make(self, move):
        self.gamemoves.discard(move)
        if not self.gamemoves:
            self.setup()


class Informer(chess.uci.InfoHandler):
    def on_go(self):
        print('onGO called')
        super().on_go()
        pass

    def on_bestmove(self, bestmove, ponder):
        print('onBEST called')
        print(bestmove)
        print(ponder)
        super().on_bestmove(bestmove, ponder)

# engine = chess.uci.popen_engine("../engines/stockfish6/stockfish_6_x64")
# engine.uci()

# handler = Informer()
# engine.info_handlers.append(handler)

# fen_game = 'r1r3k1/pp1q1pp1/4pn1p/1B1p1n2/3P4/1QN1P2P/PP3PP1/2R1R1K1 b - - 0 1'
# board = chess.Board(fen_game)
# engine.position(board)

# futur = engine.go(ponder=True, infinite=True, async_callback=True)
# print(futur)
# time.sleep(2)
# engine.stop()
# result = futur.result()
# print(result)


board = chess.Board()
board.push_san('f4')

print('Tester:')
reader = chess.polyglot.open_reader("../books/g-fun.bin")
t = Tester(reader, board)
t.setup()

print(t.all())
print('')
t.make(random.choice(list(t.all())))
print(t.all())
print('')

print(t.book())
print('')
print(t.book())
print('')
print(t.book())
print('')
print(t.book())
print('')  # after 1.f4, should result in "None" cause only 4 moves in bin-file
print(t.book())
