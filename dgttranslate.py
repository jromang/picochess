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
    def __init__(self, beep_config, beep_level, language):
        self.ConfigToBeep = {'all' : Beep.ON, 'none' : Beep.OFF, 'some' : Beep.SOME}
        self.beep = self.ConfigToBeep[beep_config]
        self.beep_level = beep_level
        self.language = language

    def beep_to_config(self, beep):
        return dict(zip(self.ConfigToBeep.values(), self.ConfigToBeep.keys()))[beep]

    def bl(self, beeplevel):
        if self.beep == Beep.ON:
            return True
        if self.beep == Beep.OFF:
            return False
        return bool(self.beep_level & beeplevel.value)

    def set_beep(self, beep):
        self.beep = beep

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
        entxt = detxt = nltxt = frtxt = estxt = None  # error case
        bl_button = self.bl(BeepLevel.BUTTON)
        bl_config = self.bl(BeepLevel.CONFIG)
        if text_id == 'B00_default':
            entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], wait=False, beep=bl_button, maxtime=0)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'B10_default':
            entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], wait=False, beep=bl_button, maxtime=1)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'M10_default':
            entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], wait=False, beep=self.bl(BeepLevel.MAP), maxtime=1)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'C10_default':
            entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], wait=False, beep=bl_config, maxtime=1)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'N10_default':
            entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], wait=False, beep=self.bl(BeepLevel.NO), maxtime=1)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'Y10_goodbye':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Good bye', s='bye', wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Tschuess', s='tschau', wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='tot ziens', m='totziens', s='dag', wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='au revoir', m='a plus', s='bye', wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='adios', s=None, wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
        if text_id == 'Y10_pleasewait':
            entxt = Dgt.DISPLAY_TEXT(l='please wait', m='pls wait', s='wait', wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='bitteWarten', m='warten', s=None, wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='wacht even', m='wachten', s='wacht', wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='patientez', m='patience', s='patien', wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='espere', s=None, wait=False, beep=self.bl(BeepLevel.YES), maxtime=1)
        if text_id == 'B10_nomove':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='no move', s='nomove', wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Kein Zug', s='kn zug', wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Geen zet', s='gn zet', wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='pas de mouv', m='pas mvt', s='pasmvt', wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='sin mov', s='no mov', wait=False, beep=bl_button, maxtime=1)
        if text_id == 'B00_wb':
            entxt = Dgt.DISPLAY_TEXT(l=' W       B ', m=' W     B', s='wh  bl', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=' W       S ', m=' W     S', s='we  sc', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=' W       Z ', m=' W     Z', s='wi  zw', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=' B       N ', m=' B     N', s='bl  no', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=' B       N ', m=' B     N', s='bl  ne', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_bw':
            entxt = Dgt.DISPLAY_TEXT(l=' B       W ', m=' B     W', s='bl  wh', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=' S       W ', m=' S     W', s='sc  we', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=' Z       W ', m=' Z     W', s='zw  wi', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=' N       B ', m=' N     B', s='no  bl', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=' N       B ', m=' N     B', s='ne  bl', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_960no':
            entxt = Dgt.DISPLAY_TEXT(l='uci960 no', m='960 no', s='960 no', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='uci960 nein', m='960 nein', s='960 nn', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='uci960 nee', m='960 nee', s='960nee', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='uci960 non', m='960 non', s='960non', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='uci960 no', m='960 no', s='960 no', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_960yes':
            entxt = Dgt.DISPLAY_TEXT(l='uci960 yes', m='960 yes', s='960yes', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='uci960 ja', m='960 ja', s='960 ja', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='uci960 ja', m='960 ja', s='960 ja', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='uci960 oui', m='960 oui', s='960oui', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='uci960 si', m='960 si', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B10_picochess':
            entxt = Dgt.DISPLAY_TEXT(l='picoChs ' + version, m='pico ' + version, s='pic ' + version, wait=False,
                                     beep=bl_button, maxtime=1)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'B00_nofunction':
            entxt = Dgt.DISPLAY_TEXT(l='no function', m='no funct', s='nofunc', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='Keine Funkt', m='KeineFkt', s='kn fkt', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='Geen functie', m='Geen fnc', s='gn fnc', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='no fonction', m='no fonct', s='nofonc', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='sin funcion', m='sin func', s='nofunc', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'Y00_erroreng':
            entxt = Dgt.DISPLAY_TEXT(l='err engine', m='err engn', s='engerr', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='err engine', m='err engn', s='engerr', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='fout engine', m='fout eng', s='e fout', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='err moteur', m='err mot', s='errmot', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='error motor', m='err mot', s='errmot', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
        if text_id == 'B10_okengine':
            entxt = Dgt.DISPLAY_TEXT(l='ok engine', m='okengine', s='ok eng', wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='ok engine', m='okengine', s='ok eng', wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='ok engine', m='okengine', s='ok eng', wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='ok moteur', m='ok mot', s=None, wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='ok motor', m='ok motor', s='ok mot', wait=False, beep=bl_button, maxtime=1)
        if text_id == 'B10_okmode':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok mode', s='okmode', wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok Modus', s='okmode', wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok modus', s='okmode', wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='ok mode', s='okmode', wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ok modo', s='okmodo', wait=False, beep=bl_button, maxtime=1)
        if text_id == 'B10_oklevel':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok level', s='ok lvl', wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok Stufe', s='ok stf', wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok level', s='ok lvl', wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='ok niveau', m='ok niv', s='ok niv', wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ok nivel', s='ok nvl', wait=False, beep=bl_button, maxtime=1)
        if text_id == 'B00_nolevel':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='no level', s='no lvl', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='Keine Stufe', m='Keine St', s='kn stf', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='Geen level', m='Gn level', s='gn lvl', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='no niveau', m='no niv', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='sin nivel', m='sinNivel', s='no nvl', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B10_okbook':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok book', s='okbook', wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok Buch', s='okbuch', wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok boek', s='okboek', wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='ok livre', s='ok liv', wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ok libro', s='oklibr', wait=False, beep=bl_button, maxtime=1)
        if text_id == 'B10_noipadr':
            entxt = Dgt.DISPLAY_TEXT(l='no IP addr', m='no IPadr', s='no ip', wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='Keine IPadr', m='Keine IP', s='kn ip', wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='Geen IPadr', m='Geen IP', s='gn ip', wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='pas d IP', s='pd ip', wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='no IP dir', m='no IP', s=None, wait=False, beep=bl_button, maxtime=1)
        if text_id == 'Y00_errormenu':
            entxt = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='errmen', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='error Menu', m='err Menu', s='errmen', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='fout menu', m='foutmenu', s='fout m', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='pd men', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='errmen', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
        if text_id == 'B00_sidewhite':
            entxt = Dgt.DISPLAY_TEXT(l='side move W', m='side W', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='W am Zug', s='w zug', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='wit aan zet', m='wit zet', s='w zet', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='aux blancs', m='mvt bl', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='lado blanco', m='lado W', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_sideblack':
            entxt = Dgt.DISPLAY_TEXT(l='side move B', m='side B', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='S am Zug', s='s zug', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='zw aan zet', m='zw zet', s='z zet', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='aux noirs', m='mvt n', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='lado negro', m='lado B', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_scanboard':
            entxt = Dgt.DISPLAY_TEXT(l='scan board', m='scan', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='lese Stellg', m='lese Stl', s='lese s', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='scan bord', m='scan', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='scan echiq', m='scan', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='escan tabl', m='escan', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'Y05_illegalpos':
            entxt = Dgt.DISPLAY_TEXT(l='invalid pos', m='invalid', s='badpos', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0.5)
            detxt = Dgt.DISPLAY_TEXT(l='illegalePos', m='illegal', s='errpos', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0.5)
            nltxt = Dgt.DISPLAY_TEXT(l='ongeldig', m='ongeldig', s='ongeld', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0.5)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='illegale', s='pos il', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0.5)
            estxt = Dgt.DISPLAY_TEXT(l='illegal pos', m='ileg pos', s='ilegpo', wait=False, beep=self.bl(BeepLevel.YES), maxtime=0.5)
        if text_id == 'Y00_error960':
            entxt = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s="err960", wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s="err960", wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='fout uci960', m='fout 960', s="err960", wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s="err960", wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s="err960", wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
        if text_id == 'B10_oktime':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok time', s='ok tim', wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok Zeit', s='okzeit', wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok tyd', s='ok tyd', wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='ok temps', s='ok tps', wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='ok tiempo', m='okTiempo', s='ok tpo', wait=False, beep=bl_button, maxtime=1)
        if text_id == 'B10_okbeep':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok beep', s='okbeep', wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok TonSt', s='ok ton', wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok piep', s='okpiep', wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='ok sons', s='oksons', wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ok beep', s='okbeep', wait=False, beep=bl_button, maxtime=1)
        if text_id == 'K05_okpico':
            entxt = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            detxt = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            estxt = Dgt.DISPLAY_TEXT(l=None, m="ok pico", s="okpico", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
        if text_id == 'K05_okuser':
            entxt = Dgt.DISPLAY_TEXT(l="ok player", m="okplayer", s="okplay", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            detxt = Dgt.DISPLAY_TEXT(l="ok Spieler", m="ok Splr", s="oksplr", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            nltxt = Dgt.DISPLAY_TEXT(l="ok Speler", m="okSpeler", s="oksplr", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            frtxt = Dgt.DISPLAY_TEXT(l="ok joueur", m="okjoueur", s="ok jr", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            estxt = Dgt.DISPLAY_TEXT(l="ok usuario", m="okusuari", s="okuser", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
        if text_id == 'K05_okmove':
            entxt = Dgt.DISPLAY_TEXT(l=None, m="ok move", s="okmove", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            detxt = Dgt.DISPLAY_TEXT(l=None, m="ok Zug", s=None, wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m="ok zet", s=None, wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m="ok mouv", s="ok mvt", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
            estxt = Dgt.DISPLAY_TEXT(l=None, m="ok jugada", s="ok jug", wait=True, beep=self.bl(BeepLevel.OKAY), maxtime=0.5)
        if text_id == 'B05_altmove':
            entxt = Dgt.DISPLAY_TEXT(l="altn move", m="alt move", s="altmov", wait=False, beep=bl_button, maxtime=0.5)
            detxt = Dgt.DISPLAY_TEXT(l="altnatv Zug", m="alt Zug", s="altzug", wait=False, beep=bl_button, maxtime=0.5)
            nltxt = Dgt.DISPLAY_TEXT(l="andere zet", m="alt zet", s="altzet", wait=False, beep=bl_button, maxtime=0.5)
            frtxt = Dgt.DISPLAY_TEXT(l="autre mouv", m="alt move", s="altmov", wait=False, beep=bl_button, maxtime=0.5)
            estxt = Dgt.DISPLAY_TEXT(l="altn jugada", m="altjugad", s="altjug", wait=False, beep=bl_button, maxtime=0.5)
        if text_id == 'C10_newgame':
            entxt = Dgt.DISPLAY_TEXT(l=None, m="new Game", s="newgam", wait=False, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l="neues Spiel", m="neuesSpl", s="neuspl", wait=False, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l="nieuw party", m="nw party", s="nwpart", wait=False, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='nvl partie', m="nvl part", s="newgam", wait=False, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='nuev partid', m="nuevpart", s="n part", wait=False, beep=bl_config, maxtime=1)
        if text_id == 'C10_ucigame':
            msg = msg.rjust(3)
            entxt = Dgt.DISPLAY_TEXT(l="new Game" + msg, m="Game " + msg, s="gam" + msg, wait=False, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l="neuSpiel" + msg, m="Spiel" + msg, s="spl" + msg, wait=False, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l="nw party" + msg, m="party" + msg, s="par" + msg, wait=False, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='nvl part' + msg, m="part " + msg, s="gam" + msg, wait=False, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='partid  ' + msg, m="part " + msg, s="par" + msg, wait=False, beep=bl_config, maxtime=1)
        if text_id == 'C00_takeback':
            entxt = Dgt.DISPLAY_TEXT(l=None, m="takeback", s="takbak", wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l="Ruecknahme", m="Rcknahme", s="rueckn", wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l="zet terug", m="zetterug", s="terug", wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m="retour", s=None, wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='retrocede', m="atras", s=None, wait=True, beep=bl_config, maxtime=1)
        if text_id == 'N10_bookmove':
            entxt = Dgt.DISPLAY_TEXT(l=None, m="book", s=None, wait=True, beep=self.bl(BeepLevel.NO), maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m="Buch", s=None, wait=True, beep=self.bl(BeepLevel.NO), maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m="boek", s=None, wait=True, beep=self.bl(BeepLevel.NO), maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m="livre", s=None, wait=True, beep=self.bl(BeepLevel.NO), maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m="libro", s=None, wait=True, beep=self.bl(BeepLevel.NO), maxtime=1)
        if text_id == 'N00_setpieces':
            entxt = Dgt.DISPLAY_TEXT(l="set pieces", m="set pcs", s="setpcs", wait=True, beep=self.bl(BeepLevel.NO), maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l="St aufbauen", m="aufbauen", s="aufbau", wait=True, beep=self.bl(BeepLevel.NO), maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l="zet stukken", m="zet stkn", s="zet st", wait=True, beep=self.bl(BeepLevel.NO), maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l="placer pcs", m="set pcs", s="setpcs", wait=True, beep=self.bl(BeepLevel.NO), maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l="hasta piez", m="hasta pz", s="hastap", wait=True, beep=self.bl(BeepLevel.NO), maxtime=0)
        if text_id == 'Y00_errorjack':
            entxt = Dgt.DISPLAY_TEXT(l="error jack", m="err jack", s="jack", wait=True, beep=self.bl(BeepLevel.YES), maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l="err Kabel", m="errKabel", s="errkab", wait=True, beep=self.bl(BeepLevel.YES), maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l="fout Kabel", m="errKabel", s="errkab", wait=True, beep=self.bl(BeepLevel.YES), maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l="jack error", m="jack err", s="jack", wait=True, beep=self.bl(BeepLevel.YES), maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l="jack error", m="jack err", s="jack", wait=True, beep=self.bl(BeepLevel.YES), maxtime=0)
        if text_id == 'B00_level':
            if msg.startswith('Elo@'):
                msg = str(int(msg[4:])).rjust(4)
                entxt = Dgt.DISPLAY_TEXT(l=None, m='Elo ' + msg, s='el' + msg, wait=False, beep=bl_button, maxtime=0)
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
            elif msg.startswith('Level@'):
                msg = str(int(msg[6:])).rjust(2)
                entxt = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg, wait=False, beep=bl_button, maxtime=0)
                detxt = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='stf ' + msg, wait=False, beep=bl_button, maxtime=0)
                nltxt = entxt
                frtxt = Dgt.DISPLAY_TEXT(l='niveau ' + msg, m='niveau' + msg, s='niv ' + msg, wait=False, beep=bl_button, maxtime=0)
                estxt = Dgt.DISPLAY_TEXT(l=None, m='nivel ' + msg, s='nvl ' + msg, wait=False, beep=bl_button, maxtime=0)
            else:
                entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], wait=False, beep=bl_button, maxtime=0)
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
        if text_id == 'B10_level':
            if msg.startswith('Elo@'):
                msg = str(int(msg[4:])).rjust(4)
                entxt = Dgt.DISPLAY_TEXT(l=None, m='Elo ' + msg, s='el' + msg, wait=False, beep=bl_button, maxtime=1)
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
            elif msg.startswith('Level@'):
                msg = str(int(msg[6:])).rjust(2)
                entxt = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg, wait=False, beep=bl_button, maxtime=1)
                detxt = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='stf ' + msg, wait=False, beep=bl_button, maxtime=1)
                nltxt = entxt
                frtxt = Dgt.DISPLAY_TEXT(l='niveau ' + msg, m='niveau' + msg, s='niv ' + msg, wait=False, beep=bl_button, maxtime=1)
                estxt = Dgt.DISPLAY_TEXT(l=None, m='nivel ' + msg, s='nvl ' + msg, wait=False, beep=bl_button, maxtime=1)
            else:
                entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], wait=False, beep=bl_button, maxtime=1)
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
        if text_id == 'M10_level':
            if msg.startswith('Elo@'):
                msg = str(int(msg[4:])).rjust(4)
                entxt = Dgt.DISPLAY_TEXT(l=None, m='Elo ' + msg, s='el' + msg, wait=False, beep=self.bl(BeepLevel.MAP), maxtime=1)
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
            elif msg.startswith('Level@'):
                msg = str(int(msg[6:])).rjust(2)
                entxt = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg, wait=False, beep=self.bl(BeepLevel.MAP), maxtime=1)
                detxt = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='stf ' + msg, wait=False, beep=self.bl(BeepLevel.MAP),
                                         maxtime=1)
                nltxt = entxt
                frtxt = Dgt.DISPLAY_TEXT(l='niveau ' + msg, m='niveau' + msg, s='niv ' + msg, wait=False, beep=bl_button, maxtime=1)
                estxt = Dgt.DISPLAY_TEXT(l=None, m='nivel ' + msg, s='nvl ' + msg, wait=False, beep=bl_button, maxtime=1)
            else:
                entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], wait=False, beep=self.bl(BeepLevel.MAP), maxtime=1)
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
        if text_id == 'B10_mate':
            entxt = Dgt.DISPLAY_TEXT(l='mate in ' + msg, m='mate ' + msg, s='mate' + msg, wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='Matt in ' + msg, m='Matt ' + msg, s='matt' + msg, wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='mat in ' + msg, m='mat ' + msg, s='mat ' + msg, wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='mat en ' + msg, m='mat ' + msg, s=None, wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='mate en ' + msg, m='mate ' + msg, s='mate' + msg, wait=False, beep=bl_button, maxtime=1)
        if text_id == 'B10_score':
            text_s = 'no scr' if msg is None else str(msg).rjust(6)
            text_m = 'no score' if msg is None else str(msg).rjust(8)
            entxt = Dgt.DISPLAY_TEXT(l=None, m=text_m, s=text_s, wait=False, beep=bl_button, maxtime=1)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'B00_menu_top_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='Haupt Menu', m='Hpt Menu', s='topmen', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_menu_mode_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Mode', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Modus', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Modus', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Mode', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Modo', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_menu_position_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Stelling', s='stelng', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Posicion', s='posic', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_menu_time_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Time', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Zeit', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Tyd', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Temps', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Tiempo', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_menu_book_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Book', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Buch', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Boek', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Livre', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Libro', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_menu_engine_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Moteur', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Motor', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_menu_system_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='System', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='System', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Systeem', s='system', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Systeme', s='system', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Sistema', s='sistem', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_mode_normal_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Normal', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Normal', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Normaal', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_mode_analysis_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Analysis', s='analys', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Analyse', s='analys', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='Analyseren', m='Analyse', s='analys', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Analyser', s='analys', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Analisis', s='analis', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_mode_kibitz_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Evaluer', s='evalue', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_mode_observe_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Observe', s='observ', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Observe', s='observ', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='Observeren', m='Observr', s='observ', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Observer', s='observ', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Observa', s='observ', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_mode_remote_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Remoto', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_timemode_fixed_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Fixed', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='ZeitproZug', m='Zeit/Zug', s='fest', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Fixed', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Fixe', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Reparado', s='repar', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_timemode_blitz_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_timemode_fischer_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_settings_version_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Versie', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_settings_ipadr_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='IP address', m='IP adr', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Adr IP', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='IP dir', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_settings_sound_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Sound', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Toene', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Geluid', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Sons', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Sonido', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_settings_language_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Language', s='lang', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Sprache', s='sprach', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Taal', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Langue', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Idioma', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_gameresult_mate_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='mate', s=None, wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Matt', s=None, wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='mat', s=None, wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='mat', s=None, wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='mate', s=None, wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_gameresult_stalemate_menu':
            entxt = Dgt.DISPLAY_TEXT(l='stalemate', m='stalemat', s='stale', wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Patt', s=None, wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='patstelling', m='pat', s=None, wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='pat', s=None, wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ahogado', s='ahogad', wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_gameresult_time_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='time', s=None, wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Zeit', s=None, wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='tyd', s=None, wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='tombe', s=None, wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='tiempo', s=None, wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_gameresult_material_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='material', s='materi', wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Material', s='materi', wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='materiaal', m='material', s='materi', wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='materiel', s='materl', wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='material', s='mater', wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_gameresult_moves_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='75 moves', s='75 mov', wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='75 Zuege', s='75 zug', wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='75 zetten', m='75zetten', s='75 zet', wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='75 mouv', s='75 mvt', wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='75 mov', s=None, wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_gameresult_repetition_menu':
            entxt = Dgt.DISPLAY_TEXT(l='repetition', m='rep pos', s='reppos', wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='Wiederholg', m='Wiederhg', s='wh pos', wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='zetherhaling', m='herhalin', s='herhal', wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='3ieme rep', m='3iem rep', s='3 rep', wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='repeticion', m='repite 3', s='rep 3', wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_gameresult_abort_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='abort', s=None, wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Abbruch', s='abbrch', wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='afbreken', s='afbrek', wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='sortir', s=None, wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='abortar', s='abort', wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_gameresult_white_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='W wins', s=None, wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='W gewinnt', m='W gewinn', s='w gew', wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='wit wint', m='wit wint', s='w wint', wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='B gagne', s='b gagn', wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='B ganan', s='b gana', wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_gameresult_black_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='B wins', s=None, wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='S gewinnt', m='S gewinn', s='s gew', wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='zwart wint', m='zw wint', s='z wint', wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='N gagne', s='n gagn', wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='N ganan', s='n gana', wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_gameresult_draw_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='draw', s=None, wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Remis', s='remis', wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='remise', s=None, wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='nulle', s=None, wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='tablas', s=None, wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B10_playmode_white_user':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='player W', s='white', wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='Spieler W', m='SpielerW', s='splr w', wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='speler wit', m='speler W', s='splr w', wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='joueur B', m='joueur B', s='blancs', wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='jugador B', m='jugad B', s='juga b', wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B10_playmode_black_user':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='player B', s='black', wait=True, beep=bl_config, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='Spieler S', m='SpielerS', s='splr s', wait=True, beep=bl_config, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l='speler zw', m='speler z', s='splr z', wait=True, beep=bl_config, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='joueur n', m='joueur n', s='noirs', wait=True, beep=bl_config, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='jugador n', m='jugad n', s='juga n', wait=True, beep=bl_config, maxtime=1)
        if text_id == 'B00_language_en_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='English', s='englsh', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Englisch', s='en', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Engels', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Anglais', s='anglai', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Ingles', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_language_de_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='German', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Deutsch', s='de', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Duits', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Allemand', s='allema', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Aleman', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_language_nl_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Dutch', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='Niederldsch', m='Niederl', s='nl', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l='Nederlands', m='Nederl', wait=False, s=None, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l='Neerlandais', m='Neerlnd', s='neer', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Holandes', s='holand', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_language_fr_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='French', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l='Franzosisch', m='Franzsch', s='fr', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Frans', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Francais', s='france', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Frances', s='franc', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_language_es_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Spanish', s='spanis', wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Spanisch', s='es', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Spaans', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Espagnol', s='espag', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Espanol', s='esp', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_beep_off_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Never', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Nie', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Nooit', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Jamais', s=None, wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Nunca', s=None, wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_beep_some_menu':
            entxt = Dgt.DISPLAY_TEXT(l='Sometimes', m='Some', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Manchmal', s='manch', wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Soms', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Parfois', s='parfoi', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='A veces', s='aveces', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B00_beep_on_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Always', s=None, wait=False, beep=bl_button, maxtime=0)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Immer', s=None, wait=False, beep=bl_button, maxtime=0)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Altyd', s=None, wait=False, beep=bl_button, maxtime=0)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Toujours', s='toujou', wait=False, beep=bl_button, maxtime=0)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Siempre', s='siempr', wait=False, beep=bl_button, maxtime=0)
        if text_id == 'B10_oklang':
            entxt = Dgt.DISPLAY_TEXT(l='ok language', m='ok lang', s='oklang', wait=False, beep=bl_button, maxtime=1)
            detxt = Dgt.DISPLAY_TEXT(l='ok Sprache', m='okSprach', s='ok spr', wait=False, beep=bl_button, maxtime=1)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok taal', s='oktaal', wait=False, beep=bl_button, maxtime=1)
            frtxt = Dgt.DISPLAY_TEXT(l='ok langue', m='okLangue', s='oklang', wait=False, beep=bl_button, maxtime=1)
            estxt = Dgt.DISPLAY_TEXT(l='ok idioma', m='okIdioma', s='oklang', wait=False, beep=bl_button, maxtime=1)
        if text_id == 'B00_tc_fixed':
            entxt = Dgt.DISPLAY_TEXT(l='Fixed  ' + msg, m='Fixd' + msg, s='mov' + msg, wait=False, beep=bl_button, maxtime=0)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'B00_tc_blitz':
            entxt = Dgt.DISPLAY_TEXT(l='Blitz  ' + msg, m='Bltz' + msg, s='bl' + msg, wait=False, beep=bl_button, maxtime=0)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'B00_tc_fisch':
            entxt = Dgt.DISPLAY_TEXT(l='Fischr' + msg, m='Fsh' + msg, s='f' + msg, wait=False, beep=bl_button, maxtime=0)
            detxt = entxt 
            nltxt = entxt 
            frtxt = entxt 
            estxt = entxt 
        if entxt is None:
            entxt = Dgt.DISPLAY_TEXT(l=None, m=text_id, s=None, wait=False, beep=self.bl(BeepLevel.YES), maxtime=0)
            logging.warning('unknown text_id {}'.format(text_id))
        if self.language == 'de' and detxt is not None:
            return detxt
        if self.language == 'nl' and nltxt is not None:
            return nltxt
        if self.language == 'fr' and frtxt is not None:
            return frtxt
        if self.language == 'es' and estxt is not None:
            return estxt
        return entxt
