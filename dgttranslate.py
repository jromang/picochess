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


class DgtTranslate(object):
    def __init__(self, beep_level, language):
        self.beep_level = beep_level
        self.language = language

    def bl(self, beeplevel):
        if beeplevel == BeepLevel.YES:
            return True
        if beeplevel == BeepLevel.NO:
            return False
        return bool(self.beep_level & beeplevel.value)

    def set_beep_level(self, beep_level):
        self.beep_level = beep_level

    def set_language(self, language):
        self.language  = language

    def move(self, text):
        def replace_all(text, dict):
            for i, j in dict.items():
                text = text.replace(i, j)
            return text

        dict = {}
        if self.language == 'de':
            dict = {'R': 'T', 'N': 'S', 'B': 'L', 'Q': 'D'}
        if self.language == 'nl':
            dict = {'R': 'T', 'N': 'P', 'B': 'L', 'Q': 'D'}
        if self.language == 'fr':
            dict = {'R': 'T', 'N': 'C', 'B': 'F', 'Q': 'D', 'K': 'R'}
        if self.language == 'es':
            dict = {'R': 'T', 'N': 'C', 'B': 'A', 'Q': 'D', 'K': 'R'}
        return replace_all(text, dict)

    def text(self, text_id, msg=''):
        en = de = nl = fr = es = None  # error case
        if text_id == 'B00_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = en
            nl = en
            fr = en
            es = en
        if text_id == 'B10_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = en
            nl = en
            fr = en
            es = en
        if text_id == 'M10_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.MAP), duration=1)
            de = en
            nl = en
            fr = en
            es = en
        if text_id == 'C10_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = en
            nl = en
            fr = en
            es = en
        if text_id == 'N10_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.NO), duration=1)
            de = en
            nl = en
            fr = en
            es = en
        if text_id == 'Y10_goodbye':
            en = Dgt.DISPLAY_TEXT(l=None, m='good bye', s='bye', beep=self.bl(BeepLevel.YES), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Tschuess', s='tschau', beep=self.bl(BeepLevel.YES), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='tot ziens', m='totziens', s='dag', beep=self.bl(BeepLevel.YES), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='au revoir', m='a plus', s='bye', beep=self.bl(BeepLevel.YES), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='adios', s=None, beep=self.bl(BeepLevel.YES), duration=1)
        if text_id == 'Y10_pleasewait':
            en = Dgt.DISPLAY_TEXT(l='please wait', m='pls wait', s='wait', beep=self.bl(BeepLevel.YES), duration=1)
            de = Dgt.DISPLAY_TEXT(l='bittewarten', m='warten', s=None, beep=self.bl(BeepLevel.YES), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='wacht even', m='wachten', s='wacht', beep=self.bl(BeepLevel.YES), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='patientez', m='patience', s='patien', beep=self.bl(BeepLevel.YES), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='espere', s=None, beep=self.bl(BeepLevel.YES), duration=1)
        if text_id == 'B10_nomove':
            en = Dgt.DISPLAY_TEXT(l=None, m='no move', s='nomove', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='kein Zug', s='kn zug', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='geen zet', s='gn zet', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='pas de mouv', m='pas mvt', s='pasmvt', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='sin mov', s='no mov', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B00_wb':
            en = Dgt.DISPLAY_TEXT(l=None, m=' w     b', s='w    b', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m=' w     s', s='w    s', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m=' w     z', s='w    z', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m=' b     n', s='b    n', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m=' b     n', s='b    n', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_bw':
            en = Dgt.DISPLAY_TEXT(l=None, m=' b     w', s='b    w', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m=' s     w', s='s    w', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m=' z     w', s='z    w', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m=' n     b', s='n    b', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m=' n     b', s='n    b', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_960no':
            en = Dgt.DISPLAY_TEXT(l='uci960 no', m='960 no', s='960 no', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='uci960 nein', m='960 nein', s='960 nn', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='uci960 nee', m='960 nee', s='960nee', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='uci960 non', m='960 non', s='960non', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='uci960 no', m='960 no', s='960 no', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_960yes':
            en = Dgt.DISPLAY_TEXT(l='uci960 yes', m='960 yes', s='960yes', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='uci960 ja', m='960 ja', s='960 ja', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='uci960 ja', m='960 ja', s='960 ja', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='uci960 oui', m='960 oui', s='960oui', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='uci960 si', m='960 si', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B10_picochess':
            en = Dgt.DISPLAY_TEXT(l='picoChs ' + version, m='pico ' + version, s='pic ' + version,
                                  beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = en
            nl = en
            fr = en
            es = en
        if text_id == 'B00_nofunction':
            en = Dgt.DISPLAY_TEXT(l='no function', m='no funct', s='nofunc', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='keine Funkt', m='keineFkt', s='kn fkt', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='geen functie', m='geen fnc', s='gn fnc', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='no fonction', m='no fonct', s='nofonc', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='sin funcion', m='sin func', s='nofunc', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'Y00_erroreng':
            en = Dgt.DISPLAY_TEXT(l='engine err', m='engn err', s='engerr', beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l='engine err', m='engn err', s='engerr', beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='engine fout', m='eng fout', s='e fout', beep=self.bl(BeepLevel.YES), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='moteur err', m='mot err', s='errmot', beep=self.bl(BeepLevel.YES), duration=0)
            es = Dgt.DISPLAY_TEXT(l='motor error', m='mot err', s='errmot', beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B10_okengine':
            en = Dgt.DISPLAY_TEXT(l='engine Okay', m='engineOk', s='ok eng', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='engine Okay', m='engineOk', s='ok eng', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='engine Ok', m='engineOk', s='ok eng', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='moteur Ok', m='mot Ok', s=None, beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='motor Okay', m='motor Ok', s='ok mot', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_okmode':
            en = Dgt.DISPLAY_TEXT(l='mode Okay', m='mode Ok', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Modus Okay', m='Modus Ok', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='modus Ok', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='mode Ok', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='modo Okay', m='modo Ok', s='okmodo', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_oklevel':
            en = Dgt.DISPLAY_TEXT(l='level Okay', m='level Ok', s='ok lvl', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Stufe Okay', m='Stufe Ok', s='ok stf', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='level Ok', s='ok lvl', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='niveau Ok', m='niv Ok', s='ok niv', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='nivel Okay', m='nivel Ok', s='ok nvl', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B00_nolevel':
            en = Dgt.DISPLAY_TEXT(l=None, m='no level', s='no lvl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='keine Stufe', m='keine St', s='kn stf', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='geen level', m='gn level', s='gn lvl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='no niveau', m='niv non', s='no niv', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='sin nivel', m='sinnivel', s='no nvl', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B10_okbook':
            en = Dgt.DISPLAY_TEXT(l='book Okay', m='book Ok', s='okbook', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Buch Okay', m='Buch Ok', s='okbuch', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='boek Ok', m='boek Ok', s='okboek', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='livre Ok', s='ok liv', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='libro Okay', m='libro Ok', s='oklibr', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_noipadr':
            en = Dgt.DISPLAY_TEXT(l='no ip addr', m='no ipadr', s='no ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='keine IPadr', m='keine IP', s='kn ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='geen IP adr', m='geen IP', s='gn ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='pas d ip', s='pd ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='no ip dir', m='no ip', s=None, beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'Y00_errormenu':
            en = Dgt.DISPLAY_TEXT(l='menu error', m='err menu', s='errmen', beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l='menu error', m='err menu', s='errmen', beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='menu fout', m='foutmenu', s='fout m', beep=self.bl(BeepLevel.YES), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='menu error', m='err menu', s='pd men', beep=self.bl(BeepLevel.YES), duration=0)
            es = Dgt.DISPLAY_TEXT(l='menu error', m='err menu', s='errmen', beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B00_sidewhite':
            en = Dgt.DISPLAY_TEXT(l='side move w', m='side w', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='W am Zug', s='w zug', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='wit aan zet', m='wit zet', s='w zet', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='aux blancs', m='mvt bl', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='lado blanco', m='lado w', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_sideblack':
            en = Dgt.DISPLAY_TEXT(l='side move b', m='side b', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='S am Zug', s='s zug', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='zw aan zet', m='zw zet', s='z zet', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='aux noirs', m='mvt n', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='lado negro', m='lado b', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_scanboard':
            en = Dgt.DISPLAY_TEXT(l='scan board', m='scan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='lese Stellg', m='lese Stl', s='lese s', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='scan bord', m='scan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='scan echiq', m='scan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='escan tabl', m='escan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'Y05_illegalpos':
            en = Dgt.DISPLAY_TEXT(l='illegal pos', m='illegal', s='badpos', beep=self.bl(BeepLevel.YES), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l='Pos illegal', m='illegal', s='errpos', beep=self.bl(BeepLevel.YES), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l='ongeldig', m='ongeldig', s='ongeld', beep=self.bl(BeepLevel.YES), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l=None, m='illegale', s='pos il', beep=self.bl(BeepLevel.YES), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l='illegal pos', m='ileg pos', s='ilegpo', beep=self.bl(BeepLevel.YES), duration=0.5)
        if text_id == 'Y00_error960':
            en = Dgt.DISPLAY_TEXT(l='uci960 err', m='960 err', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l='uci960 err', m='960 err', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='uci960 fout', m='960 fout', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='uci960 err', m='960 err', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            es = Dgt.DISPLAY_TEXT(l='uci960 err', m='960 err', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B10_oktime':
            en = Dgt.DISPLAY_TEXT(l='time Okay', m='time Ok', s='oktime', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Zeit Okay', m='Zeit Ok', s='okzeit', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='tyd Ok', m='tyd Ok', s='ok tyd', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='temps Ok', s='tps Ok', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='tiempo Okay', m='tiempo Ok', s='oktime', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_okbeep':
            en = Dgt.DISPLAY_TEXT(l='beep Okay', m='beep Ok', s='okbeep', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='TonSt Okay', m='TonSt Ok', s='ok ton', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='piep Ok', m='piep Ok', s='okpiep', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='sons Ok', s='son Ok', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='beep Okay', m='beep Ok', s='okbeep', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'K05_okpico':
            en = Dgt.DISPLAY_TEXT(l="pico Okay", m="pico Ok", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="pico Okay", m="pico Ok", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l="pico Ok", m="pico Ok", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l=None, m="pico Ok", s="pic Ok", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l="pico Okay", m="pico Ok", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
        if text_id == 'K05_okuser':
            en = Dgt.DISPLAY_TEXT(l="player Okay", m="playerOk", s="okuser", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="Spieler Ok", m="Splr Ok", s="oksplr", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l="speler Ok", m="spelerOk", s="okuser", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l="joueur Ok", m="joueurOk", s="ok jr", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l="jugador Ok", m="jugad Ok", s="okjuga", beep=self.bl(BeepLevel.OKAY), duration=0.5)
        if text_id == 'K05_okmove':
            en = Dgt.DISPLAY_TEXT(l="move Okay", m="move Ok", s="okmove", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="Zug Okay", m="Zug Ok", s=None, beep=self.bl(BeepLevel.OKAY), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l=None, m="zet Ok", s="ok zet", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l=None, m="mouv Ok", s="ok mvt", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l="jugada Okay", m="jugada Ok", s="ok jug", beep=self.bl(BeepLevel.OKAY), duration=0.5)
        if text_id == 'B05_altmove':
            en = Dgt.DISPLAY_TEXT(l="altn move", m="alt move", s="altmov", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="altnatv Zug", m="alt Zug", s="altzug", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l="andere zet", m="alt zet", s="altzet", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l="autre mouv", m="alt move", s="altmov", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l="altn jugada", m="altjugad", s="altjug", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
        if text_id == 'C10_newgame':
            en = Dgt.DISPLAY_TEXT(l=None, m="new game", s="newgam", beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l="neues Spiel", m="neuSpiel", s="neuspl", beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l="nieuw party", m="nw party", s="newspl", beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='nvl partie', m="new game", s="newgam", beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l='nuev partid', m="nuevpart", s="n part", beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'C00_takeback':
            en = Dgt.DISPLAY_TEXT(l=None, m="takeback", s="takbak", beep=self.bl(BeepLevel.CONFIG), duration=0)
            de = Dgt.DISPLAY_TEXT(l="Ruecknahme", m="Ruecknah", s="rueckn", beep=self.bl(BeepLevel.CONFIG), duration=0)
            nl = Dgt.DISPLAY_TEXT(l="zet terug", m="zetterug", s="terug", beep=self.bl(BeepLevel.CONFIG), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m="retour", s=None, beep=self.bl(BeepLevel.CONFIG), duration=0)
            es = Dgt.DISPLAY_TEXT(l='retrocede', m="atras", s=None, beep=self.bl(BeepLevel.CONFIG), duration=0)
        if text_id == 'N10_bookmove':
            en = Dgt.DISPLAY_TEXT(l=None, m="book", s=None, beep=self.bl(BeepLevel.NO), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m="Buch", s=None, beep=self.bl(BeepLevel.NO), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m="boek", s=None, beep=self.bl(BeepLevel.NO), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m="livre", s=None, beep=self.bl(BeepLevel.NO), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m="libro", s=None, beep=self.bl(BeepLevel.NO), duration=1)
        if text_id == 'N00_setpieces':
            en = Dgt.DISPLAY_TEXT(l="set pieces", m="set pcs", s="setpcs", beep=self.bl(BeepLevel.NO), duration=0)
            de = Dgt.DISPLAY_TEXT(l="St aufbauen", m="aufbauen", s="aufbau", beep=self.bl(BeepLevel.NO), duration=0)
            nl = Dgt.DISPLAY_TEXT(l="zet stukken", m="zet stkn", s="zet st", beep=self.bl(BeepLevel.NO), duration=0)
            fr = Dgt.DISPLAY_TEXT(l="placer pcs", m="set pcs", s="setpcs", beep=self.bl(BeepLevel.NO), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m="posicion", s="setpcs", beep=self.bl(BeepLevel.NO), duration=0)
        if text_id == 'Y00_errorjack':
            en = Dgt.DISPLAY_TEXT(l="jack error", m="err jack", s="jack", beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l="Kabel err", m="errKabel", s="errkab", beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l="jack error", m="jack err", s="jack", beep=self.bl(BeepLevel.YES), duration=0)
            fr = Dgt.DISPLAY_TEXT(l="jack error", m="jack err", s="jack", beep=self.bl(BeepLevel.YES), duration=0)
            es = Dgt.DISPLAY_TEXT(l="jack error", m="jack err", s="jack", beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B00_beep':
            en = Dgt.DISPLAY_TEXT(l=None, m='beep ' + msg, s='beep' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='TonStufe ' + msg, m='TonSt ' + msg, s='ton ' + msg, beep=self.bl(BeepLevel.BUTTON),
                                  duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='piep ' + msg, s='piep' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='son ' + msg, s='son ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='beep ' + msg, s='beep' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_level':
            en = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='stf ' + msg, beep=self.bl(BeepLevel.BUTTON),
                                  duration=0)
            nl = en
            fr = Dgt.DISPLAY_TEXT(l='niveau ' + msg, m='niveau' + msg, s='niv ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='nivel ' + msg, s='nvl ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B10_level':
            en = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='stf ' + msg, beep=self.bl(BeepLevel.BUTTON),
                                  duration=1)
            nl = en
            fr = Dgt.DISPLAY_TEXT(l='niveau ' + msg, m='niveau' + msg, s='niv ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='nivel ' + msg, s='nvl ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'M10_level':
            en = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg, beep=self.bl(BeepLevel.MAP), duration=1)
            de = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='stf ' + msg, beep=self.bl(BeepLevel.MAP),
                                  duration=1)
            nl = en
            fr = Dgt.DISPLAY_TEXT(l='niveau ' + msg, m='niveau' + msg, s='niv ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='nivel ' + msg, s='nvl ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B10_mate':
            en = Dgt.DISPLAY_TEXT(l='mate in ' + msg, m='mate ' + msg, s='mate' + msg, beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Matt in ' + msg, m='Matt ' + msg, s='matt' + msg, beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='mat in ' + msg, m='mat ' + msg, s='mat ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='mat en ' + msg, m='mat ' + msg, s=None, beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='mate en ' + msg, m='mate ' + msg, s='mate' + msg, beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_score':
            text_s = 'no scr' if msg is None else str(msg).rjust(6)
            text_m = 'no score' if msg is None else str(msg).rjust(8)
            en = Dgt.DISPLAY_TEXT(l=None, m=text_m, s=text_s, beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = en
            nl = en
            fr = en
            es = en
        if text_id == 'B00_menu_top_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='topmen', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='topmen', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='topmen', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='topmen', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='topmen', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_mode_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='mode', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Modus', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='modus', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='mode', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='modo', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_position_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='position', s='posit', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='positie', m='positie', s='positi', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='position', s='posit', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='posicion', s='posic', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_time_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='time', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Zeit', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='tyd', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='temps', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='tiempo', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_book_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='book', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Buch', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='boek', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='livre', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='libro', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_engine_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='engine', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='engine', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='moteur', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='motor', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_system_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='system', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='System', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='systeem', s='system', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='systeme', s='system', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='sistema', s='sistem', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_normal_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='normaal', m='normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_analysis_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='analysis', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Analyse', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='analyseren', m='analyse', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='analyser', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='analisis', s='analis', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_kibitz_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='evaluer', s='evalue', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_observe_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='observe', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Observe', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='observeren', m='observr', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='observer', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='observa', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_remote_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='remoto', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_timemode_fixed_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='fixed', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='feste Zeit', m='festZeit', s='fest', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='fixed', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='fixe', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='reparado', m='reparado', s='repar', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_timemode_blitz_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_timemode_fischer_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_version_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='version', s='vers', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='versie', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='version', s='vers', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='version', s='vers', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_ipadr_menu':
            en = Dgt.DISPLAY_TEXT(l='IP address', m='IP adr', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='IP adres', s='IP adr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='adr IP', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='IP dir', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_sound_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='sound', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Sound', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='geluid', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='sons', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='sonido', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_language_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Language', s='lang', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Sprache', s='sprach', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='taal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='langue', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='idioma', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_gameresult_mate_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='mate', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Matt', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='mat', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='mat', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='mate', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_stalemate_menu':
            en = Dgt.DISPLAY_TEXT(l='stalemate', m='stalemat', s='stale', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Patt', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='patstelling', m='pat', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='pat', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='ahogado', s='ahogad', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_time_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='time', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Zeit', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='tyd', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='tombe', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='tiempo', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_material_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='material', s='materi', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Material', s='materi', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='materiaal', m='material', s='materi', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='materiel', s='materl', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='material', s='mater', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_moves_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='75 moves', s='75 mov', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='75 Zuege', s='75 zug', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='75 zetten', m='75zetten', s='75 zet', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='75 mouv', s='75 mvt', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='75 mov', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_repetition_menu':
            en = Dgt.DISPLAY_TEXT(l='repetition', m='rep pos', s='reppos', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Wiederholg', m='Wiederho', s='wh pos', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='zetherhaling', m='herhalin', s='herhal', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='3ieme rep', m='3iem rep', s='3 rep', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l='repeticion', m='repite 3', s='rep 3', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_abort_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='abort', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Abbruch', s='abbrch', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='afbreken', s='afbrek', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='sortir', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='abortar', s='abort', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_white_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='w wins', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='W gewinnt', m='W gewinn', s='w gew', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='wit wint', m='wit wint', s='w wint', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='b gagne', s='b gagn', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='b ganan', s='b gana', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_black_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='b wins', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='S gewinnt', m='S gewinn', s='s gew', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='zwart wint', m='zw wint', s='z wint', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='n gagne', s='n gagn', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='n ganan', s='n gana', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_draw_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='draw', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Remis', s='remis', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='remise', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='nulle', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='tablas', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B10_playmode_white_user':
            en = Dgt.DISPLAY_TEXT(l=None, m='white', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Spieler W', m='Spielr W', s='splr w', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='Speler wit', m='Speler w', s='splr w', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='joueur b', m='joueur b', s='blancs', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l='jugador b', m='jugad b', s='juga b', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B10_playmode_black_user':
            en = Dgt.DISPLAY_TEXT(l=None, m='black', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Spieler S', m='Spielr S', s='splr s', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='Speler zw', m='Speler z', s='splr z', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='joueur n', m='joueur n', s='noirs', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l='jugador n', m='jugad n', s='juga n', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_language_en_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='english', s='englsh', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Englisch', s='en', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Engels', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='anglais', s='anglai', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='ingles', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_language_de_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='german', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Deutsch', s='de', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Duits', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='allemand', s='allema', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='aleman', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_language_nl_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='dutch', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='Niederlaend', m='Niederl', s='nl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='Nederlands', m='Nederl', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='neerlandais', m='neerlnd', s='neer', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='holandes', s='holand', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_language_fr_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='french', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='Franzosisch', m='Franzoes', s='fr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Frans', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='francais', m='francais', s='france', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='frances', s='franc', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_language_es_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='spanish', s='spanis', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Spanisch', s='es', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Spaans', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='espagnol', s='espag', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='espanol', s='esp', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B10_oklang':
            en = Dgt.DISPLAY_TEXT(l='lang Okay', m='lang Ok', s='oklang', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Sprache Okay', m='SpracheOk', s='ok spr', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='taal Ok', m='taal Ok', s='oktaal', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='langue Ok', m='lang Ok', s='oklang', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='idioma Ok', m='lang Ok', s='oklang', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if en is None:
            en = Dgt.DISPLAY_TEXT(l=None, m=text_id, s=None, beep=self.bl(BeepLevel.YES), duration=0)
            logging.warning('unknown text_id {}'.format(text_id))
        if self.language == 'de' and de is not None:
            return de
        if self.language == 'nl' and nl is not None:
            return nl
        if self.language == 'fr' and fr is not None:
            return fr
        if self.language == 'es' and es is not None:
            return es
        return en
