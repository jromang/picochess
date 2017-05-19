# Copyright (C) 2013-2017 Jean-Francois Romang (jromang@posteo.de)
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

try:
    import enum
except ImportError:
    import enum34 as enum


class AutoNumber(enum.Enum):
    def __new__(cls):  # Autonumber
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


@enum.unique
class Top(enum.Enum):
    MODE = 'B00_top_mode_menu'  # Mode Menu
    POSITION = 'B00_top_position_menu'  # Setup position menu
    TIME = 'B00_top_time_menu'  # Time controls menu
    BOOK = 'B00_top_book_menu'  # Book menu
    ENGINE = 'B00_top_engine_menu'  # Engine menu
    SYSTEM = 'B00_top_system_menu'  # Settings menu


class TopLoop(object):
    def __init__(self):
        super(TopLoop, self).__init__()

    @staticmethod
    def next(m: Top):
        if m == Top.MODE:
            return Top.POSITION
        elif m == Top.POSITION:
            return Top.TIME
        elif m == Top.TIME:
            return Top.BOOK
        elif m == Top.BOOK:
            return Top.ENGINE
        elif m == Top.ENGINE:
            return Top.SYSTEM
        elif m == Top.SYSTEM:
            return Top.MODE
        return 'errMenuNext'

    @staticmethod
    def prev(m: Top):
        if m == Top.MODE:
            return Top.SYSTEM
        elif m == Top.POSITION:
            return Top.MODE
        elif m == Top.TIME:
            return Top.POSITION
        elif m == Top.BOOK:
            return Top.TIME
        elif m == Top.ENGINE:
            return Top.BOOK
        elif m == Top.SYSTEM:
            return Top.ENGINE
        return 'errMenuPrev'


@enum.unique
class Mode(enum.Enum):
    NORMAL = 'B00_mode_normal_menu'
    ANALYSIS = 'B00_mode_analysis_menu'
    KIBITZ = 'B00_mode_kibitz_menu'
    OBSERVE = 'B00_mode_observe_menu'
    REMOTE = 'B00_mode_remote_menu'
    PONDER = 'B00_mode_ponder_menu'


class ModeLoop(object):
    def __init__(self):
        super(ModeLoop, self).__init__()

    @staticmethod
    def next(m: Mode):
        if m == Mode.NORMAL:
            return Mode.ANALYSIS
        elif m == Mode.ANALYSIS:
            return Mode.KIBITZ
        elif m == Mode.KIBITZ:
            return Mode.OBSERVE
        elif m == Mode.OBSERVE:
            return Mode.REMOTE
        elif m == Mode.REMOTE:
            return Mode.PONDER
        elif m == Mode.PONDER:
            return Mode.NORMAL
        return 'errModeNext'

    @staticmethod
    def prev(m: Mode):
        if m == Mode.NORMAL:
            return Mode.PONDER
        elif m == Mode.ANALYSIS:
            return Mode.NORMAL
        elif m == Mode.KIBITZ:
            return Mode.ANALYSIS
        elif m == Mode.OBSERVE:
            return Mode.KIBITZ
        elif m == Mode.REMOTE:
            return Mode.OBSERVE
        elif m == Mode.PONDER:
            return Mode.REMOTE
        return 'errModePrev'


@enum.unique
class PlayMode(enum.Enum):
    USER_WHITE = 'B10_playmode_white_user'
    USER_BLACK = 'B10_playmode_black_user'


class TimeMode(enum.Enum):
    FIXED = 'B00_timemode_fixed_menu'  # Fixed seconds per move
    BLITZ = 'B00_timemode_blitz_menu'  # Fixed time per game
    FISCHER = 'B00_timemode_fischer_menu'  # Fischer increment


