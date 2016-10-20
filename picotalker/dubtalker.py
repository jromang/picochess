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

# for this (picotalker) to work you need to run these commands (if you haven't done before)
# pip3 install pydub
# pip3 install pyaudio
# apt-get install ffmpeg

from pydub import AudioSegment
from pydub.playback import *
import pyaudio

import os
import sys

nf3check = [
    AudioSegment.from_ogg('voices/en/al/knight.ogg'),
    AudioSegment.from_ogg('voices/en/al/f.ogg'),
    AudioSegment.from_ogg('voices/en/al/3.ogg'),
    AudioSegment.from_ogg('voices/en/al/check.ogg')
]
sound = AudioSegment.empty()
for part in nf3check:
    sound += part

# Hide errors
devnull = os.open(os.devnull, os.O_WRONLY)
old_stderr = os.dup(2)
sys.stderr.flush()
os.dup2(devnull, 2)
os.close(devnull)

p = pyaudio.PyAudio()
# Enable errors
os.dup2(old_stderr, 2)
os.close(old_stderr)

stream = p.open(format=p.get_format_from_width(sound.sample_width), channels=sound.channels, rate=sound.frame_rate,
                output=True)

# break audio into half-second chunks (to allows keyboard interrupts)
for chunk in make_chunks(sound, 500):
    stream.write(chunk._data)

stream.stop_stream()
stream.close()
p.terminate()
