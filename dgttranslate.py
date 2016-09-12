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

    def text(self, str_code, msg=''):
        entxt = detxt = nltxt = frtxt = estxt = None  # error case

        (code, text_id) = str_code.split('_', 1)
        if code[1] == 'B':
            beep = self.bl(BeepLevel.BUTTON)
        elif code[1] == 'N':
            beep = self.bl(BeepLevel.NO)
        elif code[1] == 'Y':
            beep = self.bl(BeepLevel.YES)
        elif code[1] == 'K':
            beep = self.bl(BeepLevel.OKAY)
        elif code[1] == 'C':
            beep = self.bl(BeepLevel.CONFIG)
        elif code[1] == 'M':
            beep = self.bl(BeepLevel.MAP)
        else:
            beep = False
        maxtime = int(code[1:]) / 10
        wait = False

        if text_id == 'default':
            entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6])
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'goodbye':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Good bye', s='bye')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Tschuess', s='tschau')
            nltxt = Dgt.DISPLAY_TEXT(l='tot ziens', m='totziens', s='dag')
            frtxt = Dgt.DISPLAY_TEXT(l='au revoir', m='a plus', s='bye')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='adios', s=None)
        if text_id == 'pleasewait':
            entxt = Dgt.DISPLAY_TEXT(l='please wait', m='pls wait', s='wait')
            detxt = Dgt.DISPLAY_TEXT(l='bitteWarten', m='warten', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l='wacht even', m='wachten', s='wacht')
            frtxt = Dgt.DISPLAY_TEXT(l='patientez', m='patience', s='patien')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='espere', s=None)
        if text_id == 'nomove':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='no move', s='nomove')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Kein Zug', s='kn zug')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Geen zet', s='gn zet')
            frtxt = Dgt.DISPLAY_TEXT(l='pas de mouv', m='pas mvt', s='pasmvt')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='sin mov', s='no mov')
        if text_id == 'wb':
            entxt = Dgt.DISPLAY_TEXT(l=' W       B ', m=' W     B', s='wh  bl')
            detxt = Dgt.DISPLAY_TEXT(l=' W       S ', m=' W     S', s='we  sc')
            nltxt = Dgt.DISPLAY_TEXT(l=' W       Z ', m=' W     Z', s='wi  zw')
            frtxt = Dgt.DISPLAY_TEXT(l=' B       N ', m=' B     N', s='bl  no')
            estxt = Dgt.DISPLAY_TEXT(l=' B       N ', m=' B     N', s='bl  ne')
        if text_id == 'bw':
            entxt = Dgt.DISPLAY_TEXT(l=' B       W ', m=' B     W', s='bl  wh')
            detxt = Dgt.DISPLAY_TEXT(l=' S       W ', m=' S     W', s='sc  we')
            nltxt = Dgt.DISPLAY_TEXT(l=' Z       W ', m=' Z     W', s='zw  wi')
            frtxt = Dgt.DISPLAY_TEXT(l=' N       B ', m=' N     B', s='no  bl')
            estxt = Dgt.DISPLAY_TEXT(l=' N       B ', m=' N     B', s='ne  bl')
        if text_id == '960no':
            entxt = Dgt.DISPLAY_TEXT(l='uci960 no', m='960 no', s='960 no')
            detxt = Dgt.DISPLAY_TEXT(l='uci960 nein', m='960 nein', s='960 nn')
            nltxt = Dgt.DISPLAY_TEXT(l='uci960 nee', m='960 nee', s='960nee')
            frtxt = Dgt.DISPLAY_TEXT(l='uci960 non', m='960 non', s='960non')
            estxt = Dgt.DISPLAY_TEXT(l='uci960 no', m='960 no', s='960 no')
        if text_id == '960yes':
            entxt = Dgt.DISPLAY_TEXT(l='uci960 yes', m='960 yes', s='960yes')
            detxt = Dgt.DISPLAY_TEXT(l='uci960 ja', m='960 ja', s='960 ja')
            nltxt = Dgt.DISPLAY_TEXT(l='uci960 ja', m='960 ja', s='960 ja')
            frtxt = Dgt.DISPLAY_TEXT(l='uci960 oui', m='960 oui', s='960oui')
            estxt = Dgt.DISPLAY_TEXT(l='uci960 si', m='960 si', s=None)
        if text_id == 'picochess':
            entxt = Dgt.DISPLAY_TEXT(l='picoChs ' + version, m='pico ' + version, s='pic ' + version)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'nofunction':
            entxt = Dgt.DISPLAY_TEXT(l='no function', m='no funct', s='nofunc')
            detxt = Dgt.DISPLAY_TEXT(l='Keine Funkt', m='KeineFkt', s='kn fkt')
            nltxt = Dgt.DISPLAY_TEXT(l='Geen functie', m='Geen fnc', s='gn fnc')
            frtxt = Dgt.DISPLAY_TEXT(l='no fonction', m='no fonct', s='nofonc')
            estxt = Dgt.DISPLAY_TEXT(l='sin funcion', m='sin func', s='nofunc')
        if text_id == 'erroreng':
            entxt = Dgt.DISPLAY_TEXT(l='err engine', m='err engn', s='engerr')
            detxt = Dgt.DISPLAY_TEXT(l='err engine', m='err engn', s='engerr')
            nltxt = Dgt.DISPLAY_TEXT(l='fout engine', m='fout eng', s='e fout')
            frtxt = Dgt.DISPLAY_TEXT(l='err moteur', m='err mot', s='errmot')
            estxt = Dgt.DISPLAY_TEXT(l='error motor', m='err mot', s='errmot')
        if text_id == 'okengine':
            entxt = Dgt.DISPLAY_TEXT(l='ok engine', m='okengine', s='ok eng')
            detxt = Dgt.DISPLAY_TEXT(l='ok engine', m='okengine', s='ok eng')
            nltxt = Dgt.DISPLAY_TEXT(l='ok engine', m='okengine', s='ok eng')
            frtxt = Dgt.DISPLAY_TEXT(l='ok moteur', m='ok mot', s=None)
            estxt = Dgt.DISPLAY_TEXT(l='ok motor', m='ok motor', s='ok mot')
        if text_id == 'okmode':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok mode', s='okmode')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok Modus', s='okmode')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok modus', s='okmode')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='ok mode', s='okmode')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ok modo', s='okmodo')
        if text_id == 'okbook':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok book', s='okbook')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok Buch', s='okbuch')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok boek', s='okboek')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='ok livre', s='ok liv')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ok libro', s='oklibr')
        if text_id == 'noipadr':
            entxt = Dgt.DISPLAY_TEXT(l='no IP addr', m='no IPadr', s='no ip')
            detxt = Dgt.DISPLAY_TEXT(l='Keine IPadr', m='Keine IP', s='kn ip')
            nltxt = Dgt.DISPLAY_TEXT(l='Geen IPadr', m='Geen IP', s='gn ip')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='pas d IP', s='pd ip')
            estxt = Dgt.DISPLAY_TEXT(l='no IP dir', m='no IP', s=None)
        if text_id == 'errormenu':
            entxt = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='errmen')
            detxt = Dgt.DISPLAY_TEXT(l='error Menu', m='err Menu', s='errmen')
            nltxt = Dgt.DISPLAY_TEXT(l='fout menu', m='foutmenu', s='fout m')
            frtxt = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='pd men')
            estxt = Dgt.DISPLAY_TEXT(l='error menu', m='err menu', s='errmen')
        if text_id == 'sidewhite':
            entxt = Dgt.DISPLAY_TEXT(l='side move W', m='side W', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='W am Zug', s='w zug')
            nltxt = Dgt.DISPLAY_TEXT(l='wit aan zet', m='wit zet', s='w zet')
            frtxt = Dgt.DISPLAY_TEXT(l='aux blancs', m='mvt bl', s=None)
            estxt = Dgt.DISPLAY_TEXT(l='lado blanco', m='lado W', s=None)
        if text_id == 'sideblack':
            entxt = Dgt.DISPLAY_TEXT(l='side move B', m='side B', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='S am Zug', s='s zug')
            nltxt = Dgt.DISPLAY_TEXT(l='zw aan zet', m='zw zet', s='z zet')
            frtxt = Dgt.DISPLAY_TEXT(l='aux noirs', m='mvt n', s=None)
            estxt = Dgt.DISPLAY_TEXT(l='lado negro', m='lado B', s=None)
        if text_id == 'scanboard':
            entxt = Dgt.DISPLAY_TEXT(l='scan board', m='scan', s=None)
            detxt = Dgt.DISPLAY_TEXT(l='lese Stellg', m='lese Stl', s='lese s')
            nltxt = Dgt.DISPLAY_TEXT(l='scan bord', m='scan', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l='scan echiq', m='scan', s=None)
            estxt = Dgt.DISPLAY_TEXT(l='escan tabl', m='escan', s=None)
        if text_id == 'illegalpos':
            entxt = Dgt.DISPLAY_TEXT(l='invalid pos', m='invalid', s='badpos')
            detxt = Dgt.DISPLAY_TEXT(l='illegalePos', m='illegal', s='errpos')
            nltxt = Dgt.DISPLAY_TEXT(l='ongeldig', m='ongeldig', s='ongeld')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='illegale', s='pos il')
            estxt = Dgt.DISPLAY_TEXT(l='illegal pos', m='ileg pos', s='ilegpo')
        if text_id == 'error960':
            entxt = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s='err960')
            detxt = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s='err960')
            nltxt = Dgt.DISPLAY_TEXT(l='fout uci960', m='fout 960', s='err960')
            frtxt = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s='err960')
            estxt = Dgt.DISPLAY_TEXT(l='err uci960', m='err 960', s='err960')
        if text_id == 'oktime':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok time', s='ok tim')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok Zeit', s='okzeit')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok tyd', s='ok tyd')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='ok temps', s='ok tps')
            estxt = Dgt.DISPLAY_TEXT(l='ok tiempo', m='okTiempo', s='ok tpo')
        if text_id == 'okbeep':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok beep', s='okbeep')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok TonSt', s='ok ton')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok piep', s='okpiep')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='ok sons', s='oksons')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ok beep', s='okbeep')
        if text_id == 'okpico':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok pico', s='okpico')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'okuser':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l='ok player', m='okplayer', s='okplay')
            detxt = Dgt.DISPLAY_TEXT(l='ok Spieler', m='ok Splr', s='oksplr')
            nltxt = Dgt.DISPLAY_TEXT(l='ok Speler', m='okSpeler', s='oksplr')
            frtxt = Dgt.DISPLAY_TEXT(l='ok joueur', m='okjoueur', s='ok jr')
            estxt = Dgt.DISPLAY_TEXT(l='ok usuario', m='okusuari', s='okuser')
        if text_id == 'okmove':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='ok move', s='okmove')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='ok Zug', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok zet', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='ok mouv', s='ok mvt')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ok jugada', s='ok jug')
        if text_id == 'altmove':
            entxt = Dgt.DISPLAY_TEXT(l='altn move', m='alt move', s='altmov')
            detxt = Dgt.DISPLAY_TEXT(l='altnatv Zug', m='alt Zug', s='altzug')
            nltxt = Dgt.DISPLAY_TEXT(l='andere zet', m='alt zet', s='altzet')
            frtxt = Dgt.DISPLAY_TEXT(l='autre mouv', m='alt move', s='altmov')
            estxt = Dgt.DISPLAY_TEXT(l='altn jugada', m='altjugad', s='altjug')
        if text_id == 'newgame':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='new Game', s='newgam')
            detxt = Dgt.DISPLAY_TEXT(l='neues Spiel', m='neuesSpl', s='neuspl')
            nltxt = Dgt.DISPLAY_TEXT(l='nieuw party', m='nw party', s='nwpart')
            frtxt = Dgt.DISPLAY_TEXT(l='nvl partie', m='nvl part', s='newgam')
            estxt = Dgt.DISPLAY_TEXT(l='nuev partid', m='nuevpart', s='n part')
        if text_id == 'ucigame':
            msg = msg.rjust(3)
            entxt = Dgt.DISPLAY_TEXT(l='new Game' + msg, m='Game ' + msg, s='gam' + msg)
            detxt = Dgt.DISPLAY_TEXT(l='neuSpiel' + msg, m='Spiel' + msg, s='spl' + msg)
            nltxt = Dgt.DISPLAY_TEXT(l='nw party' + msg, m='party' + msg, s='par' + msg)
            frtxt = Dgt.DISPLAY_TEXT(l='nvl part' + msg, m='part ' + msg, s='gam' + msg)
            estxt = Dgt.DISPLAY_TEXT(l='partid  ' + msg, m='part ' + msg, s='par' + msg)
        if text_id == 'takeback':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='takeback', s='takbak')
            detxt = Dgt.DISPLAY_TEXT(l='Ruecknahme', m='Rcknahme', s='rueckn')
            nltxt = Dgt.DISPLAY_TEXT(l='zet terug', m='zetterug', s='terug')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='retour', s=None)
            estxt = Dgt.DISPLAY_TEXT(l='retrocede', m='atras', s=None)
        if text_id == 'bookmove':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='book', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Buch', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='boek', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='livre', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='libro', s=None)
        if text_id == 'setpieces':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l='set pieces', m='set pcs', s='setpcs')
            detxt = Dgt.DISPLAY_TEXT(l='St aufbauen', m='aufbauen', s='aufbau')
            nltxt = Dgt.DISPLAY_TEXT(l='zet stukken', m='zet stkn', s='zet st')
            frtxt = Dgt.DISPLAY_TEXT(l='placer pcs', m='set pcs', s='setpcs')
            estxt = Dgt.DISPLAY_TEXT(l='hasta piez', m='hasta pz', s='hastap')
        if text_id == 'errorjack':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l='error jack', m='err jack', s='jack')
            detxt = Dgt.DISPLAY_TEXT(l='err Kabel', m='errKabel', s='errkab')
            nltxt = Dgt.DISPLAY_TEXT(l='fout Kabel', m='errKabel', s='errkab')
            frtxt = Dgt.DISPLAY_TEXT(l='jack error', m='jack err', s='jack')
            estxt = Dgt.DISPLAY_TEXT(l='jack error', m='jack err', s='jack')
        if text_id == 'level':
            if msg.startswith('Elo@'):
                msg = str(int(msg[4:])).rjust(4)
                entxt = Dgt.DISPLAY_TEXT(l=None, m='Elo ' + msg, s='el' + msg)
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
            elif msg.startswith('Level@'):
                msg = str(int(msg[6:])).rjust(2)
                entxt = Dgt.DISPLAY_TEXT(l=None, m='level ' + msg, s='lvl ' + msg)
                detxt = Dgt.DISPLAY_TEXT(l='SpielSt ' + msg, m='Stufe ' + msg, s='stf ' + msg)
                nltxt = entxt
                frtxt = Dgt.DISPLAY_TEXT(l='niveau ' + msg, m='niveau' + msg, s='niv ' + msg)
                estxt = Dgt.DISPLAY_TEXT(l=None, m='nivel ' + msg, s='nvl ' + msg)
            else:
                entxt = Dgt.DISPLAY_TEXT(l=msg, m=msg[:8], s=msg[:6])
                detxt = entxt
                nltxt = entxt
                frtxt = entxt
                estxt = entxt
        if text_id == 'mate':
            entxt = Dgt.DISPLAY_TEXT(l='mate in ' + msg, m='mate ' + msg, s='mate' + msg)
            detxt = Dgt.DISPLAY_TEXT(l='Matt in ' + msg, m='Matt ' + msg, s='matt' + msg)
            nltxt = Dgt.DISPLAY_TEXT(l='mat in ' + msg, m='mat ' + msg, s='mat ' + msg)
            frtxt = Dgt.DISPLAY_TEXT(l='mat en ' + msg, m='mat ' + msg, s=None)
            estxt = Dgt.DISPLAY_TEXT(l='mate en ' + msg, m='mate ' + msg, s='mate' + msg)
        if text_id == 'score':
            text_s = 'no scr' if msg is None else str(msg).rjust(6)
            text_m = 'no score' if msg is None else str(msg).rjust(8)
            entxt = Dgt.DISPLAY_TEXT(l=None, m=text_m, s=text_s)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'menu_top_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen')
            detxt = Dgt.DISPLAY_TEXT(l='Haupt Menu', m='Hpt Menu', s='topmen')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Top menu', s='topmen')
        if text_id == 'menu_mode_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Mode', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Modus', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Modus', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Mode', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Modo', s=None)
        if text_id == 'menu_position_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Stelling', s='stelng')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Position', s='posit')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Posicion', s='posic')
        if text_id == 'menu_time_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Time', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Zeit', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Tyd', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Temps', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Tiempo', s=None)
        if text_id == 'menu_book_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Book', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Buch', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Boek', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Livre', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Libro', s=None)
        if text_id == 'menu_engine_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Engine', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Moteur', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Motor', s=None)
        if text_id == 'menu_system_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='System', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='System', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Systeem', s='system')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Systeme', s='system')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Sistema', s='sistem')
        if text_id == 'mode_normal_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Normal', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Normal', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Normaal', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='normal', s=None)
        if text_id == 'mode_analysis_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Analysis', s='analys')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Analyse', s='analys')
            nltxt = Dgt.DISPLAY_TEXT(l='Analyseren', m='Analyse', s='analys')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Analyser', s='analys')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Analisis', s='analis')
        if text_id == 'mode_kibitz_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Evaluer', s='evalue')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Kibitz', s=None)
        if text_id == 'mode_observe_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Observe', s='observ')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Observe', s='observ')
            nltxt = Dgt.DISPLAY_TEXT(l='Observeren', m='Observr', s='observ')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Observer', s='observ')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Observa', s='observ')
        if text_id == 'mode_remote_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Remote', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Remoto', s=None)
        if text_id == 'timemode_fixed_menu':
            entxt = Dgt.DISPLAY_TEXT(l='Move time', m='Movetime', s='move t')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Zugzeit', s='zug z')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Zet tyd', s='zet')
            frtxt = Dgt.DISPLAY_TEXT(l='Mouv temps', m='Mouv tem', s='mouv')
            estxt = Dgt.DISPLAY_TEXT(l='Mov tiempo', m='mov tiem', s='mov')
        if text_id == 'timemode_blitz_menu':
            entxt = Dgt.DISPLAY_TEXT(l='Game time', m='Gametime', s='game t')
            detxt = Dgt.DISPLAY_TEXT(l='Spielzeit', m='Spielz', s='spielz')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Spel tyd', s='spel')
            frtxt = Dgt.DISPLAY_TEXT(l='Partie temp', m='Partie')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Partid', s=None)
        if text_id == 'timemode_fischer_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Fischer', s='fischr')
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt
        if text_id == 'settings_version_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Versie', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Version', s='vers')
        if text_id == 'settings_ipadr_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='IP adr', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l='IP address', m='IP adr', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Adr IP', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='IP dir', s=None)
        if text_id == 'settings_sound_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Sound', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Toene', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Geluid', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Sons', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Sonido', s=None)
        if text_id == 'settings_language_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Language', s='lang')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Sprache', s='sprach')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Taal', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Langue', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Idioma', s=None)
        if text_id == 'gameresult_mate_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='mate', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Matt', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='mat', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='mat', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='mate', s=None)
        if text_id == 'gameresult_stalemate_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l='stalemate', m='stalemat', s='stale')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Patt', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l='patstelling', m='pat', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='pat', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='ahogado', s='ahogad')
        if text_id == 'gameresult_time_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='time', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Zeit', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='tyd', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='tombe', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='tiempo', s=None)
        if text_id == 'gameresult_material_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='material', s='materi')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Material', s='materi')
            nltxt = Dgt.DISPLAY_TEXT(l='materiaal', m='material', s='materi')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='materiel', s='materl')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='material', s='mater')
        if text_id == 'gameresult_moves_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='75 moves', s='75 mov')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='75 Zuege', s='75 zug')
            nltxt = Dgt.DISPLAY_TEXT(l='75 zetten', m='75zetten', s='75 zet')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='75 mouv', s='75 mvt')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='75 mov', s=None)
        if text_id == 'gameresult_repetition_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l='repetition', m='rep pos', s='reppos')
            detxt = Dgt.DISPLAY_TEXT(l='Wiederholg', m='Wiederhg', s='wh pos')
            nltxt = Dgt.DISPLAY_TEXT(l='zetherhaling', m='herhalin', s='herhal')
            frtxt = Dgt.DISPLAY_TEXT(l='3ieme rep', m='3iem rep', s='3 rep')
            estxt = Dgt.DISPLAY_TEXT(l='repeticion', m='repite 3', s='rep 3')
        if text_id == 'gameresult_abort_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='abort', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Abbruch', s='abbrch')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='afbreken', s='afbrek')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='sortir', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='abortar', s='abort')
        if text_id == 'gameresult_white_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='W wins', s=None)
            detxt = Dgt.DISPLAY_TEXT(l='W gewinnt', m='W Gewinn', s='w gew')
            nltxt = Dgt.DISPLAY_TEXT(l='wit wint', m='wit wint', s='w wint')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='B gagne', s='b gagn')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='B ganan', s='b gana')
        if text_id == 'gameresult_black_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='B wins', s=None)
            detxt = Dgt.DISPLAY_TEXT(l='S gewinnt', m='S Gewinn', s='s gew')
            nltxt = Dgt.DISPLAY_TEXT(l='zwart wint', m='zw wint', s='z wint')
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='N gagne', s='n gagn')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='N ganan', s='n gana')
        if text_id == 'gameresult_draw_menu':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='draw', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Remis', s='remis')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='remise', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='nulle', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='tablas', s=None)
        if text_id == 'playmode_white_user':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='player W', s='white')
            detxt = Dgt.DISPLAY_TEXT(l='Spieler W', m='SpielerW', s='splr w')
            nltxt = Dgt.DISPLAY_TEXT(l='speler wit', m='speler W', s='splr w')
            frtxt = Dgt.DISPLAY_TEXT(l='joueur B', m='joueur B', s='blancs')
            estxt = Dgt.DISPLAY_TEXT(l='jugador B', m='jugad B', s='juga b')
        if text_id == 'playmode_black_user':
            wait = True
            entxt = Dgt.DISPLAY_TEXT(l=None, m='player B', s='black')
            detxt = Dgt.DISPLAY_TEXT(l='Spieler S', m='SpielerS', s='splr s')
            nltxt = Dgt.DISPLAY_TEXT(l='speler zw', m='speler z', s='splr z')
            frtxt = Dgt.DISPLAY_TEXT(l='joueur n', m='joueur n', s='noirs')
            estxt = Dgt.DISPLAY_TEXT(l='jugador n', m='jugad n', s='juga n')
        if text_id == 'language_en_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='English', s='englsh')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Englisch', s='en')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Engels', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Anglais', s='anglai')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Ingles', s=None)
        if text_id == 'language_de_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='German', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Deutsch', s='de')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Duits', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Allemand', s='allema')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Aleman', s=None)
        if text_id == 'language_nl_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Dutch', s=None)
            detxt = Dgt.DISPLAY_TEXT(l='Niederldsch', m='Niederl', s='nl')
            nltxt = Dgt.DISPLAY_TEXT(l='Nederlands', m='Nederl', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l='Neerlandais', m='Neerlnd', s='neer')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Holandes', s='holand')
        if text_id == 'language_fr_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='French', s=None)
            detxt = Dgt.DISPLAY_TEXT(l='Franzosisch', m='Franzsch', s='fr')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Frans', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Francais', s='france')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Frances', s='franc')
        if text_id == 'language_es_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Spanish', s='spanis')
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Spanisch', s='es')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Spaans', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Espagnol', s='espag')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Espanol', s='esp')
        if text_id == 'beep_off_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Never', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Nie', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Nooit', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Jamais', s=None)
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Nunca', s=None)
        if text_id == 'beep_some_menu':
            entxt = Dgt.DISPLAY_TEXT(l='Sometimes', m='Some', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Manchmal', s='manch')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Soms', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Parfois', s='parfoi')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='A veces', s='aveces')
        if text_id == 'beep_on_menu':
            entxt = Dgt.DISPLAY_TEXT(l=None, m='Always', s=None)
            detxt = Dgt.DISPLAY_TEXT(l=None, m='Immer', s=None)
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='Altyd', s=None)
            frtxt = Dgt.DISPLAY_TEXT(l=None, m='Toujours', s='toujou')
            estxt = Dgt.DISPLAY_TEXT(l=None, m='Siempre', s='siempr')
        if text_id == 'oklang':
            entxt = Dgt.DISPLAY_TEXT(l='ok language', m='ok lang', s='oklang')
            detxt = Dgt.DISPLAY_TEXT(l='ok Sprache', m='okSprach', s='ok spr')
            nltxt = Dgt.DISPLAY_TEXT(l=None, m='ok taal', s='oktaal')
            frtxt = Dgt.DISPLAY_TEXT(l='ok langue', m='okLangue', s='oklang')
            estxt = Dgt.DISPLAY_TEXT(l='ok idioma', m='okIdioma', s='oklang')
        if text_id == 'tc_fixed':
            entxt = Dgt.DISPLAY_TEXT(l='Move time' + msg, m='Move t' + msg, s='mov ' + msg)
            detxt = Dgt.DISPLAY_TEXT(l='Zugzeit  ' + msg, m='Zug z ' + msg, s='zug ' + msg)
            nltxt = Dgt.DISPLAY_TEXT(l='Zet tyd  ' + msg, m='Zet t ' + msg, s='zet ' + msg)
            frtxt = Dgt.DISPLAY_TEXT(l='Mouv     ' + msg, m='Mouv  ' + msg, s='mouv' + msg)
            estxt = Dgt.DISPLAY_TEXT(l='Mov      ' + msg, m='Mov   ' + msg, s='mov ' + msg)
        if text_id == 'tc_blitz':
            entxt = Dgt.DISPLAY_TEXT(l='Game time' + msg, m='Game t' + msg, s='game' + msg)
            detxt = Dgt.DISPLAY_TEXT(l='Spielzeit' + msg, m='Spielz' + msg, s='spl ' + msg)
            nltxt = Dgt.DISPLAY_TEXT(l='Spel tyd ' + msg, m='Spel t' + msg, s='spel' + msg)
            frtxt = Dgt.DISPLAY_TEXT(l='Partie   ' + msg, m='Partie' + msg, s='part' + msg)
            estxt = Dgt.DISPLAY_TEXT(l='Partid   ' + msg, m='Partid' + msg, s='part' + msg)
        if text_id == 'tc_fisch':
            entxt = Dgt.DISPLAY_TEXT(l='Fischr' + msg, m='Fsh' + msg, s='f' + msg)
            detxt = entxt
            nltxt = entxt
            frtxt = entxt
            estxt = entxt

        for txt in [entxt, detxt, nltxt, frtxt, estxt]:
            if txt:
                txt.wait = wait
                txt.beep = beep
                txt.maxtime = maxtime

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
