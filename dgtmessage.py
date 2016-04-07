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


class DgtMessage(object):
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

    def text(self, text_id, msg=''):
        en = de = nl = None  # error case
        if text_id == 'B00_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = en
            nl = en
        if text_id == 'B10_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = en
            nl = en
        if text_id == 'M10_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.MAP), duration=1)
            de = en
            nl = en
        if text_id == 'C10_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = en
            nl = en
        if text_id == 'N10_default':
            en = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6], beep=self.bl(BeepLevel.NO), duration=1)
            de = en
            nl = en
        if text_id == 'Y10_goodbye':
            en = Dgt.DISPLAY_TEXT(l=None, m='good bye', s='bye', beep=self.bl(BeepLevel.YES), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Tschuess', s='bye', beep=self.bl(BeepLevel.YES), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='goedendag', m='doeidoei', s='dagdag', beep=self.bl(BeepLevel.YES), duration=1)
        if text_id == 'Y10_pleasewait':
            en = Dgt.DISPLAY_TEXT(l='please wait', m='pls wait', s='wait', beep=self.bl(BeepLevel.YES), duration=1)
            de = Dgt.DISPLAY_TEXT(l='wartem', m='warten', s='wait', beep=self.bl(BeepLevel.YES), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='wacht even', m='wachten', s='wacht', beep=self.bl(BeepLevel.YES), duration=1)
        if text_id == 'B10_nomove':
            en = Dgt.DISPLAY_TEXT(l=None, m='no move', s='nomove', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='kein Zug', s='nomove', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='geen zet', s='gn zet', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B00_wb':
            en = Dgt.DISPLAY_TEXT(l=None, m=' w     b', s='w    b', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m=' w     s', s='w    s', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m=' w     z', s='w    z', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_bw':
            en = Dgt.DISPLAY_TEXT(l=None, m=' b     w', s='b    w', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m=' s     w', s='s    w', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m=' z     w', s='z    w', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_960no':
            en = Dgt.DISPLAY_TEXT(l=None, m='960 no', s='960 no', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='960 nein', s='960 no', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='960 nee', s='960nee', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_960yes':
            en = Dgt.DISPLAY_TEXT(l=None, m='960 yes', s='960yes', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='960 ja', s='960 ja', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='960 ja', s='960 ja', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B10_picochess':
            en = Dgt.DISPLAY_TEXT(l='picoChs ' + version, m='pico ' + version, s='pic ' + version,
                                  beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = en
            nl = en
        if text_id == 'B00_nofunction':
            en = Dgt.DISPLAY_TEXT(l='no function', m='no funct', s='nofunc', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='keine Funkt', m='keineFkt', s='nofunc', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='geen functie', m='geen fnc', s='gn fnc', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'Y00_erroreng':
            en = Dgt.DISPLAY_TEXT(l='err engine', m='error', s=None, beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l='err engine', m='err eng', s='error', beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='engine fout', m='eng fout', s='e fout', beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B10_okengine':
            en = Dgt.DISPLAY_TEXT(l='okay engine', m='ok engin', s='ok eng', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='okay engine', m='ok engin', s='ok eng', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='oke engine', m='okengine', s='ok eng', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_okmode':
            en = Dgt.DISPLAY_TEXT(l='okay mode', m='ok mode', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='okay Modus', m='ok Modus', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='okay mode', m='ok mode', s='okmode', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_oklevel':
            en = Dgt.DISPLAY_TEXT(l='okay level', m='ok level', s='ok lvl', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='okay Stufe', m='ok Stufe', s='ok lvl', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='oke level', m='ok level', s='ok lvl', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B00_nolevel':
            en = Dgt.DISPLAY_TEXT(l=None, m='no level', s='no lvl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='keine Stufe', m='keine St', s='no lvl', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='geen level', m='gn level', s='no lvl', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B10_okbook':
            en = Dgt.DISPLAY_TEXT(l='okay book', m='ok book', s='okbook', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='okay Buch', m='ok Buch', s='okbook', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='okay boek', m='ok boek', s='okboek', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_noipadr':
            en = Dgt.DISPLAY_TEXT(l='no ip addr', m='no ipadr', s='no ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='keine IPadr', m='keine IP', s='no ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='geen IPadr', m='geen IP', s='gn ip', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'Y00_errormenu':
            en = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='errmen', beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='errmen', beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='menu fout', m='men fout', s='m fout', beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B00_sidewhite':
            en = Dgt.DISPLAY_TEXT(l='side move w', m='side w', s='side w', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='W am Zug', m='W am Zug', s='side w', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='w aan beurt', m='w beurt', s='w brt', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_sideblack':
            en = Dgt.DISPLAY_TEXT(l='side move b', m='side b', s='side b', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='S am Zug', m='S am Zug', s='side b', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='z aan beurt', m='z beurt', s='z brt', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_scanboard':
            en = Dgt.DISPLAY_TEXT(l='scan board', m='scan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='lese Stellg', m='lese Stl', s='scan', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='scan bord', m='scan', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'Y05_illegalpos':
            en = Dgt.DISPLAY_TEXT(l='illegal pos', m='illegal', s='badpos', beep=self.bl(BeepLevel.YES), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l='illegal Pos', m='illegal', s='badpos', beep=self.bl(BeepLevel.YES), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l='ongeldig', m='ongeldig', s='ongeld', beep=self.bl(BeepLevel.YES), duration=0.5)
        if text_id == 'Y00_error960':
            en = Dgt.DISPLAY_TEXT(l='error 960', m='err 960', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l='error 960', m='err 960', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='fout 960', m='fout 960', s="err960", beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B10_oktime':
            en = Dgt.DISPLAY_TEXT(l='okay time', m='ok time', s='oktime', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='okay Zeit', m='ok Zeit', s='okzeit', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='oke tijd', m='oke tijd', s='oktijd', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_okbeep':
            en = Dgt.DISPLAY_TEXT(l='okay beep', m='ok beep', s='okbeep', beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='okay Toene', m='ok Ton', s='ok Ton', beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='oke piep', m='oke piep', s='okpiep', beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'K05_okpico':
            en = Dgt.DISPLAY_TEXT(l="okay pico", m="ok pico", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="okay pico", m="ok pico", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l="oke pico", m="oke pico", s="okpico", beep=self.bl(BeepLevel.OKAY), duration=0.5)
        if text_id == 'K05_okuser':
            en = Dgt.DISPLAY_TEXT(l="okay user", m="ok user", s="okuser", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="okay user", m="ok user", s="okuser", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l="oke user", m="oke user", s="okuser", beep=self.bl(BeepLevel.OKAY), duration=0.5)
        if text_id == 'K05_okmove':
            en = Dgt.DISPLAY_TEXT(l="okay move", m="ok move", s="okmove", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="okay Zug", m="okay Zug", s="ok zug", beep=self.bl(BeepLevel.OKAY), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l="oke zet", m="oke zet", s="ok zet", beep=self.bl(BeepLevel.OKAY), duration=0.5)
        if text_id == 'B05_altmove':
            en = Dgt.DISPLAY_TEXT(l="altn move", m="alt move", s="altmov", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            de = Dgt.DISPLAY_TEXT(l="altnatv Zug", m="alt Zug", s="altmov", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
            nl = Dgt.DISPLAY_TEXT(l="andere zet", m="alt zet", s="altzet", beep=self.bl(BeepLevel.BUTTON), duration=0.5)
        if text_id == 'C10_newgame':
            en = Dgt.DISPLAY_TEXT(l=None, m="new game", s="newgam", beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l="neues Spiel", m="neuSpiel", s="newgam", beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l="nieuw spel", m="new spel", s="newspl", beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'C00_takeback':
            en = Dgt.DISPLAY_TEXT(l=None, m="takeback", s="takbak", beep=self.bl(BeepLevel.CONFIG), duration=0)
            de = Dgt.DISPLAY_TEXT(l="Ruecknahme", m="Ruecknah", s="takbak", beep=self.bl(BeepLevel.CONFIG), duration=0)
            nl = Dgt.DISPLAY_TEXT(l="zet terug", m="zetterug", s="terug", beep=self.bl(BeepLevel.CONFIG), duration=0)
        if text_id == 'N10_bookmove':
            en = Dgt.DISPLAY_TEXT(l="book move", m="book mov", s="book", beep=self.bl(BeepLevel.NO), duration=1)
            de = Dgt.DISPLAY_TEXT(l="Buch", m="Buch", s="book", beep=self.bl(BeepLevel.NO), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m="boek", s=None, beep=self.bl(BeepLevel.NO), duration=1)
        if text_id == 'N00_setpieces':
            en = Dgt.DISPLAY_TEXT(l="set pieces", m="set pcs", s="setpcs", beep=self.bl(BeepLevel.NO), duration=0)
            de = Dgt.DISPLAY_TEXT(l="Stellg aufb", m="Stl aufb", s="staufb", beep=self.bl(BeepLevel.NO), duration=0)
            nl = Dgt.DISPLAY_TEXT(l="zet stukken", m="zet stkn", s="zet st", beep=self.bl(BeepLevel.NO), duration=0)
        if text_id == 'Y00_errorjack':
            en = Dgt.DISPLAY_TEXT(l="error jack", m="err jack", s="jack", beep=self.bl(BeepLevel.YES), duration=0)
            de = Dgt.DISPLAY_TEXT(l="err Kabel", m="errKabel", s="jack", beep=self.bl(BeepLevel.YES), duration=0)
            nl = Dgt.DISPLAY_TEXT(l="error jack", m="err jack", s="jack", beep=self.bl(BeepLevel.YES), duration=0)
        if text_id == 'B00_beep':
            en = Dgt.DISPLAY_TEXT(l=None, m='beep ' + msg, s='bp ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='TonStufe ', m='TonSt ' + msg, s='Ton ' + msg, beep=self.bl(BeepLevel.BUTTON),
                                  duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='piep ' + msg, s='piep' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_level':
            en = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='lvl ' + msg, beep=self.bl(BeepLevel.BUTTON),
                                  duration=0)
            nl = en
        if text_id == 'B10_level':
            en = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='lvl ' + msg, beep=self.bl(BeepLevel.BUTTON),
                                  duration=1)
            nl = en
        if text_id == 'M10_level':
            en = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg, beep=self.bl(BeepLevel.MAP), duration=1)
            de = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='lvl ' + msg, beep=self.bl(BeepLevel.MAP),
                                  duration=1)
            nl = en
        if text_id == 'B10_mate':
            en = Dgt.DISPLAY_TEXT(l=None, m='mate ' + msg, s='m ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Matt ' + msg, s='m ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='mat ' + msg, s='m ' + msg, beep=self.bl(BeepLevel.BUTTON), duration=1)
        if text_id == 'B10_score':
            text_s = 'no scr' if msg is None else str(msg).rjust(6)
            text_m = 'no score' if msg is None else str(msg).rjust(8)
            en = Dgt.DISPLAY_TEXT(l=None, m=text_m, s=text_s, beep=self.bl(BeepLevel.BUTTON), duration=1)
            de = en
            nl = en
        if text_id == 'B00_menu_top_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='top men', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='top men', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='top men', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_mode_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='mode ', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Modus', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='mode', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_position_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='position', s='posit', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='positie', m='positie', s='positi', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_time_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='time ', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Zeit', s='zeit', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='tijd', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_book_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='book', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Buch', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='boek', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_engine_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='engine', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='engine', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_menu_system_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='system', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='System', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='system', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_normal_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Normal', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='spel', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_analysis_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='analysis', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Analyse', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l='analyseren', m='analys', s='analys', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_kibitz_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='kibitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_observe_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='observe', s='observ', beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Observe', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='bekijk', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_mode_remote_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='remote', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_timemode_fixed_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='fixed', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Fest', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='fixed', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_timemode_blitz_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='blitz', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_timemode_fischer_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='fischer', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='fischer', s='fisch', beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_version_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='version', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Version', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='version', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_ipadr_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_settings_sound_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='sound', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            de = Dgt.DISPLAY_TEXT(l=None, m='Sound', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
            nl = Dgt.DISPLAY_TEXT(l=None, m='sound', s=None, beep=self.bl(BeepLevel.BUTTON), duration=0)
        if text_id == 'B00_gameresult_mate_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='mate', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Matt', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='mat', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_stalemate_menu':
            en = Dgt.DISPLAY_TEXT(l='stalemate', m='stalemat', s='stale', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Patt', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='patstelling', m='patstlng', s='pat', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_time_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='time', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Zeit', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='tijd', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_material_menu':
            en = Dgt.DISPLAY_TEXT(l='material', m='material', s='materi', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Material', m='Material', s='materi', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='materiaal', m='material', s='materi', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_moves_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='75 move', s='75 mov', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='75 Zuege', s='75 mov', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='zet 75', m='75zetten', s='75 zetten', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_repetition_menu':
            en = Dgt.DISPLAY_TEXT(l='repetition', m='rep pos', s='reppos', beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Wiederholg', m='Wiederho', s='reppos', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='zelfde stel', m='dezelfde', s='zelfde', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_abort_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='abort', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l=None, m='Abbruch', s='abort', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='afbreken', m='afbreken', s='afbrek', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_white_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='w wins', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='W gewinnt', m='Wgewinnt', s='w wins', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='wit wint', m='wit wint', s='w wint', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_black_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='b wins', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='S gewinnt', m='Sgewinnt', s='b wins', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l='zwart wint', m='z wint', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B00_gameresult_draw_menu':
            en = Dgt.DISPLAY_TEXT(l=None, m='draw', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='unentschied', m='unendsch', s='draw', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='remise', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B10_playmode_white_user':
            en = Dgt.DISPLAY_TEXT(l=None, m='white', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Spieler W', m='Spielr W', s='splr w', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='speler w', s='splr w', beep=self.bl(BeepLevel.CONFIG), duration=1)
        if text_id == 'B10_playmode_black_user':
            en = Dgt.DISPLAY_TEXT(l=None, m='black', s=None, beep=self.bl(BeepLevel.CONFIG), duration=1)
            de = Dgt.DISPLAY_TEXT(l='Spieler S', m='Spielr S', s='splr s', beep=self.bl(BeepLevel.CONFIG), duration=1)
            nl = Dgt.DISPLAY_TEXT(l=None, m='speler z', s='splr z', beep=self.bl(BeepLevel.CONFIG), duration=1)
        # en = de  # Test german!
        if en is None:
            en = Dgt.DISPLAY_TEXT(l=None, m=text_id, s=None, beep=self.bl(BeepLevel.YES), duration=0)
            logging.warning('unknown text_id {}'.format(text_id))
        if self.language == 'de':
            return de
        if self.language == 'nl':
            return nl
        return en