class TimeModeLoop(object):
    def __init__(self):
        super(TimeModeLoop, self).__init__()

    @staticmethod
    def next(m: TimeMode):
        if m == TimeMode.FIXED:
            return TimeMode.BLITZ
        elif m == TimeMode.BLITZ:
            return TimeMode.FISCHER
        elif m == TimeMode.FISCHER:
            return TimeMode.FIXED
        return 'errTiMoNext'

    @staticmethod
    def prev(m: TimeMode):
        if m == TimeMode.FIXED:
            return TimeMode.FISCHER
        elif m == TimeMode.BLITZ:
            return TimeMode.FIXED
        elif m == TimeMode.FISCHER:
            return TimeMode.BLITZ
        return 'errTiMoPrev'


class System(enum.Enum):
    VERSION = 'B00_system_version_menu'
    IPADR = 'B00_system_ipadr_menu'
    SOUND = 'B00_system_sound_menu'
    LANGUAGE = 'B00_system_language_menu'
    LOGFILE = 'B00_system_logfile_menu'
    VOICE = 'B00_system_voice_menu'
    DISPLAY = 'B00_system_display_menu'


class SystemLoop(object):
    def __init__(self):
        super(SystemLoop, self).__init__()

    @staticmethod
    def next(m: System):
        if m == System.VERSION:
            return System.IPADR
        elif m == System.IPADR:
            return System.SOUND
        elif m == System.SOUND:
            return System.LANGUAGE
        elif m == System.LANGUAGE:
            return System.LOGFILE
        elif m == System.LOGFILE:
            return System.VOICE
        elif m == System.VOICE:
            return System.DISPLAY
        elif m == System.DISPLAY:
            return System.VERSION
        return 'errSystNext'

    @staticmethod
    def prev(m: System):
        if m == System.VERSION:
            return System.DISPLAY
        if m == System.DISPLAY:
            return System.VOICE
        if m == System.VOICE:
            return System.LOGFILE
        if m == System.LOGFILE:
            return System.LANGUAGE
        if m == System.LANGUAGE:
            return System.SOUND
        elif m == System.SOUND:
            return System.IPADR
        elif m == System.IPADR:
            return System.VERSION
        return 'errSystPrev'


class Language(enum.Enum):
    EN = 'B00_language_en_menu'
    DE = 'B00_language_de_menu'
    NL = 'B00_language_nl_menu'
    FR = 'B00_language_fr_menu'
    ES = 'B00_language_es_menu'
    IT = 'B00_language_it_menu'


class LanguageLoop(object):
    def __init__(self):
        super(LanguageLoop, self).__init__()

    @staticmethod
    def next(m: Language):
        if m == Language.EN:
            return Language.DE
        elif m == Language.DE:
            return Language.NL
        elif m == Language.NL:
            return Language.FR
        elif m == Language.FR:
            return Language.ES
        elif m == Language.ES:
            return Language.IT
        elif m == Language.IT:
            return Language.EN
        return 'errLangNext'

    @staticmethod
    def prev(m: Language):
        if m == Language.EN:
            return Language.IT
        if m == Language.IT:
            return Language.ES
        if m == Language.ES:
            return Language.FR
        if m == Language.FR:
            return Language.NL
        elif m == Language.NL:
            return Language.DE
        elif m == Language.DE:
            return Language.EN
        return 'errLangPrev'


class Beep(enum.Enum):
    OFF = 'B00_beep_off_menu'
    SOME = 'B00_beep_some_menu'
    ON = 'B00_beep_on_menu'


class BeepLoop(object):
    def __init__(self):
        super(BeepLoop, self).__init__()

    @staticmethod
    def next(m: Beep):
        if m == Beep.OFF:
            return Beep.SOME
        elif m == Beep.SOME:
            return Beep.ON
        elif m == Beep.ON:
            return Beep.OFF
        return 'errBeepNext'

    @staticmethod
    def prev(m: Beep):
        if m == Beep.OFF:
            return Beep.ON
        if m == Beep.ON:
            return Beep.SOME
        if m == Beep.SOME:
            return Beep.OFF
        return 'errBeepPrev'


class Voice(enum.Enum):
    SPEED = 'B00_voice_speed_menu'
    USER = 'B00_voice_user_menu'
    COMP = 'B00_voice_comp_menu'


