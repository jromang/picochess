# Copyright (C) 2013-2016 Jean-Francois Romang (jromang@posteo.de)
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

from utilities import *


class MsgKey(AutoNumber):
    MODE_GAME = ()
    MODE_ANALYSIS = ()
    MODE_KIBITZ = ()
    MODE_OBSERVE = ()
    MODE_REMOTE = ()
    
    GAMERESULT_MATE = ()
    GAMERESULT_STALEMATE = ()
    GAMERESULT_OUT_OF_TIME = ()
    GAMERESULT_MATERIAL = ()
    GAMERESULT_MOVES = ()
    GAMERESULT_REPETITION = ()
    GAMERESULT_ABORT = ()
    GAMERESULT_RESIGN_WHITE = ()
    GAMERESULT_RESIGN_BLACK = ()
    GAMERESULT_DRAW = ()
    CLOCKMODE_FIXED = ()
    CLOCKMODE_BLITZ = ()
    CLOCKMODE_FISCHER = ()
    
    POWER_OFF = ()
    REBOOT = ()
    NOMOVE = ()
    LEVEL = ()
    NOLEVEL = ()
    PICOCHESS = ()
    
    NOSCORE = ()
    MATE = ()
    ORIENTATION_BW = ()
    ORIENTATION_WB = ()
    ERROR = ()
    SCAN = ()
    
    BADPOS = ()
    OK_LEVEL = ()
    QUESTION_POWEROFF = ()
    QUESTION_REBOOT = ()
    OK_BOOK = ()
    OK_TIME = ()
    
    MODE960YES = ()
    MODE960NO = ()
    MENU_GAME = ()
    MENU_POSITION = ()
    MENU_ENGINE = ()
    MENU_LEVEL = ()
    MENU_BOOK = ()
    MENU_TIME = ()
    MENU_SYSTEM = ()
    
    OK_ENGINE = ()
    NEW_GAME = ()
    YOU_MOVE = ()
    OK_PICO = ()
    OK_MOVE = ()
    ALTERNATIVE_MOVE = ()
    
    TAKEBACK = ()
    BOOK_MOVE = ()


class MsgTxt(object):
    def __init__(self, s=None, m=None, l=None):
        super(MsgTxt, self).__init__()
        self.s = s
        self.m = m
        self.l = l

    def small(self):
        return self.s

    def medium(self):
        return self.m

    def large(self):
        return self.l


