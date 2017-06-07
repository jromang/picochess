import chess.uci
from threading import Timer
from utilities import Observable
from dgt.api import Event


class Informer(chess.uci.InfoHandler):

    """internal uci engine info handler."""

    def __init__(self):
        super(Informer, self).__init__()
        self.allow_score = True
        self.allow_pv = True
        self.allow_depth = True

    def on_go(self):
        self.allow_score = True
        self.allow_pv = True
        self.allow_depth = True
        super().on_go()

    def _reset_allow_score(self):
        self.allow_score = True

    def _reset_allow_pv(self):
        self.allow_pv = True

    def _reset_allow_depth(self):
        self.allow_depth = True

    def _allow_fire_score(self):
        if self.allow_score:
            self.allow_score = False
            Timer(0.5, self._reset_allow_score).start()
            return True
        else:
            return False

    def _allow_fire_pv(self):
        if self.allow_pv:
            self.allow_pv = False
            Timer(0.5, self._reset_allow_pv).start()
            return True
        else:
            return False

    def _allow_fire_depth(self):
        if self.allow_depth:
            self.allow_depth = False
            Timer(0.5, self._reset_allow_depth).start()
            return True
        else:
            return False

    def score(self, cp, mate, lowerbound, upperbound):
        if self._allow_fire_score():
            Observable.fire(Event.NEW_SCORE(score=cp, mate=mate))
        super().score(cp, mate, lowerbound, upperbound)

    def pv(self, moves):
        if self._allow_fire_pv() and moves:
            Observable.fire(Event.NEW_PV(pv=moves))
        super().pv(moves)

    def depth(self, dep):
        if self._allow_fire_depth():
            Observable.fire(Event.NEW_DEPTH(depth=dep))
        super().depth(dep)