class VoiceLoop(object):
    def __init__(self):
        super(VoiceLoop, self).__init__()

    @staticmethod
    def next(m: Voice):
        if m == Voice.SPEED:
            return Voice.COMP
        elif m == Voice.COMP:
            return Voice.USER
        elif m == Voice.USER:
            return Voice.SPEED
        return 'errVoicNext'

    @staticmethod
    def prev(m: Voice):
        if m == Voice.SPEED:
            return Voice.USER
        elif m == Voice.USER:
            return Voice.COMP
        elif m == Voice.COMP:
            return Voice.SPEED
        return 'errVoicPrev'


@enum.unique
class Display(enum.Enum):
    PONDER = 'B00_display_ponder_menu'
    CONFIRM = 'B00_display_confirm_menu'


class DisplayLoop(object):
    def __init__(self):
        super(DisplayLoop, self).__init__()

    @staticmethod
    def next(m: Display):
        if m == Display.PONDER:
            return Display.CONFIRM
        elif m == Display.CONFIRM:
            return Display.PONDER
        return 'errDispNext'

    @staticmethod
    def prev(m: Display):
        if m == Display.PONDER:
            return Display.CONFIRM
        elif m == Display.CONFIRM:
            return Display.PONDER
        return 'errDispPrev'


@enum.unique
class GameResult(enum.Enum):

    """Game end result."""

    MATE = 'B00_gameresult_mate'
    STALEMATE = 'B00_gameresult_stalemate'
    OUT_OF_TIME = 'B00_gameresult_time'
    INSUFFICIENT_MATERIAL = 'B00_gameresult_material'
    SEVENTYFIVE_MOVES = 'B00_gameresult_moves'
    FIVEFOLD_REPETITION = 'B00_gameresult_repetition'
    ABORT = 'B00_gameresult_abort'
    WIN_WHITE = 'B00_gameresult_white'
    WIN_BLACK = 'B00_gameresult_black'
    DRAW = 'B00_gameresult_draw'


class EngineStatus(AutoNumber):

    """Status of the engine."""

    THINK = ()
    PONDER = ()
    WAIT = ()


@enum.unique
class BeepLevel(enum.Enum):

    """Define the beep level for each beep event."""

    YES = 0x0f  # Always ON
    NO = 0x00  # Always OFF
    CONFIG = 0x01  # Takeback, GameEnd, NewGame, ComputerMove and SetPieces
    BUTTON = 0x02  # All Events coming from button press
    MAP = 0x04  # All Events coming from Queen placing at start pos (line3-6)
    OKAY = 0x08  # All Events from "ok" (confirm) messages


@enum.unique
class ClockSide(enum.Enum):

    """Side to display the message."""

    LEFT = 0x01
    RIGHT = 0x02
    NONE = 0x04


@enum.unique
class ClockIcons(enum.Enum):

    """DGT clock icons."""

    NONE = 0x00
    COLON = 0x08
    DOT = 0x10