english = {MsgKey.MODE_GAME:                MsgTxt(s='game',    m='game',       l='game'),
           MsgKey.MODE_ANALYSIS:            MsgTxt(s='analys',  m='analyse',    l='analysis'),
           MsgKey.MODE_KIBITZ:              MsgTxt(s='kibitz',  m='kibitz',     l='kibitz'),
           MsgKey.MODE_OBSERVE:             MsgTxt(s='observ',  m='observe',    l='observe'),
           MsgKey.MODE_REMOTE:              MsgTxt(s='remote',  m='remote',     l='remote'),
           
           MsgKey.GAMERESULT_MATE:          MsgTxt(s='mate',    m='mate',       l='mate'),
           MsgKey.GAMERESULT_STALEMATE:     MsgTxt(s='stale',   m='stalemat',   l='stalemate'),
           MsgKey.GAMERESULT_OUT_OF_TIME:   MsgTxt(s='time',    m='time',       l='time'),
           MsgKey.GAMERESULT_MATERIAL:      MsgTxt(s='materi',  m='material',   l='material'),
           MsgKey.GAMERESULT_MOVES:         MsgTxt(s='75 mov',  m='75 moves',   l='75 moves'),
           MsgKey.GAMERESULT_REPETITION:    MsgTxt(s='reppos',  m='rep pos',    l='repetition'),
           MsgKey.GAMERESULT_ABORT:         MsgTxt(s='abort',   m='abort',      l='abort'),
           MsgKey.GAMERESULT_RESIGN_WHITE:  MsgTxt(s='w wins',  m='w wins',     l='w wins'),
           MsgKey.GAMERESULT_RESIGN_BLACK:  MsgTxt(s='b wins',  m='b wins',     l='b wins'),
           MsgKey.GAMERESULT_DRAW:          MsgTxt(s='draw',    m='draw',       l='draw'),
           MsgKey.CLOCKMODE_FIXED:          MsgTxt(s='fixed',   m='fixed',      l='fixed'),
           MsgKey.CLOCKMODE_BLITZ:          MsgTxt(s='blitz',   m='blitz',      l='blitz'),
           MsgKey.CLOCKMODE_FISCHER:        MsgTxt(s='fische',  m='fischer',    l='fischer'),

           MsgKey.POWER_OFF:                MsgTxt(s='byebye',  m='good bye',   l='good bye'),
           MsgKey.REBOOT:                   MsgTxt(s='wait',    m='pls wait',   l='please wait'),
           MsgKey.NOMOVE:                   MsgTxt(s='nomove',  m='no move',    l='no move'),
           MsgKey.LEVEL:                    MsgTxt(s='lvl ',    m='level ',     l='level '),
           MsgKey.NOLEVEL:                  MsgTxt(s='no lvl',  m='no level',   l='no level'),
           MsgKey.PICOCHESS:                MsgTxt(s='pic ',    m='pico ',      l='pico '),

           MsgKey.NOSCORE:                  MsgTxt(s='no scr',  m='no score',   l='no score'),
           MsgKey.MATE:                     MsgTxt(s='m ',      m='mate ',      l='mate in '),
           MsgKey.ORIENTATION_BW:           MsgTxt(s='b    w',  m=' b     w',   l=' b        w'),
           MsgKey.ORIENTATION_WB:           MsgTxt(s='w    b',  m=' w     b',   l=' w        b'),
           MsgKey.ERROR:                    MsgTxt(s='error',   m='error',      l='error'),
           MsgKey.SCAN:                     MsgTxt(s='scan',    m='scan',       l='scan board'),

           MsgKey.BADPOS:                   MsgTxt(s='badpos',  m='bad pos',    l='bad pos'),
           MsgKey.OK_LEVEL:                 MsgTxt(s='ok lvl',  m='ok level',   l='okay level'),
           MsgKey.QUESTION_POWEROFF:        MsgTxt(s='-off-',   m='pwroff ?',   l='power off ?'),
           MsgKey.QUESTION_REBOOT:          MsgTxt(s='-boot-',  m='reboot ?',   l='reboot ?'),
           MsgKey.OK_BOOK:                  MsgTxt(s='okbook',  m='ok book',    l='okay book'),
           MsgKey.OK_TIME:                  MsgTxt(s='oktime',  m='ok time',    l='okay time'),

           MsgKey.MODE960YES:               MsgTxt(s='960yes',  m='960 yes',    l='960 yes'),
           MsgKey.MODE960NO:                MsgTxt(s='960 no',  m='960 no',     l='960 no'),
           MsgKey.MENU_GAME:                MsgTxt(s='game',    m='game',       l='game'),
           MsgKey.MENU_POSITION:            MsgTxt(s='positi',  m='position',   l='position'),
           MsgKey.MENU_ENGINE:              MsgTxt(s='engine',  m='engine',     l='engine'),
           MsgKey.MENU_LEVEL:               MsgTxt(s='level',   m='level',      l='level'),
           MsgKey.MENU_BOOK:                MsgTxt(s='book',    m='book',       l='book'),
           MsgKey.MENU_TIME:                MsgTxt(s='time',    m='time',       l='time'),
           MsgKey.MENU_SYSTEM:              MsgTxt(s='system',  m='system',     l='system'),

           MsgKey.OK_ENGINE:                MsgTxt(s='ok eng',  m='okengine',   l='okay engine'),
           MsgKey.NEW_GAME:                 MsgTxt(s='newgam',  m='new game',   l='new game'),
           MsgKey.YOU_MOVE:                 MsgTxt(s='youmov',  m='you move',   l='your move'),
           MsgKey.OK_PICO:                  MsgTxt(s='okpico',  m='ok pico',    l='okay pico'),
           MsgKey.OK_MOVE:                  MsgTxt(s='okmove',  m='ok move',    l='okay move'),
           MsgKey.ALTERNATIVE_MOVE:         MsgTxt(s='altmov',  m='alt move',   l='altn move'),

           MsgKey.TAKEBACK:                 MsgTxt(s='takbak',  m='takeback',   l='takeback'),
           MsgKey.BOOK_MOVE:                MsgTxt(s='book',    m='book',       l='book move')
           }

