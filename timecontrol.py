from utilities import *


class TimeControl:
    def __init__(self, mode=ClockMode.FIXED_TIME, seconds_per_move=3, minutes_per_game=0, fischer_increment=0):
        super().__init__()
        self.mode = mode
        self.seconds_per_move = seconds_per_move
        self.minutes_per_game = minutes_per_game
        self.fischer_increment =  fischer_increment