@enum.unique
class DgtCmd(enum.Enum):

    """COMMAND CODES FROM PC TO BOARD."""

    # Commands not resulting in returning messages:
    DGT_SEND_RESET = 0x40  # Puts the board in IDLE mode, cancelling any UPDATE mode
    DGT_STARTBOOTLOADER = 0x4e  # Makes a long jump to the FC00 boot loader code. Start FLIP now
    # Commands resulting in returning message(s):
    DGT_SEND_CLK = 0x41  # Results in a DGT_MSG_BWTIME message
    DGT_SEND_BRD = 0x42  # Results in a DGT_MSG_BOARD_DUMP message
    DGT_SEND_UPDATE = 0x43  # Results in DGT_MSG_FIELD_UPDATE messages and DGT_MSG_BWTIME messages
    # as long as the board is in UPDATE mode
    DGT_SEND_UPDATE_BRD = 0x44  # Results in DGT_MSG_FIELD_UPDATE messages as long as the board is in UPDATE_BOARD mode
    DGT_RETURN_SERIALNR = 0x45  # Results in a DGT_MSG_SERIALNR message
    DGT_RETURN_BUSADRES = 0x46  # Results in a DGT_MSG_BUSADRES message
    DGT_SEND_TRADEMARK = 0x47  # Results in a DGT_MSG_TRADEMARK message
    DGT_SEND_EE_MOVES = 0x49  # Results in a DGT_MSG_EE_MOVES message
    DGT_SEND_UPDATE_NICE = 0x4b  # Results in DGT_MSG_FIELD_UPDATE messages and DGT_MSG_BWTIME messages,
    # the latter only at time changes, as long as the board is in UPDATE_NICE mode
    DGT_SEND_BATTERY_STATUS = 0x4c  # New command for bluetooth board. Requests the battery status from the board.
    DGT_SEND_VERSION = 0x4d  # Results in a DGT_MSG_VERSION message
    DGT_SEND_BRD_50B = 0x50  # Results in a DGT_MSG_BOARD_DUMP_50 message: only the black squares
    DGT_SCAN_50B = 0x51  # Sets the board in scanning only the black squares. This is written in EEPROM
    DGT_SEND_BRD_50W = 0x52  # Results in a DGT_MSG_BOARD_DUMP_50 message: only the black squares
    DGT_SCAN_50W = 0x53  # Sets the board in scanning only the black squares. This is written in EEPROM.
    DGT_SCAN_100 = 0x54  # Sets the board in scanning all squares. This is written in EEPROM
    DGT_RETURN_LONG_SERIALNR = 0x55  # Results in a DGT_LONG_SERIALNR message
    DGT_SET_LEDS = 0x60  # Only for the Revelation II to switch a LED pattern on. This is a command that
    # has three extra bytes with data.
    # Clock commands, returns ACK message if mode is in UPDATE or UPDATE_NICE
    DGT_CLOCK_MESSAGE = 0x2b  # This message contains a command for the clock.


class DgtClk(enum.Enum):

    """DESCRIPTION OF THE COMMANDS FROM BOARD TO PC."""

    DGT_CMD_CLOCK_DISPLAY = 0x01  # This command can control the segments of six 7-segment characters,
    # two dots, two semicolons and the two '1' symbols.
    DGT_CMD_CLOCK_ICONS = 0x02  # Used to control the clock icons like flags etc.
    DGT_CMD_CLOCK_END = 0x03  # This command clears the message and brings the clock back to the
    # normal display (showing clock times).
    DGT_CMD_CLOCK_BUTTON = 0x08  # Requests the current button pressed (if any).
    DGT_CMD_CLOCK_VERSION = 0x09  # This commands requests the clock version.
    DGT_CMD_CLOCK_SETNRUN = 0x0a  # This commands controls the clock times and counting direction, when
    # the clock is in mode 23. A clock can be paused or counting down. But
    # counting up isn't supported on current DGT XL's (1.14 and lower) yet.
    DGT_CMD_CLOCK_BEEP = 0x0b  # This clock command turns the beep on, for a specified time (64ms * byte 5)
    DGT_CMD_CLOCK_ASCII = 0x0c  # This clock commands sends a ASCII message to the clock that
    # can be displayed only by the DGT3000.
    DGT_CMD_CLOCK_START_MESSAGE = 0x03
    DGT_CMD_CLOCK_END_MESSAGE = 0x00


class DgtAck(enum.Enum):

    """DESCRIPTION OF THE ACKNOWLEDGMENTS FROM BOARD TO PC."""

    DGT_ACK_CLOCK_DISPLAY = 0x01  # Display ack
    DGT_ACK_CLOCK_ICON = 0x02
    DGT_ACK_CLOCK_END = 0x03
    DGT_ACK_CLOCK_BUTTON_NONE = 0x08  # Buttons ack, but no button information is returned though
    DGT_ACK_CLOCK_VERSION = 0x09  # Version ack. ack2>>4 is main version, ack2&0x0f is sub version
    DGT_ACK_CLOCK_SETNRUN = 0x0a  # SetNRun ack
    DGT_ACK_CLOCK_BEEP = 0x0b  # Beep ack
    DGT_ACK_CLOCK_ASCII = 0x0c
    DGT_ACK_CLOCK_READY = 0x81
    DGT_ACK_CLOCK_BUTTON = 0x88  # Ack of a clock button
    DGT_ACK_CLOCK_MODE = 0x8a
    DGT_ACK_CLOCK_NOT_IN_MODE = 0x90