german = { MsgKey.MODE_GAME:                MsgTxt(s='game',    m='game',       l='game'),
           MsgKey.MODE_ANALYSIS:            MsgTxt(s='analys',  m='analyse',    l='analysis'),
           MsgKey.MODE_KIBITZ:              MsgTxt(s='kibitz',  m='kibitz',     l='kibitz'),
           MsgKey.MODE_OBSERVE:             MsgTxt(s='observ',  m='observe',    l='observe'),
           MsgKey.MODE_REMOTE:              MsgTxt(s='remote',  m='remote',     l='remote'),

           MsgKey.GAMERESULT_MATE:          MsgTxt(s='mate',    m='matt',       l='matt'),
           MsgKey.GAMERESULT_STALEMATE:     MsgTxt(s='stale',   m='patt',       l='patt'),
           MsgKey.GAMERESULT_OUT_OF_TIME:   MsgTxt(s='time',    m='zeit',       l='zeit'),
           MsgKey.GAMERESULT_MATERIAL:      MsgTxt(s='materi',  m='material',   l='material'),
           MsgKey.GAMERESULT_MOVES:         MsgTxt(s='75 mov',  m='75 zuege',   l='75 zuege'),
           MsgKey.GAMERESULT_REPETITION:    MsgTxt(s='reppos',  m='wiederho',   l='wiederholg'),
           MsgKey.GAMERESULT_ABORT:         MsgTxt(s='abort',   m='abbruch',    l='abbruch'),
           MsgKey.GAMERESULT_RESIGN_WHITE:  MsgTxt(s='w wins',  m='w gewinn',   l='w gewinnt'),
           MsgKey.GAMERESULT_RESIGN_BLACK:  MsgTxt(s='b wins',  m='s gewinn',   l='s gewinnt'),
           MsgKey.GAMERESULT_DRAW:          MsgTxt(s='draw',    m='unendsch',   l='unentschied'),
           MsgKey.CLOCKMODE_FIXED:          MsgTxt(s='fixed',   m='fest',       l='feste zeit'),
           MsgKey.CLOCKMODE_BLITZ:          MsgTxt(s='blitz',   m='blitz',      l='blitz'),
           MsgKey.CLOCKMODE_FISCHER:        MsgTxt(s='fische',  m='fischer',    l='fischer'),

           MsgKey.POWER_OFF:                MsgTxt(s='byebye',  m='tschuess',   l='tschuess'),
           MsgKey.REBOOT:                   MsgTxt(s='wait',    m='warten',     l='warten'),
           MsgKey.NOMOVE:                   MsgTxt(s='nomove',  m='kein zug',   l='kein zug'),
           MsgKey.LEVEL:                    MsgTxt(s='lvl ',    m='stufe ',     l='stufe '),
           MsgKey.NOLEVEL:                  MsgTxt(s='no lvl',  m='keine st',   l='keine stufe'),
           MsgKey.PICOCHESS:                MsgTxt(s='pic ',    m='pico ',      l='pico '),

           MsgKey.NOSCORE:                  MsgTxt(s='no scr',  m='keinwert',   l='kein wert'),
           MsgKey.MATE:                     MsgTxt(s='mate ',   m='matt ',      l='matt in '),
           MsgKey.ORIENTATION_BW:           MsgTxt(s='b    w',  m=' s     w',   l=' s        w'),
           MsgKey.ORIENTATION_WB:           MsgTxt(s='w    b',  m=' w     s',   l=' w        s'),
           MsgKey.ERROR:                    MsgTxt(s='error',   m='fehler',     l='fehler'),
           MsgKey.SCAN:                     MsgTxt(s='scan',    m='lese stl',   l='lese stellg'),

           MsgKey.BADPOS:                   MsgTxt(s='badpos',  m='err stl',    l='err stellg'),
           MsgKey.OK_LEVEL:                 MsgTxt(s='ok lvl',  m='ok stufe',   l='ok stufe'),
           MsgKey.QUESTION_POWEROFF:        MsgTxt(s='-off-',   m='aussch ?',   l='ausschalt ?'),
           MsgKey.QUESTION_REBOOT:          MsgTxt(s='-boot-',  m='restart ?',  l='reboot ?'),
           MsgKey.OK_BOOK:                  MsgTxt(s='okbook',  m='ok buch',    l='okay buch'),
           MsgKey.OK_TIME:                  MsgTxt(s='oktime',  m='ok zeit',    l='okay zeit'),

           MsgKey.MODE960YES:               MsgTxt(s='960yes',  m='960 ja',     l='960 ja'),
           MsgKey.MODE960NO:                MsgTxt(s='960 no',  m='960 nein',   l='960 nein'),
           MsgKey.MENU_GAME:                MsgTxt(s='game',    m='spiel',      l='spiel'),
           MsgKey.MENU_POSITION:            MsgTxt(s='positi',  m='position',   l='position'),
           MsgKey.MENU_ENGINE:              MsgTxt(s='engine',  m='engine',     l='engine'),
           MsgKey.MENU_LEVEL:               MsgTxt(s='level',   m='stufe',      l='stufe'),
           MsgKey.MENU_BOOK:                MsgTxt(s='book',    m='buch',       l='buch'),
           MsgKey.MENU_TIME:                MsgTxt(s='time',    m='zeit',       l='zeit'),
           MsgKey.MENU_SYSTEM:              MsgTxt(s='system',  m='system',     l='system'),
           MsgKey.OK_ENGINE:                MsgTxt(s='ok eng',  m='okengine',   l='okay engine'),
           MsgKey.NEW_GAME:                 MsgTxt(s='newgam',  m='neues sp',   l='neues spiel'),
           MsgKey.YOU_MOVE:                 MsgTxt(s='youmov',  m='ihr zug',    l='ihr zug'),
           MsgKey.OK_PICO:                  MsgTxt(s='okpico',  m='ok pico',    l='okay pico'),
           MsgKey.OK_MOVE:                  MsgTxt(s='okmove',  m='ok zug',     l='okay zug'),
           MsgKey.ALTERNATIVE_MOVE:         MsgTxt(s='altmov',  m='altn zug',   l='altnat zug'),

           MsgKey.TAKEBACK:                 MsgTxt(s='takbak',  m='ruecknah',   l='ruecknahme'),
           MsgKey.BOOK_MOVE:                MsgTxt(s='book',    m='buch zug',   l='buch zug')
           }

