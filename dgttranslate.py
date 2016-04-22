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
            en = Dgt.DISPLAY_TEXT(l=None, m='Good bye', s='bye', beep=self.bl(BeepLevel.YES), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Tschuess', s='tschau', beep=self.bl(BeepLevel.YES), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='tot ziens', m='totziens', s='dag', beep=self.bl(BeepLevel.YES), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='au revoir', m='a plus', s='bye', beep=self.bl(BeepLevel.YES), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='adios', s=None, beep=self.bl(BeepLevel.YES), duration=1)
        if text_id == 'Y10_pleasewait':
            en = Dgt.DISPLAY_TEXT(l='please wait', m='pls wait', s='wait', beep=self.bl(BeepLevel.YES), duration=1)
            de = Dgt.DISPLAY_TEXT(l='bitteWarten', m='warten', s=None, beep=self.bl(BeepLevel.YES), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='wacht even', m='wachten', s='wacht', beep=self.bl(BeepLevel.YES), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='patientez', m='patience', s='patien', beep=self.bl(BeepLevel.YES), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='espere', s=None, beep=self.bl(BeepLevel.YES), duration=1)
        if text_id == 'B10_nomove':
            en = Dgt.DISPLAY_TEXT(l=None, m='no move', s='nomove', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Kein Zug', s='kn zug', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Geen zet', s='gn zet', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='pas de mouv', m='pas mvt', s='pasmvt', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='sin mov', s='no mov', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B00_wb':
            en = Dgt.DISPLAY_TEXT(l=' W       B ', m=' W     B', s='wh  bl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=' W       S ', m=' W     S', s='we  sc', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=' W       Z ', m=' W     Z', s='wi  zw', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=' B       N ', m=' B     N', s='bl  no', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=' B       N ', m=' B     N', s='bl  ne', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_bw':
            en = Dgt.DISPLAY_TEXT(l=' B       W ', m=' B     W', s='bl  wh', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=' S       W ', m=' S     W', s='sc  we', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=' Z       W ', m=' Z     W', s='zw  wi', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=' N       B ', m=' N     B', s='no  bl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=' N       B ', m=' N     B', s='ne  bl', beep=self.bl(BeepLevel.BUTTON), duration=0)
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
            de = Dgt.DISPLAY_TEXT(l='Keine Funkt', m='KeineFkt', s='kn fkt', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='Geen functie', m='Geen fnc', s='gn fnc', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='no fonction', m='no fonct', s='nofonc', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='sin funcion', m='sin func', s='nofunc', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'Y00_erroreng':
            en = Dgt.DISPLAY_TEXT(l='err engine', m='err engn', s='engerr', beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l='err engine', m='err engn', s='engerr', beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='fout engine', m='fout eng', s='e fout', beep=self.bl(BeepLevel.YES), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='err moteur', m='err mot', s='errmot', beep=self.bl(BeepLevel.YES), duration=0)
            es = Dgt.DISPLAY_TEXT(l='error motor', m='err mot', s='errmot', beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B10_okengine':
            en = Dgt.DISPLAY_TEXT(l='ok engine', m='okengine', s='ok eng', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='ok engine', m='okengine', s='ok eng', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='ok engine', m='okengine', s='ok eng', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='ok moteur', m='ok mot', s=None, beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='ok motor', m='ok motor', s='ok mot', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_okmode':
            en = Dgt.DISPLAY_TEXT(l=None, m='ok mode', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='ok Modus', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='ok modus', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='ok mode', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='ok modo', s='okmodo', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_oklevel':
            en = Dgt.DISPLAY_TEXT(l=None, m='ok level', s='ok lvl', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='ok Stufe', s='ok stf', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='ok level', s='ok lvl', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='ok niveau', m='ok niv', s='ok niv', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='ok nivel', s='ok nvl', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B00_nolevel':
            en = Dgt.DISPLAY_TEXT(l=None, m='no level', s='no lvl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='Keine Stufe', m='Keine St', s='kn stf', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='Geen level', m='Gn level', s='gn lvl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='no niveau', m='no niv', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='sin nivel', m='sinNivel', s='no nvl', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B10_okbook':
            en = Dgt.DISPLAY_TEXT(l=None, m='ok book', s='okbook', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='ok Buch', s='okbuch', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='ok boek', s='okboek', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='ok livre', s='ok liv', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='ok libro', s='oklibr', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_noipadr':
            en = Dgt.DISPLAY_TEXT(l='no IP addr', m='no IPadr', s='no ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Keine IPadr', m='Keine IP', s='kn ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='Geen IPadr', m='Geen IP', s='gn ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='pas d IP', s='pd ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='no IP dir', m='no IP', s=None, beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'Y00_errormenu':
            en = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='errmen', beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='errmen', beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='fout menu', m='foutmenu', s='fout m', beep=self.bl(BeepLevel.YES), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='pd men', beep=self.bl(BeepLevel.YES), duration=0)
            es = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='errmen', beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B00_sidewhite':
            en = Dgt.DISPLAY_TEXT(l='side move W', m='side W', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='W am Zug', s='w zug', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='wit aan zet', m='wit zet', s='w zet', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='aux blancs', m='mvt bl', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='lado blanco', m='lado W', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_sideblack':
            en = Dgt.DISPLAY_TEXT(l='side move B', m='side B', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='S am Zug', s='s zug', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='zw aan zet', m='zw zet', s='z zet', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='aux noirs', m='mvt n', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='lado negro', m='lado B', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_scanboard':
            en = Dgt.DISPLAY_TEXT(l='scan board', m='scan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='lese Stellg', m='lese Stl', s='lese s', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='scan bord', m='scan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='scan echiq', m='scan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l='escan tabl', m='escan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'Y05_illegalpos':
            en = Dgt.DISPLAY_TEXT(l='invalid pos', m='invalid', s='badpos', beep=self.bl(BeepLevel.YES), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l='illegalePos', m='illegal', s='errpos', beep=self.bl(BeepLevel.YES), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l='ongeldig', m='ongeldig', s='ongeld', beep=self.bl(BeepLevel.YES), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l=None, m='illegale', s='pos il', beep=self.bl(BeepLevel.YES), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l='illegal pos', m='ileg pos', s='ilegpo', beep=self.bl(BeepLevel.YES), duration=0.5)
        if text_id == 'Y00_error960':
            en = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='fout uci960', m='fout 960', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            es = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B10_oktime':
            en = Dgt.DISPLAY_TEXT(l=None, m='ok time', s='ok tim', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='ok Zeit', s='okzeit', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='ok tyd', s='ok tyd', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='ok temps', s='ok tps', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='ok tiempo', m='okTiempo', s='ok tpo', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_okbeep':
            en = Dgt.DISPLAY_TEXT(l=None, m='ok beep', s='okbeep', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='ok TonSt', s='ok ton', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='ok piep', s='okpiep', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='ok sons', s='oksons', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='ok beep', s='okbeep', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'K05_okpico':
            en = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
        if text_id == 'K05_okuser':
            en = Dgt.DISPLAY_TEXT(l="ok player", m="okplayer", s="okplay", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="ok Spieler", m="ok Splr", s="oksplr", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l="ok Speler", m="okSpeler", s="oksplr", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l="ok joueur", m="okjoueur", s="ok jr", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l="ok usuario", m="okusuari", s="okuser", beep=self.bl(BeepLevel.OKAY), duration=0.5)
        if text_id == 'K05_okmove':
            en = Dgt.DISPLAY_TEXT(l=None, m="ok move", s="okmove", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l=None, m="ok Zug", s=None, beep=self.bl(BeepLevel.OKAY), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l=None, m="ok zet", s=None, beep=self.bl(BeepLevel.OKAY), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l=None, m="ok mouv", s="ok mvt", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l=None, m="ok jugada", s="ok jug", beep=self.bl(BeepLevel.OKAY), duration=0.5)
        if text_id == 'B05_altmove':
            en = Dgt.DISPLAY_TEXT(l="altn move", m="alt move", s="altmov", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="altnatv Zug", m="alt Zug", s="altzug", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l="andere zet", m="alt zet", s="altzet", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            fr = Dgt.DISPLAY_TEXT(l="autre mouv", m="alt move", s="altmov", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            es = Dgt.DISPLAY_TEXT(l="altn jugada", m="altjugad", s="altjug", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
        if text_id == 'C10_newgame':
            en = Dgt.DISPLAY_TEXT(l=None, m="new Game", s="newgam", beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l="neues Spiel", m="neuSpiel", s="neuspl", beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l="nieuw party", m="nw party", s="nwpart", beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='nvl partie', m="nvl part", s="newgam", beep=self.bl(BeepLevel.CONFIG), duration=1)
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
            es = Dgt.DISPLAY_TEXT(l="hasta piez", m="hasta pz", s="hastap", beep=self.bl(BeepLevel.NO), duration=0)
        if text_id == 'Y00_errorjack':
            en = Dgt.DISPLAY_TEXT(l="error jack", m="err jack", s="jack", beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l="err Kabel", m="errKabel", s="errkab", beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l="fout Kabel", m="errKabel", s="errkab", beep=self.bl(BeepLevel.YES), duration=0)
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
            en = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_mode_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Mode', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Modus', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Modus', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Mode', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Modo', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_position_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Stelling', s='stelng', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Posicion', s='posic', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_time_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Time', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Zeit', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Tyd', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Temps', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Tiempo', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_book_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Book', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Buch', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Boek', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Livre', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Libro', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_engine_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Moteur', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Motor', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_system_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='System', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='System', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Systeem', s='system', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Systeme', s='system', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Sistema', s='sistem', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_normal_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Normaal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_analysis_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Analysis', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Analyse', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='Analyseren', m='Analyse', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Analyser', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Analisis', s='analis', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_kibitz_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Evaluer', s='evalue', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_observe_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Observe', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Observe', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='Observeren', m='Observr', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Observer', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Observa', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_remote_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Remoto', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_timemode_fixed_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Fixed', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='ZeitproZug', m='Zeit/Zug', s='fest', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Fixed', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Fixe', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Reparado', s='repar', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_timemode_blitz_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_timemode_fischer_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_version_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Versie', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_ipadr_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='IP address', m='IP adr', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Adr IP', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='IP dir', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_sound_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Sound', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Sound', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Geluid', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Sons', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Sonido', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_language_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Language', s='lang', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Sprache', s='sprach', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Taal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Langue', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Idioma', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
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
            en = Dgt.DISPLAY_TEXT(l=None, m='W wins', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='W gewinnt', m='W gewinn', s='w gew', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='wit wint', m='wit wint', s='w wint', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='B gagne', s='b gagn', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='B ganan', s='b gana', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_black_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='B wins', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='S gewinnt', m='S gewinn', s='s gew', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='zwart wint', m='zw wint', s='z wint', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='N gagne', s='n gagn', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='N ganan', s='n gana', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_draw_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='draw', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Remis', s='remis', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='remise', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l=None, m='nulle', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l=None, m='tablas', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B10_playmode_white_user':
            en = Dgt.DISPLAY_TEXT(l=None, m='player W', s='white', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Spieler W', m='SpielerW', s='splr w', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='speler wit', m='speler W', s='splr w', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='joueur B', m='joueur B', s='blancs', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l='jugador B', m='jugad B', s='juga b', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B10_playmode_black_user':
            en = Dgt.DISPLAY_TEXT(l=None, m='player B', s='black', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Spieler S', m='SpielerS', s='splr s', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='speler zw', m='speler z', s='splr z', beep=self.bl(BeepLevel.CONFIG), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='joueur n', m='joueur n', s='noirs', beep=self.bl(BeepLevel.CONFIG), duration=1)
            es = Dgt.DISPLAY_TEXT(l='jugador n', m='jugad n', s='juga n', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_language_en_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='English', s='englsh', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Englisch', s='en', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Engels', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Anglais', s='anglai', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Ingles', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_language_de_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='German', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Deutsch', s='de', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Duits', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Allemand', s='allema', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Aleman', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_language_nl_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Dutch', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='Niederlaend', m='Niederl', s='nl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='Nederlands', m='Nederl', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l='Neerlandais', m='Neerlnd', s='neer', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Holandes', s='holand', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_language_fr_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='French', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='Franzosisch', m='Franzoes', s='fr', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Frans', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Francais', s='france', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Frances', s='franc', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_language_es_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='Spanish', s='spanis', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Spanisch', s='es', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='Spaans', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            fr = Dgt.DISPLAY_TEXT(l=None, m='Espagnol', s='espag', beep=self.bl(BeepLevel.BUTTON), duration=0)
            es = Dgt.DISPLAY_TEXT(l=None, m='Espanol', s='esp', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B10_oklang':
            en = Dgt.DISPLAY_TEXT(l='ok language', m='ok lang', s='oklang', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='ok Sprache', m='okSprach', s='ok spr', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='ok taal', s='oktaal', beep=self.bl(BeepLevel.BUTTON), duration=1)
            fr = Dgt.DISPLAY_TEXT(l='ok langue', m='okLangue', s='oklang', beep=self.bl(BeepLevel.BUTTON), duration=1)
            es = Dgt.DISPLAY_TEXT(l='ok idioma', m='okIdioma', s='oklang', beep=self.bl(BeepLevel.BUTTON), duration=1)
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
