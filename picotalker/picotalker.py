#!/usr/bin/env python3

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

import logging

# for this (picoctalker) to work you need to run these commands (if you haven't done before)
# pip3 install pysoundfile
# pip3 install sounddevice
# pip3 install numpy

try:
    import sounddevice as sd
    import soundfile as sf

    data, fs = sf.read('voices/en/al/knight.ogg', dtype='float32')
    sd.play(data, fs, blocking=True)
    data, fs = sf.read('voices/en/al/f.ogg', dtype='float32')
    sd.play(data, fs, blocking=True)
    data, fs = sf.read('voices/en/al/3.ogg', dtype='float32')
    sd.play(data, fs, blocking=True)
    data, fs = sf.read('voices/en/al/check.ogg', dtype='float32')
    sd.play(data, fs, blocking=True)
    status = sd.get_status()
    if status:
        logging.warning(str(status))
except KeyboardInterrupt:
    print('\nInterrupted by user')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))