dutch =   {MsgKey.MODE_GAME:                MsgTxt(s='spel',    m='spel',       l='spel'),
           MsgKey.MODE_ANALYSIS:            MsgTxt(s='analyse', m='analyse',    l='analyseren'),
           MsgKey.MODE_KIBITZ:              MsgTxt(s='kibitz',  m='kibitz',     l='kibitz'),
           MsgKey.MODE_OBSERVE:             MsgTxt(s='bekijk',  m='bekijk', 	l='bekijk'),
           MsgKey.MODE_REMOTE:              MsgTxt(s='remote',  m='remote',     l='remote'),

           MsgKey.GAMERESULT_MATE:          MsgTxt(s='mat',     m='mat',        l='mat'),
           MsgKey.GAMERESULT_STALEMATE:     MsgTxt(s='pat',     m='patstlng',   l='patstelling'),
           MsgKey.GAMERESULT_OUT_OF_TIME:   MsgTxt(s='tijd',    m='tijd',       l='tijd'),
           MsgKey.GAMERESULT_MATERIAL:      MsgTxt(s='materi',  m='material',   l='materiaal'),
           MsgKey.GAMERESULT_MOVES:         MsgTxt(s='zet 75',  m='75zetten',   l='75 zetten'),
           MsgKey.GAMERESULT_REPETITION:    MsgTxt(s='zelfde',  m='dezelfde',   l='zelfde stel'),
           MsgKey.GAMERESULT_ABORT:         MsgTxt(s='afbrek',  m='afbreken',   l='afbreken'),
           MsgKey.GAMERESULT_RESIGN_WHITE:  MsgTxt(s='w wint',  m='wit wint',   l='wit wint'),
           MsgKey.GAMERESULT_RESIGN_BLACK:  MsgTxt(s='z wint',  m='z wint',     l='zwart wint'),
           MsgKey.GAMERESULT_DRAW:          MsgTxt(s='remise',  m='remise',     l='remise'),
           MsgKey.CLOCKMODE_FIXED:          MsgTxt(s='fixed',   m='fixed',      l='fixed'),
           MsgKey.CLOCKMODE_BLITZ:          MsgTxt(s='blitz',   m='blitz',      l='blitz'),
           MsgKey.CLOCKMODE_FISCHER:        MsgTxt(s='fische',  m='fischer',    l='fischer'),

           MsgKey.POWER_OFF:                MsgTxt(s='dagdag',  m='doeidoei',   l='goedendag'),
           MsgKey.REBOOT:                   MsgTxt(s='wacht',   m='wachten',    l='wacht even'),
           MsgKey.NOMOVE:                   MsgTxt(s='gn zet',  m='geen zet',   l='geen zet'),
           MsgKey.LEVEL:                    MsgTxt(s='lvl ',    m='level ',     l='level '),
           MsgKey.NOLEVEL:                  MsgTxt(s='gn lvl',  m='gn level',   l='geen level'),
           MsgKey.PICOCHESS:                MsgTxt(s='pic ',    m='pico ',      l='pico '),

           MsgKey.NOSCORE:                  MsgTxt(s='no scr',  m='no score',   l='no score'),
           MsgKey.MATE:                     MsgTxt(s='mat ',    m='mat in ',    l='mate in '),
           MsgKey.ORIENTATION_BW:           MsgTxt(s='z    w',  m=' z     w',   l='z        w'),
           MsgKey.ORIENTATION_WB:           MsgTxt(s='w    z',  m=' w     z',   l='w        z'),
           MsgKey.ERROR:                    MsgTxt(s='error',   m='error',      l='error'),
           MsgKey.SCAN:                     MsgTxt(s='scan',    m='scan',       l='scan bord'),

           MsgKey.BADPOS:                   MsgTxt(s='badpos',  m='bad pos',    l='bad pos'),
           MsgKey.OK_LEVEL:                 MsgTxt(s='ok lvl',  m='ok level',   l='oke level'),
           MsgKey.QUESTION_POWEROFF:        MsgTxt(s='-uit-',   m='zetuit ?',   l='uitzetten ?'),
           MsgKey.QUESTION_REBOOT:          MsgTxt(s='-boot-',  m='reboot ?',   l='reboot ?'),
           MsgKey.OK_BOOK:                  MsgTxt(s='okboek',  m='ok boek',    l='okay boek'),
           MsgKey.OK_TIME:                  MsgTxt(s='oktijd',  m='ok tijd',    l='oke tijd'),

           MsgKey.MODE960YES:               MsgTxt(s='960 ja',  m='960 ja',     l='960 ja'),
           MsgKey.MODE960NO:                MsgTxt(s='960nee',  m='960 nee',    l='960 nee'),
           MsgKey.MENU_GAME:                MsgTxt(s='spel',    m='spel',       l='spel'),
           MsgKey.MENU_POSITION:            MsgTxt(s='positi',  m='positie',    l='positie'),
           MsgKey.MENU_ENGINE:              MsgTxt(s='engine',  m='engine',     l='engine'),
           MsgKey.MENU_LEVEL:               MsgTxt(s='level',   m='level',      l='level'),
           MsgKey.MENU_BOOK:                MsgTxt(s='boek',    m='boek',       l='boek'),
           MsgKey.MENU_TIME:                MsgTxt(s='tijd',    m='tijd',       l='tijd'),
           MsgKey.MENU_SYSTEM:              MsgTxt(s='system',  m='systeem',    l='systeem'),

           MsgKey.OK_ENGINE:                MsgTxt(s='ok eng',  m='okengine',   l='oke engine'),
           MsgKey.NEW_GAME:                 MsgTxt(s='newspl',  m='new spel',   l='nieuw spel'),
           MsgKey.YOU_MOVE:                 MsgTxt(s='uw zet',  m='uw zet',     l='uw zet'),
           MsgKey.OK_PICO:                  MsgTxt(s='okpico',  m='oke pico',   l='oke pico'),
           MsgKey.OK_MOVE:                  MsgTxt(s='zet ok',  m='zet oke',    l='zet oke'),
           MsgKey.ALTERNATIVE_MOVE:         MsgTxt(s='altzet',  m='alt zet',    l='andere zet'),

           MsgKey.TAKEBACK:                 MsgTxt(s='terug',   m='zetterug',   l='zet terug'),
           MsgKey.BOOK_MOVE:                MsgTxt(s='boek',    m='boek zet',   l='boek zet')
           }

print(english[MsgKey.NEW_GAME])
print(english[MsgKey.ERROR].small())
print(english[MsgKey.ERROR].medium())
