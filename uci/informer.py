# Copyright (C) 2013-2018 Jean-Francois Romang (jromang@posteo.de)
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

from threading import Timer

from utilities import Observable
from dgt.api import Event
import chess.uci


class Informer(chess.uci.InfoHandler):

    """Internal uci engine info handler."""

    def __init__(self):
        super(Informer, self).__init__()
        self.allow_score = True
        self.allow_pv = True
        self.allow_depth = True

    def on_go(self):
        """Engine sends GO."""
        self.allow_score = True
        self.allow_pv = True
        self.allow_depth = True
        Observable.fire(Event.START_SEARCH())
        super().on_go()

    def on_bestmove(self, bestmove, ponder):
        Observable.fire(Event.STOP_SEARCH())
        super().on_bestmove(bestmove, ponder)

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
        """Engine sends SCORE."""
        if self._allow_fire_score():
            Observable.fire(Event.NEW_SCORE(score=cp, mate=mate))
        super().score(cp, mate, lowerbound, upperbound)

    def pv(self, moves):
        """Call when engine sends PV."""
        if self._allow_fire_pv() and moves:
            Observable.fire(Event.NEW_PV(pv=moves))
        super().pv(moves)

    def depth(self, dep):
        """Engine sends DEPTH."""
        if self._allow_fire_depth():
            Observable.fire(Event.NEW_DEPTH(depth=dep))
        super().depth(dep)
