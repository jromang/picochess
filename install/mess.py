#!/usr/bin/env python3
import sys
import subprocess
from time import sleep
import pifacecad
from subprocess import call

if __name__ == "__main__":
    cad = pifacecad.PiFaceCAD()
    cad.lcd.blink_off()
    cad.lcd.cursor_off()

    if "clear" in sys.argv:
        cad.lcd.clear()
        cad.lcd.display_off()
        cad.lcd.backlight_off()
    else:
        cad.lcd.backlight_on()
        cad.lcd.write(str(sys.argv[1]))
        a = call(["espeak","-s140 -ven+18 -z",str(sys.argv[1])])
        a.communicate()
