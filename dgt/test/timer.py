#!/usr/bin/env python3
#
from threading import Timer
from time import sleep


def stopped_maxtimer():
    print('stopped')


print('start')
maxtimer = Timer(5, stopped_maxtimer)
maxtimer.start()
print(maxtimer.is_alive())
print('sleep2')
print()
sleep(2)
print(maxtimer.is_alive())
maxtimer.cancel()
print('X')
print(maxtimer.is_alive())
maxtimer.join()
print('Y')
print(maxtimer.is_alive())
print('sleep5')
print()
sleep(5)
print(maxtimer.is_alive())
print('end')
