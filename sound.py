#!/usr/bin/env python3

from talker.picotalker import *

# from utilities import *
# PicoTalkerDisplay('it:luigi', 'it:luigi').start()
# DisplayMsg.show(Message.START_NEW_GAME())
# DisplayMsg.show(Message.LEVEL())

method_list = [func for func in dir(PicoTalker) if callable(getattr(PicoTalker, func)) and func.startswith("say_")]

pt = PicoTalker('en:al')
for method in method_list:
    if method in ('say_move', 'say_out_of_time', 'say_winner'):
        continue
    print(method)
    getattr(pt, method)()