class DgtMsg(enum.IntEnum):

    """DESCRIPTION OF THE MESSAGES FROM BOARD TO PC."""

    MESSAGE_BIT = 0x80  # The Message ID is the logical OR of MESSAGE_BIT and ID code
    # ID codes
    DGT_NONE = 0x00
    DGT_BOARD_DUMP = 0x06
    DGT_BWTIME = 0x0d
    DGT_FIELD_UPDATE = 0x0e
    DGT_EE_MOVES = 0x0f
    DGT_BUSADRES = 0x10
    DGT_SERIALNR = 0x11
    DGT_TRADEMARK = 0x12
    DGT_VERSION = 0x13
    DGT_BOARD_DUMP_50B = 0x14  # Added for Draughts board
    DGT_BOARD_DUMP_50W = 0x15  # Added for Draughts board
    DGT_BATTERY_STATUS = 0x20  # Added for Bluetooth board
    DGT_LONG_SERIALNR = 0x22  # Added for Bluetooth board
    # DGT_MSG_BOARD_DUMP is the message that follows on a DGT_SEND_BOARD command
    DGT_MSG_BOARD_DUMP = (MESSAGE_BIT | DGT_BOARD_DUMP)
    DGT_SIZE_BOARD_DUMP = 67
    DGT_SIZE_BOARD_DUMP_DRAUGHTS = 103
    DGT_MSG_BOARD_DUMP_50B = (MESSAGE_BIT | DGT_BOARD_DUMP_50B)
    DGT_SIZE_BOARD_DUMP_50B = 53
    DGT_MSG_BOARD_DUMP_50W = (MESSAGE_BIT | DGT_BOARD_DUMP_50W)
    DGT_SIZE_BOARD_DUMP_50W = 53
    DGT_MSG_BWTIME = (MESSAGE_BIT | DGT_BWTIME)
    DGT_SIZE_BWTIME = 10
    DGT_MSG_FIELD_UPDATE = (MESSAGE_BIT | DGT_FIELD_UPDATE)
    DGT_SIZE_FIELD_UPDATE = 5
    DGT_MSG_TRADEMARK = (MESSAGE_BIT | DGT_TRADEMARK)
    DGT_MSG_BUSADRES = (MESSAGE_BIT | DGT_BUSADRES)
    DGT_SIZE_BUSADRES = 5
    DGT_MSG_SERIALNR = (MESSAGE_BIT | DGT_SERIALNR)
    DGT_SIZE_SERIALNR = 8
    DGT_MSG_LONG_SERIALNR = (MESSAGE_BIT | DGT_LONG_SERIALNR)
    DGT_SIZE_LONG_SERIALNR = 13
    DGT_MSG_VERSION = (MESSAGE_BIT | DGT_VERSION)
    DGT_SIZE_VERSION = 5
    DGT_MSG_BATTERY_STATUS = (MESSAGE_BIT | DGT_BATTERY_STATUS)
    DGT_SIZE_BATTERY_STATUS = 7
    DGT_MSG_EE_MOVES = (MESSAGE_BIT | DGT_EE_MOVES)
    # Definition of the one-byte EEPROM message codes
    EE_POWERUP = 0x6a
    EE_EOF = 0x6b
    EE_FOURROWS = 0x6c
    EE_EMPTYBOARD = 0x6d
    EE_DOWNLOADED = 0x6e
    EE_BEGINPOS = 0x6f
    EE_BEGINPOS_ROT = 0x7a
    EE_START_TAG = 0x7b
    EE_WATCHDOG_ACTION = 0x7c
    EE_FUTURE_1 = 0x7d
    EE_FUTURE_2 = 0x7e
    EE_NOP = 0x7f
    EE_NOP2 = 0x00
