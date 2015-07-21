/**
* DGT Low Level EBoard Communication
* Copyright 2009 DGT
*
* Jan Krabbenbos
* $Id: dgtbrd.h 2962 2012-04-17 14:41:33Z vincent $
*/
#ifndef _DGTBRD_H_
#define _DGTBRD_H_

/**
Protocol description for DGT chess board. 
Copyright 1998-2014 DGT Projects B.V 

******************************************************************************
This protocol is protected under trade mark registration and copyrights.
It may not be used commercially without written permission
of DGT Projects B.V. It is illegal to transfer any registered trade mark
identifications by means of this protocol between any chessboard or other
application and any computer.
******************************************************************************

==============================================================================
Changes
==============================================================================
|20091013|Jan        |Merged draughts and chess board header file            |
|20091014|Jan        |Added clock message information                        |
|20100222|Jan        |Corrected the battery message information              |
|20111021|Vincent    |Added clock information, swapped Left and Right in     |
|                    |BwTime, swapped WCROWN and BDISK scan codes            |
|20120127|Vincent    |Changed DGT_LONG_SERIALNR to 0x22.                     |
|                    |Described EE_FOURROWS for 10x10 boards                 |
|20120202|Vincent    |Clock commands are terminated with 0x00                |
|20120213|Vincent    |Added EE_NOP2, described magic pieces                  |
|20120221|Jan        |Added clock information for displaying icons           |
|20120309|Vincent    |Added notes about clock commands                       |
|20120404|Vincent    |Described DGT_CMD_CLOCK_BEEP time duration calculation |
|20140709|Jan        |Added DGT3000 ascii clock message and RevelationII LED |
|        |           |control commands                                       |
|20141219|Ben        |Added description of S bit in DGT_MSG_FIELD_UPDATE     |
|20150720|Marius	 |Swapped D3 and D4 of byte9 of DGT_BWTIME to match 	 |
|		 |			 |the actual clock behaviour (D3-right), (D4-left)	 	 |
=============================================================================

Main functionality of the DGT Electronic Chess Board
----------------------------------------------------

The DGT board is basically a sensor which senses the presense of the special
chess set pieces on the squares of the board. The situation on the board is 
measured and can be communicated with an average maximum time delay of
200 mS.
Besides this detection function, the board communicates with an optional 
DGT TopMatch or XL Chess Clock, to give the data of the clock available to 
the general interface. 
Finally the board is equipped with an internal storage of the measured
piece positions.

The board supports two methods of communication: for single-board situations
a protocol for communication between one board and one computer is available.

For situations with many boards a network communications protocol is 
available, where many boards can be connected in a bus structure. A separate
communication protocol is available for this bus structure.

The communication protocol for single board connections is described
in the following paragraph "Single board communication protocol". This 
paragraph describes much more than only the communication protocol. All 
developers should read this paragraph, even if they would only use bus
communication.

The special bus communication protocol is derived from the single board
communication and functionality, where the main added feature is the 
possibility to address a specific board on a shared communication bus. 
The commands and data contens are described in the paragraph "Bus  
Communication Protocol", Note however that the contens can not be understood 
without reading the single board communication paragraph. 


Paragraph: Single board communication protocol
----------------------------------------------

The main function of the board is to transfer piece position information. 
For this, three modes are available:
1. IDLE mode. This cancelles any of the UPDATE modes. No automatic 
transfer of moves.
2. UPDATE_BOARD mode. On the moment that the board detects a removal, change
or placing of a piece, it outputs a DGT_SEND_UPDATE message
3. UPDATE mode. As UPDATE_BOARD mode, where additional the clock data are send
regularly (at least every second)
4. UPDATE_NICE mode. As UPDATE mode, but clock data is only sent when it has
changed.

The board accepts command codes from the computer RS232. The commands are
1-byte codes, sometimes followed by data (see code definition)
The board can send data to the computer. Data always carries a message header.
The message header contains a message code and the total message size in bytes.
The start of the incoming message can be recognised by the MSB of the message
identifier set to 1 (see definition).

Board to computer communication interfaces:
RS232 for communication with computer, receiving commands, sending data
- 9600 Baud, 1 stopbit, 1 startbit, no parity
- No use of handshaking, neither software nor hardware

Connection between Digital Game Timer TopMatch Clock and the board:
Based on NEC SBI protocol. Adaption of the definition given in
the DGT TopMatch documentation.

Connector assignments for DGT Electronic Board: See User
and Programmers Manual

Related to the before mentioned modes, and to piece position information
transfer, the following commands to the board are available:
1. DGT_SEND_RESET 
puts the DGT Board in IDLE mode 
2. DGT_SEND_CLK
on which the DGT board responds with a DGT_MSG_BWTIME message containing 
clock information
3. DGT_SEND_BRD
on which the DGT Board responds with a DGT_MSG_BOARD_DUMP message containing
the actual piece exising of all fields
4. DGT_SEND_UPDATE puts the DGT Board in the UPDATE mode, FRITZ5 compatible
5. DGT_SEND_UPDATE_BRD puts the DGT Board in the UPDATE_BOARD mode
6. DGT_SEND_UPDATE_NICE puts the board in UPDATE mode, however transferring
   only clocktimes when any time info changed.

The DGT_SEND_CLK command and the DGT_SEND_BOARD command do not affect the 
current board mode: i.e. when in UPDATE mode, it continues sending 
DGT_SEND_UPDATE messages.

Board Identification:
Each DGT Electronic Board carries a unique serial number, 
a EEPROM configuration version number and a embedded program version number.
These data are unalterable by the users.
An identification looks like:

"DGT Projects - This DGT board is produced by DGT Projects.\n
 DGT Projects is a registered trade mark.\n
 220798 ISP/bus/8KP/8KE/P6/Fritz5 Vs 1.00. Serial nr. 00137 1.0"

The board can be loaded by the user with a non-volatile one-byte bus number, 
for future use with multiple board configurations.

On-board EEPROM:
The board carries a 8 kB cyclic non-volatile memory, in which all position
changes and clock information is stored during all power-up time. This
file can be read and processed.

==============================================================================
Start of Definitions:
*/

/* ------------------------------------------------------------------------ */
/* COMMAND CODES FROM PC TO BOARD:                                          */
/* ------------------------------------------------------------------------ */
/* Commands not resulting in returning messages:                            */

#define DGT_SEND_RESET           0x40
/* Puts the board in IDLE mode, cancelling any UPDATE mode. 
 */

#define DGT_TO_BUSMODE           0x4a

/* This is an addition on the other single-board commands. This command is 
 * recognised in single-board mode. The RS232 output goes in 
 * pull-up mode and bus commands are immediatly recognised hereafter.
 * Note that when the board is in single-board mode, and eventually a bus 
 * mode command is found, this command is not processed, but the board 
 * switches to bus mode. The next (bus) command is processed regularly.
 */

#define DGT_STARTBOOTLOADER      0x4e
/* Makes a long jump to the FC00 boot loader code. Start FLIP now
 */




/* ------------------------------------------------------------------------ */
/* Commands resulting in returning message(s):                              */
/* ------------------------------------------------------------------------ */

#define DGT_SEND_CLK             0x41
/* Results in a DGT_MSG_BWTIME message
 */

#define DGT_SEND_BRD             0x42
/* Results in a DGT_MSG_BOARD_DUMP message
 */

#define DGT_SEND_UPDATE          0x43
/* Results in DGT_MSG_FIELD_UPDATE messages and DGT_MSG_BWTIME messages
 * as long as the board is in UPDATE mode  */

#define DGT_SEND_UPDATE_BRD      0x44
/* results in DGT_MSG_FIELD_UPDATE messages
 * as long as the board is in UPDATE_BOARD mode  */

#define DGT_RETURN_SERIALNR      0x45
/* Results in a DGT_MSG_SERIALNR message
*/

#define DGT_RETURN_BUSADRES      0x46
/* Results in a DGT_MSG_BUSADRES message
 */

#define DGT_SEND_TRADEMARK       0x47
/* Results in a DGT_MSG_TRADEMARK message
 */

#define DGT_SEND_EE_MOVES        0x49
/* Results in a DGT_MSG_EE_MOVES message
 */

#define DGT_SEND_UPDATE_NICE     0x4b
/* results in DGT_MSG_FIELD_UPDATE messages and DGT_MSG_BWTIME messages,
 * the latter only at time changes,
 * as long as the board is in UPDATE_NICE mode*/

#define DGT_SEND_BATTERY_STATUS	 0x4c
/* New command for bluetooth board. Requests the
 * battery status from the board. 
 */

#define DGT_SEND_VERSION         0x4d
/* Results in a DGT_MSG_VERSION message
 */

#define DGT_SEND_BRD_50B         0x50
/* Results in a DGT_MSG_BOARD_DUMP_50 message: only the black squares
 */

#define DGT_SCAN_50B             0x51
/* Sets the board in scanning only the black squares. This is written 
 * in EEPROM 
 */

#define DGT_SEND_BRD_50W         0x52
/* Results in a DGT_MSG_BOARD_DUMP_50 message: only the black squares
 */

#define DGT_SCAN_50W             0x53
/* Sets the board in scanning only the black squares. This is written in 
 * EEPROM.
 */

#define DGT_SCAN_100             0x54
/* Sets the board in scanning all squares. This is written in EEPROM 
 */

#define DGT_RETURN_LONG_SERIALNR 0x55
/* Results in a DGT_LONG_SERIALNR message   
 */

#define DGT_SET_LEDS             0x60
/* Only for the Revelation II to switch a LED pattern on. This is a command that
 * has three extra bytes with data:
 * byte 1 - DGT_SET_LEDS (= 0x60)
 * byte 2 - size (= 0x04)
 * byte 3 - the pattern to display (to be determined, for now: 0 - off, 1 - on)
 * byte 4 - the start field
 * byte 5 - the end field
 * byte 6 - end of message (= 0x00)
 * Start and end field have the range 0..63 where 0 is a8 and 63 is h1. This
 * is compliant with the DGT field coding of the board.
 * For the future it is foreseen that this message can have more fields which
 * can be controlled. This means also a different size of the message.
 */

/* ------------------------------------------------------------------------ */
/* Clock commands, returns ACK message if mode is in UPDATE or UPDATE_NICE  */
/* ------------------------------------------------------------------------ */
/*
 * USB/Serial: You cannot send multiple clock commands directly after each 
 * other. After each command, you should wait for the ack before sending the
 * next one. The ack is usually returned within one or two seconds.
 *
 * BT2.10: Clock commands are processed faster and more reliable, but note:
 * - When a clock command is sent, it is possible that an empty bwtime message
 * is returned (full of zeroes). This is to be ignored.
 * - Within 1000ms after sending a clock command (and receiving its ack),
 * subsequent clock update requests may return this ack instead of the clock
 * update. This is because the clock is polled only 2-3 times a second.
 *
 *
 */

#define DGT_CLOCK_MESSAGE        0x2b
/* This message contains a command for the clock. There are clock commands
 * for showing text, displaying icons, setting beep, clearing display,
 * and for setting clock times. All these clock commands are wrapped
 * within the DGT_CLOCK_MESSAGE command.
 * 
 * byte 1 - DGT_CLOCK_MESSAGE (= 0x2b)
 * byte 2 - the size
 * byte 3 - DGT_CMD_CLOCK_START_MESSAGE (= 0x03)
 * byte 4 - one of the 7 clock command id's
 * byte 5..n-1 - the content (can be empty)
 * byte n - DGT_CMD_CLOCK_END_MESSAGE (= 0x00)
 *
 * The clock messages can be sent in any board mode, but a SetNRun message is
 *   only processed if the clock is in mode 23.
 * The board responds with an DGT_MSG_ACK message if the board is in UPDATE or
 *   UPDATE_NICE mode. If the board is in IDLE or UPDATE_BRD mode, then no
 *   ack message is returned.
 */

#define DGT_CMD_CLOCK_DISPLAY  0x01
/*
 * This command can control the segments of six 7-segment characters,
 * two dots, two semicolons and the two '1' symbols.
 * These are arranged as follows: "1A:BC 1D:EF" and thus capable of
 * showing clock times or movetext of up to 6 chars (not counting the dots/'1').
 * "1A:BC 1D:EF" : the A..F are six characters with 7 segments, the '1' is a
 * single segment and the ':' has both a dot and semicolon segment.
 *
 * byte 1  - DGT_CMD_CLOCK_MESSAGE (= 0x2b)
 * byte 2  - Size (= 0x0b)
 * byte 3  - DGT_CMD_CLOCK_START_MESSAGE (= 0x03)
 * byte 4  - DGT_CMD_CLOCK_DISPLAY (= 0x01)
 * byte 5  - 'C' location segments. Bits: 0x01=top segment, 0x02=right top,
 *           0x04=right bottom, 0x08=bottom, 0x10=left bottom, 0x20=left top,
 *           0x40=center segment.
 * byte 6  - 'B' location segments. See 'C' location for the available bits.
 * byte 7  - 'A' location segments.
 * byte 8  - 'F' location segments.
 * byte 9  - 'E' location segments.
 * byte 10 - 'D' location segments.
 * byte 11 - icons: Bitmask for displaying dots and one's. 0x01=right dot, 
 *           0x02=right semicolon, 0x04=right '1', 0x08=left dot,
 *           0x10=left semicolon, 0x20=left '1'.
 * byte 12 - 0x03 if beep, 0x01 if no beep
 * byte 13 - DGT_CMD_CLOCK_END_MESSAGE (= 0x00)
*/

#define DGT_CMD_CLOCK_ICONS    0x02
/*
 * Used to control the clock icons like flags etc.
 *
 * byte 1 -  DGT_CMD_CLOCK_MESSAGE (= 0x2b)
 * byte 2 -  Size (= 0x0b)
 * byte 3 -  DGT_CMD_CLOCK_START_MESSAGE (= 0x03)
 * byte 4 -  DGT_CMD_CLOCK_ICONS (= 0x02)
 * byte 5 -  Icon data byte 0
 *           bit 0 - left TIME symbol
 *           bit 1 - left FISCH symbol
 *           bit 2 - left DELAY symbol
 *           bit 3 - left HGLASS symbol
 *           bit 4 - left UPCNT symbol
 *           bit 5 - left BYO symbol
 *           bit 6 - left END symbol
 *           bit 7 - not in use
 * byte 6 -  Icon data byte 1
 *           bit 0 - right TIME symbol
 *           bit 1 - right FISCH symbol
 *           bit 2 - right DELAY symbol
 *           bit 3 - right HGLASS symbol
 *           bit 4 - right UPCNT symbol
 *           bit 5 - right BYO symbol
 *           bit 6 - right END symbol
 *           bit 7 - not in use
 * byte 7 -  Icon data byte 2
 *           bit 0 - left period '1' symbol
 *           bit 1 - left period '2' symbol
 *           bit 2 - left period '3' symbol
 *           bit 3 - left period '4' symbol
 *           bit 4 - left period '5' symbol
 *           bit 5 - left flag symbol
 *           bit 6 - not in use
 *           bit 7 - not in use
 * byte 8 -  Icon data byte 3
 *           bit 0 - right period '1' symbol
 *           bit 1 - right period '2' symbol
 *           bit 2 - right period '3' symbol
 *           bit 3 - right period '4' symbol
 *           bit 4 - right period '5' symbol
 *           bit 5 - right flag symbol
 *           bit 6 - not in use
 *           bit 7 - not in use
 * byte 9 -  Special (clr / condat)
 *           bit 0 - if "1" all icons are cleared, if "0" no switch off
 *           bit 1 - sound symbol
 *           bit 2 - black - white symbol
 *           bit 3 - white - black symbol
 *           bit 4 - BAT signal
 *           bit 5 - sound symbol (again!)
 *           bit 6 - display pool selec "0" icons clear after time change
 *                   "1" icons stay visible
 *           bit 7 -
 * byte 10 - Reserved (= 0x00)
 * byte 11 - Reserved (= 0x00)
 * byte 12 - Reserved (= 0x00)
 * byte 13 - DGT_CMD_CLOCK_END_MESSAGE (= 0x00)
 */

#define DGT_CMD_CLOCK_END      0x03
/* This command clears the message and brings the clock back to the
 * normal display (showing clock times).
 * byte 1  - DGT_CMD_CLOCK_MESSAGE (= 0x2b)
 * byte 2  - Size (= 0x03)
 * byte 3  - DGT_CMD_CLOCK_START_MESSAGE (= 0x03)
 * byte 4  - DGT_CMD_CLOCK_END (= 0x03)
 * byte 5  - DGT_CMD_CLOCK_END_MESSAGE (= 0x00)
*/

#define DGT_CMD_CLOCK_BUTTON   0x08
/* 
 * Requests the current button pressed (if any).
 * byte 1  - DGT_CMD_CLOCK_MESSAGE (= 0x2b)
 * byte 2  - Size (= 0x03)
 * byte 3  - DGT_CMD_CLOCK_START_MESSAGE (= 0x03)
 * byte 4  - DGT_CMD_CLOCK_BUTTON (= 0x08)
 * byte 5  - DGT_CMD_CLOCK_END_MESSAGE (= 0x00)
 */

#define DGT_CMD_CLOCK_VERSION  0x09
/* This commands requests the clock version.
 * byte 1  - DGT_CMD_CLOCK_MESSAGE (= 0x2b)
 * byte 2  - Size (= 0x03)
 * byte 3  - DGT_CMD_CLOCK_START_MESSAGE (= 0x03) 
 * byte 4  - DGT_CMD_CLOCK_VERSION (= 0x09)
 * byte 5  - DGT_CMD_CLOCK_END_MESSAGE (= 0x00)
*/

#define DGT_CMD_CLOCK_SETNRUN  0x0a
/* This commands controls the clock times and counting direction, when
 * the clock is in mode 23. A clock can be paused or counting down. But
 * counting up isn't supported on current DGT XL's (1.14 and lower) yet.
 * 
 * byte 1  - DGT_CMD_CLOCK_MESSAGE (= 0x2b)
 * byte 2  - Size (= 0x0a)
 * byte 3  - DGT_CMD_CLOCK_START_MESSAGE (= 0x03)
 * byte 4  - DGT_CMD_CLOCK_SETNRUN (= 0x0a)
 * byte 5  - left hours (|0x10 if left counts up, but not supported)
 * byte 6  - left minutes
 * byte 7  - left seconds
 * byte 8  - right hours (|0x10 if right counts up, but not supported)
 * byte 9  - right minutes
 * byte 10 - right seconds
 * byte 11 - 0x01: left counts down. 0x02: right counts down.
               0x04: pause clock. 0x08: toggle player at lever change.
 * byte 12 - DGT_CMD_CLOCK_END_MESSAGE (= 0x00)
*/

#define DGT_CMD_CLOCK_BEEP     0x0b
/*
 * This clock command turns the beep on, for a specified time (64ms * byte 5)
 * byte 1 - DGT_CMD_CLOCK_MESSAGE (= 0x2b)
 * byte 2 - Size (= 0x04)
 * byte 3 - DGT_CLOCK_START_MESSAGE (= 0x03)
 * byte 4 - CMD_CLOCK_BEEP (= 0x0b) 
 * byte 5 - The time in multiplies of 64ms. E.g. a value of 16 plays the beep for 16*64=1024ms.
 * byte 6 - DGT_CMD_CLOCK_END_MESSAGE (= 0x00)
 */

#define DGT_CMD_CLOCK_ASCII    0x0c
/*
 * This clock commands sends a ASCII message to the clock that can be displayed only by
 * the DGT3000.
 * byte 1  - DGT_CMD_CLOCK_MESSAGE (= 0x2b)
 * byte 2  - Size (= 0x0c)
 * byte 3  - DGT_CLOCK_START_MESSAGE (= 0x03)
 * byte 4  - CMD_CLOCK_ASCII (= 0x0c)
 * byte 5  - Character 1
 * byte 6  - Character 2
 * byte 7  - Character 3
 * byte 8  - Character 4
 * byte 9  - Character 5
 * byte 10 - Character 6
 * byte 11 - Character 7
 * byte 12 - Character 8
 * byte 13 - Beep value 0 - 15, 0 is no beep, else else 62.5ms + (value / 16) * 1000ms 
 * byte 14 - DGT_CMD_CLOCK_END_MESSAGE (= 0x00)
 */

/* ------------------------------------------------------------------------ */
/* DESCRIPTION OF THE MESSAGES FROM BOARD TO PC 

A message consists of three header bytes:
MESSAGE ID             one byte, MSB (MESSAGE BIT) always 1
MSB of MESSAGE SIZE    one byte, MSB always 0, carrying D13 to D7 of the
					   total message length, including the 3 header byte
LSB of MESSAGE SIZE    one byte, MSB always 0, carrying  D6 to D0 of the
					   total message length, including the 3 header bytes
followed by the data:
0 to ((2 EXP 14) minus 3) data bytes, of which the MSB is always zero.
*/

/* ------------------------------------------------------------------------ */
/* DEFINITION OF THE BOARD-TO-PC MESSAGE ID CODES and message descriptions */

/* the Message ID is the logical OR of MESSAGE_BIT and ID code */
#define MESSAGE_BIT         0x80

/* ID codes: */
#define DGT_NONE            0x00
#define DGT_BOARD_DUMP      0x06
#define DGT_BWTIME          0x0d
#define DGT_FIELD_UPDATE    0x0e
#define DGT_EE_MOVES        0x0f
#define DGT_BUSADRES        0x10
#define DGT_SERIALNR        0x11
#define DGT_TRADEMARK       0x12
#define DGT_VERSION         0x13
/* Added for Draughts board  */
#define DGT_BOARD_DUMP_50B  0x14
#define DGT_BOARD_DUMP_50W  0x15
/* Added for Bluetooth board */
#define DGT_BATTERY_STATUS  0x20
#define DGT_LONG_SERIALNR   0x22

/* ------------------------------------------------------------------------ */
/* Macros for message length coding (to avoid MSB set to 1) */

#define BYTE    char

#define LLL_SEVEN(a) ((BYTE)(a & 0x7f))            /* 0000 0000 0111 1111 */
#define LLH_SEVEN(a) ((BYTE)((a & 0x3F80)>>7))   /* 0011 1111 1000 0000 */


/* ------------------------------------------------------------------------ */
/* DGT_MSG_BOARD_DUMP is the message that follows on a DGT_SEND_BOARD 
 * command
 */
#define DGT_MSG_BOARD_DUMP  (MESSAGE_BIT | DGT_BOARD_DUMP)
#define DGT_SIZE_BOARD_DUMP 67
#define DGT_SIZE_BOARD_DUMP_DRAUGHTS 103
/* message format:
 * byte 0: DGT_MSG_BOARD_DUMP
 * byte 1: LLH_SEVEN(DGT_SIZE_BOARD_DUMP) (=0 fixed)
 * byte 2: LLL_SEVEN(DGT_SIZE_BOARD_DUMP) (=67 fixed)
 * byte 3-66: Pieces on position 0-63
 *
 * Board fields are numbered from 0 to 63, row by row, in normal reading
 * sequence. When the connector is on the left hand, counting starts at
 * the top left square. The board itself does not rotate the numbering,
 * when black instead of white plays with the clock/connector on the left hand.
 * In non-rotated board use, the field numbering is as follows:
 *
 * Field A8 is numbered 0
 * Field B8 is numbered 1
 * Field C8 is numbered 2
 * ..
 * Field A7 is numbered 8
 * ..
 * Field H1 is numbered 63
 *
 * So the board always numbers the black edge field closest to the connector
 * as 57.
 */


/* Piece codes for chess pieces: */
#define EMPTY       0x00
#define WPAWN       0x01
#define WROOK       0x02
#define WKNIGHT     0x03
#define WBISHOP     0x04
#define WKING       0x05
#define WQUEEN      0x06
#define BPAWN       0x07
#define BROOK       0x08
#define BKNIGHT     0x09
#define BBISHOP     0x0a
#define BKING       0x0b
#define BQUEEN      0x0c
#define PIECE1      0x0d  /* Magic piece: Draw */
#define PIECE2      0x0e  /* Magic piece: White win */
#define PIECE3      0x0f  /* Magic piece: Black win */

/* For the draughts board */
#define WDISK       0x01
#define BDISK       0x04
#define WCROWN      0x07
#define BCROWN      0x0a

/* ------------------------------------------------------------------------ */
/* message format DGT_MSG_BOARD_DUMP_50B                                    */
#define DGT_MSG_BOARD_DUMP_50B  (MESSAGE_BIT|DGT_BOARD_DUMP_50B)
#define DGT_SIZE_BOARD_DUMP_50B 53
/* byte 0: DGT_MSG_BOARD_DUMP_50B
 * byte 1: LLH_SEVEN(DGT_SIZE_BOARD_DUMP) (=0 fixed)
 * byte 2: LLL_SEVEN(DGT_SIZE_BOARD_DUMP) (=53 fixed)
 * byte 3-52: Pieces on position 0-50
 */

/* ------------------------------------------------------------------------ */
/* message format DGT_MSG_BOARD_DUMP_50W                                    */
#define DGT_MSG_BOARD_DUMP_50W  (MESSAGE_BIT|DGT_BOARD_DUMP_50W)
#define DGT_SIZE_BOARD_DUMP_50W 53
/* byte 0: DGT_MSG_BOARD_DUMP_50w
 * byte 1: LLH_SEVEN(DGT_SIZE_BOARD_DUMP) (=0 fixed)
 * byte 2: LLL_SEVEN(DGT_SIZE_BOARD_DUMP) (=53 fixed)
 * byte 3-52: Pieces on position 0-50
 */

/* ------------------------------------------------------------------------ */
/* message format DGT_MSG_BWTIME                                            */
#define DGT_MSG_BWTIME      (MESSAGE_BIT | DGT_BWTIME)
#define DGT_SIZE_BWTIME     10
/*
 * There are two possible distinct BwTime messages: 1) Clock Times, 2) Clock Ack.
 * The total size is always 10 bytes and the first byte is always DGT_MSG_BWTIME (=0x4d).
 * If the (4th byte & 0x0f) equals 0x0a, or if the (7th byte & 0x0f) equals 0x0a, then the 
 * message is a Clock Ack message. Otherwise it is a Clock Times message.
 *
 * Clock Times:
 * 
 * byte 0: DGT_MSG_BWTIME
 * byte 1: LLH_SEVEN(DGT_SIZE_BWTIME) (=0 fixed)
 * byte 2: LLL_SEVEN(DGT_SIZE_BWTIME) (=10 fixed)
 * byte 3:
 * D0-D3: Hours (units, 0-9 Binary coded) of right player.
 *  (If (byte 3 & 0x0f) is 0x0a, then the msg is a Clock Ack message instead)
 * D4: 1 = Flag fallen for right player, and clock blocked to zero
 *     0 = not the above situation
 * D5: 1 = Time per move indicator on for right player ( i.e. Bronstein, Fischer)
 *     0 = Time per move indicator off for right player
 * D6: 1 = Right players flag fallen and indicated on display,
 *           clock possibly still running (e.g. activation of next time period)
 *     0 = not the above situation
 * (D7 is MSB)
 * byte 4: Minutes (0-59, BCD coded)
 * byte 5: Seconds (0-59, BCD coded)
 * byte 6-8: the same for the left player
 * byte 9: Clock status byte: 7 bits
 * D0 (LSB): 1 = Clock running
 *           0 = Clock stopped by Start/Stop
 * D1: 1 = tumbler position high on right player (front view: / , right side high)
 *     0 = tumbler position high on left player (front view: \, left side high)
 * D2: 1 = Battery low indication on display
 *     0 = no battery low indication on display
 * D3: 1 = Right player's turn
 *     0 = not Right player's turn
 * D4: 1 = Left player's turn
 *     0 = not Left player's turn
 * D5: 1 = No clock connected; reading invalid
 *     0 = clock connected, reading valid
 * D6: not used (read as 0)
 * D7:  Always 0
 *
 *
 * Clock Ack:
 *
 * byte 0: DGT_MSG_BWTIME
 * byte 1: LLH_SEVEN(DGT_SIZE_BWTIME) (=0 fixed)
 * byte 2: LLL_SEVEN(DGT_SIZE_BWTIME) (=10 fixed)
 * byte 3-9: used to construct a 4-byte ack message in the following way:
 * 
 * ack0 = ((byte4) & 0x7f) | ((byte6 << 3) & 0x80);
 * ack1 = ((byte5) & 0x7f) | ((byte6 << 2) & 0x80);
 * ack2 = ((byte7) & 0x7f) | ((byte3 << 3) & 0x80);
 * ack3 = ((byte8) & 0x7f) | ((byte3 << 2) & 0x80);
 *
 * So ack0 is constructed from bits 0-6 from byte4, and bit 4 from byte6 (which goes
 *   to ack0's 7th bit).
 *
 * ack0: 0x40 indicates an error, e.g. sending a CMD_CLOCK_SETNRUN while the
 *   clock is not in mode 23.
 * ack0 is 0x10 for normal ack messages.
 * ack1: if 8th bit set (i.e. (ack1 & 0x80)==0x80), then it is an auto-generated ack.
 *   Otherwise it is a response to a command.
 *
 * Auto-generated acks:
 *    ack1==0x81: ready
 *    ack1==0x88: Button pressed. ack3: Back=0x31; Plus=0x32; Run=0x33; Minus=0x34; OK=0x35.
 *    ack1==0x8a: mode 23? ack3 contains the mode?
 *    ack1==0x90: not in mode 23?
 *
 *  Response to command ack's:
 *  ack1 is the command that was ack'ed.
 *    ack1==0x01: Display ack.
 *    ack1==0x08: Buttons ack, but no button information is returned though.
 *    ack1==0x09: Version ack. ack2>>4 is main version, ack2&0x0f is sub version.
 *    ack1==0x0a: SetNRun ack.
 *    ack1==0x0b: Beep ack.
 *
 * 
 */

/* ------------------------------------------------------------------------ */
/* message format DGT_MSG_FIELD_UPDATE:                                     */
#define DGT_MSG_FIELD_UPDATE (MESSAGE_BIT | DGT_FIELD_UPDATE)
#define DGT_SIZE_FIELD_UPDATE   5
/* byte 0: DGT_MSG_FIELD_UPDATE
 * byte 1: LLH_SEVEN(DGT_SIZE_FIELD_UPDATE) (=0 fixed)
 * byte 2: LLL_SEVEN(DGT_SIZE_FIELD_UPDATE) (=5 fixed)
 * byte 3: field number (0-63) which changed the piece code
 * byte 4: piece code including EMPTY, where a non-empty field became empty
 */

/* ------------------------------------------------------------------------ */
/* message format: DGT_MSG_TRADEMARK which returns a trade mark message     */
#define DGT_MSG_TRADEMARK  (MESSAGE_BIT | DGT_TRADEMARK)
/* byte 0: DGT_MSG_TRADEMARK
 * byte 1: LLH_SEVEN(DGT_SIZE_TRADEMARK)
 * byte 2: LLL_SEVEN(DGT_SIZE_TRADEMARK)
 * byte 3-end: ASCII TRADEMARK MESSAGE, codes 0 to 0x3F
 * The value of DGT_SIZE_TRADEMARK is not known beforehand, and may be in the
 * range of 0 to 256
 * Current trade mark message: ...
 */

/* ------------------------------------------------------------------------ */
/* Message format DGT_MSG_BUSADRES return message with bus adres            */
#define DGT_MSG_BUSADRES    (MESSAGE_BIT | DGT_BUSADRES)
#define DGT_SIZE_BUSADRES   5
/* byte 0: DGT_MSG_BUSADRES
 * byte 1: LLH_SEVEN(DGT_SIZE_BUSADRES)
 * byte 2: LLL_SEVEN(DGT_SIZE_BUSADRES)
 * byte 3,4: Busadres in 2 bytes of 7 bits hexadecimal value
 *           byte 3: 0bbb bbbb with bus adres MSB 7 bits
 *           byte 4: 0bbb bbbb with bus adres LSB 7 bits
 * The value of the 14-bit busadres is het hexadecimal representation
 * of the (decimal coded) serial number
 * i.e. When the serial number is "01025 1.0" the busadres will be
 *      byte 3: 0000 1000 (0x08)
 *      byte 4: 0000 0001 (0x01)
 */

/* ------------------------------------------------------------------------ */
/* Message format DGT_MSG_SERIALNR return message with bus adres            */
#define DGT_MSG_SERIALNR       (MESSAGE_BIT | DGT_SERIALNR)
#define DGT_SIZE_SERIALNR      8
/* Returns 5 ASCII decimal serial number:
 * byte 0-5 serial number string, sixth byte is LSByte
 */

/* ------------------------------------------------------------------------ */
/* Message format DGT_LONG_SERIALNR                                         */
#define DGT_MSG_LONG_SERIALNR	(MESSAGE_BIT | DGT_LONG_SERIALNR)
#define DGT_SIZE_LONG_SERIALNR	13
/* byte 0: DGT_LONG_SERIALNR
 * byte 1:  0
 * byte 2: DGT_SIZE_ LONG_SERIALNR
 * byte 3-12: 10 ASCII decimal serial number
 * The 10th character is Least Significant
 */

/* ------------------------------------------------------------------------ */
/* Message format DGT_MSG_VERSION return message with bus adres             */
#define DGT_MSG_VERSION    (MESSAGE_BIT | DGT_VERSION)
#define DGT_SIZE_VERSION   5
/* byte 0: DGT_MSG_VERSION
 * byte 1: LLH_SEVEN(DGT_SIZE_VERSION)
 * byte 2: LLL_SEVEN(DGT_SIZE_VERSION)
 * byte 3,4: Version in 2 bytes of 7 bits hexadecimal value
 *           byte 3: 0bbb bbbb with main version number MSB 7 bits
 *           byte 4: 0bbb bbbb with sub version number LSB 7 bits
 * The value of the version is coded in binary
 * i.e. When the number is "1.02" the busadres will be
 *      byte 3: 0000 0001 (0x01)
 *      byte 4: 0000 0010 (0x02)
 */

/* ------------------------------------------------------------------------ */
/* Retrieve the battery status from the Bluetooth board                     */
#define DGT_MSG_BATTERY_STATUS	(MESSAGE_BIT | DGT_BATTERY_STATUS)
#define DGT_SIZE_BATTERY_STATUS	7
/* byte  0: DGT_MSG_BATTERY_STATUS
 * byte  1: LLH_SEVEN(DGT_SIZE_BATTERY_STATUS)
 * byte  2: LLL_SEVEN(DGT_SIZE_BATTERY_STATUS)
 * byte  3: Current battery capacity left in %
 * byte  4: Running/Charging time left (hours)    (0x7f is N/A)
 * byte  5: Running/Charging time left (minutes)  (0x7f is N/A)
 * byte  6: On time (hours)
 * byte  7: On time (minutes)
 * byte  8: Standby time (days)
 * byte  9: Standby time (hours)
 * byte 10: Standby time (minutes)
 * byte 11: Status bits
 *         bit 0: Charge status
 *         bit 1: Discharge status
 *         bit 2: Not yet implemented
 *         bit 3: Not yet implemented
 *         bit 4: Not yet implemented
 *         bit 5: Not yet implemented
 *         bit 6: Not yet implemented
 *         bit 7: Not yet implemented
 */



/* ------------------------------------------------------------------------ */
/* DGT_SIZE_EE_MOVES is defined in dgt_ee1.h: current (0x2000-0x100+3)      */
#define DGT_MSG_EE_MOVES  (MESSAGE_BIT | DGT_EE_MOVES)
/* Message format DGT_MSG_EE_MOVES, which is the contens of the storage array
 * byte 0: DGT_MSG_EE_MOVES
 * byte 1: LLH_SEVEN(DGT_SIZE_EE_MOVES)
 * byte 2: LLL_SEVEN(DGT_SIZE_EE_MOVES)
 * byte 3-end: field change storage stream: See defines below for contents
 * 
 * The DGT_MSG_EE_MOVES message contains the contens of the storage,
 * starting with the oldest data, until the last written changes, and will
 * always end with EE_EOF
 */

/* ------------------------------------------------------------------------ */

/* 
Description of the EEPROM data storage and dump format
------------------------------------------------------

General: The internal EEPROM storage can be seen as a cyclic buffer with length
0x1f00 bytes, with one pointer, pointing to the last written byte in the buffer.
Only at this pointer location, data can be written, incrementing the pointer.
The written data always overwrites the oldest data. 
In this buffer, sequentially messages are written. The messages are of various
length, from 1 byte to 5 bytes, specific for every message. 
Various events generate a message that is written in the storage, in the 
sequence as the events occur. When the buffer is downloaded and read, the event
messages can be found, starting with the oldest event, and the latest event in
the end of the buffer, followed by EE_EOF.

- At power-on, three tags EE_NOP are written, followed by a one-byte 
EE_POWERUP message. 
After this, an UPDATE_BOARD message is written (in virtually random sequence)
for every piece that is found on the board, at power-on.
When the board is equipped with a watchdog timer, and the watchdog times out,
an EE_WATCHDOG_ACTION is written and after that, the above described power-up 
procedure takes place.

- When at any time a normal starting position for chess is found, with the 
player for white having the board connector on his left hand, an EE_BEGINPOS tag
is written, and an EE_BEGINPOS_ROT tag is written when white has the
connector at his right hand (rotated)

- 8x8 board: When 16 chess figures are found on the board, all in the A, B, G 
and H row, which are not(!) in a normal chess starting position, the one-byte
EE_FOURROWS message is written, to be tolerant on erroneous placement and i.e.  
to be able to play the "Random Chess" as proposed by Bobby
Fischer. The exact position of the pieces has to be analyzed on the context: 
or found in the previous piece move messages, or found in the
coming piece move messages.

- For 10x10 boards, EE_FOURROWS indicates a position of which the center TWO
rows are empty and all other fields are occupied.

When an empty board is detected, the one-byte EE_EMPTYBOARD message is
written.

The above described detection of begin positions or empty-board has a certain
hysteresis: only after more than two pieces have been out of the begin 
positions the search for begin positions is restarted, resulting in possibly
new tag writing. This to avoid flushing the buffer full with data, only because
of one bad positioned and flashing piece.

When the data of the internal storage are sent upon reception of the
DGT_SEND_EE_MOVES command, the one-byte EE_DOWNLOADED message is sent

On every detected change of piece positions this change is written to EEPROM
in a 2-byte message, which cover exactly the same data as is sent to the PC
in the UPDATE_BOARD mode.
The formatting of the 2-byte piece update tag is:
First byte:     0t0r nnnn (n is piece code, see before)
			  (piece code EMPTY when a piece is removed)
			  (t is recognition bit, always 1)
			  (r is '1' when the time since the previous update 
			   tag was written is less than approx. 250 ms, 
			   otherwise '0')
		so the first byte of this tag is always in the 
		range 0x40 to 0x5f
Second byte:    00ii iiii (i = 0 to 63 (0x3f), the field number as
			   defined before)

NB: when one piece only is changing, the new value is overwrites the 
piece update field described above, instead of generating a new message
in the internal storage. 
The same kind of optimization is included for begin-position tags:
a EE_BEGINPOS or EE_BEGINPOS_ROT or EE_FOURROWS is not written, when 
between the previous written tags and the new occurence of the begin-
situation only 2 or 1 piece were out of the tagged beginsituation.

On the pressing of the clock, the time of the halted clock is written in
a time message. It might be that when the moves are done very fast, the
storage is skipped. Note: the two clock sides are identified only by
left and right side of the clock: When the board is swapped, the clock
data are not (!) swapped.

The clock data are written on tumbler position change, so at the beginning
of the game, the game starting times will be lost.

Format of a three-byte time message:
First byte:    0uuf hhhh (f=1 for time in left clock screen, seen from
			  the front)
			 ( hhhh: hours, valued 0 to 9)
			 (uu recognition bits, both 1, so byte 0 has the
			 ( value range of 0x60 to 0x69, or 0x70 to 0x79)
Second byte:   0MMM mmmm (MMM: Tens of minutes (range 0 to 5),
			 (mmmm: minute units, range 0 to 9)

Third byte:    0SSS ssss (SSS: tens of seconds, range 0-5)
			 (ssss: seconds units, range 0-9)

On the recognition of the first byte of a message: The above definitions
imply that the first byte of a message is always ranged
from 40-5f for a field change message, 60-69 or 70-79 for a time message,
and 6a to 6f, or 7a to 7f for a 1-byte message. 
(all values hexadecimal)
*/

/* Definition of the one-byte EEPROM message codes */

#define EE_POWERUP         0x6a
#define EE_EOF             0x6b
#define EE_FOURROWS        0x6c
#define EE_EMPTYBOARD      0x6d
#define EE_DOWNLOADED      0x6e
#define EE_BEGINPOS        0x6f
#define EE_BEGINPOS_ROT    0x7a
#define EE_START_TAG       0x7b
#define EE_WATCHDOG_ACTION 0x7c
#define EE_FUTURE_1        0x7d
#define EE_FUTURE_2        0x7e
#define EE_NOP             0x7f
#define EE_NOP2            0x00

/* 7d and 7e are reserved for future use*/

/*
Notes on the communication dynamics:
The squares of the board are sampled one by one, where a full scan takes
about 200-250 ms. Due to this scan time, it can be, that a piece that is
moved from square e.g. A2 to A3 can be seen on both squares, in the same
scan. On a next scan of course, the old position is not seen anymore.
When in UPDATE mode, this means, that the information on changes on the
squares can come in opposite sequence: first the new occurence is reported,
then the clearing of the old position is sent.
When a piece B on C4 is taken by piece A on B3, it can be that the following
changes are reported:
A on C4
Empty on B3
(and Empty on C4 is never seen)
An other extreme situation can occur e.g. when a queen on C1 takes a pawn
on C4. The reported changes can be (in sequence):
Empty on C4 (the pawn is taken by one hand)
Queen on C2
Queen on C3
Empty on C1
Empty on C2
Queen on C4
Empty on C3
For writing software it is important to take these dynamics into account.
Some effort needs to be made to reconstruct the actual moves of the pieces.
See also the programmers and users manual

------------------------------------------------------------------------------

Paragraph: Bus communication protocol
-------------------------------------

Differencens between busmode and single board mode:
* In bus mode, RS232 input and RS232 output are connected to all boards.
The RS232 output of the board is configured as a pull-up driver: with a 
pull-down resistor on the RS232 pull-up line. Now all boards receive all 
commands from the computer, and can all send data to the computer.
* In single board mode the board has a small incoming commands
buffer (10 bytes).
* The bus mode has only a one-command incoming commands buffer
* When entered in single board mode, the board status always switches to IDLE:
changes are not send automatically

Bus mode is default power up mode of the board. The board recognises
bus commands from the start.
However, single board commands are recognised and answered.
The board switches to single board mode on the moment, a single board
command is recognised. Switching back to bus mode is invoked by the 
extra command DGT_TO_BUSMODE or by sending a busmode command. (NB This 
busmode command causing the swithing is not processed!)

For all detailed hardware descriptions: call.
*/


/* ------------------------------------------------------------------------ */
/* Bus mode commands:                                                       */
#define DGT_BUS_SEND_CLK             (0x01 | MESSAGE_BIT)
#define DGT_BUS_SEND_BRD             (0x02 | MESSAGE_BIT)
#define DGT_BUS_SEND_CHANGES         (0x03 | MESSAGE_BIT)
#define DGT_BUS_REPEAT_CHANGES       (0x04 | MESSAGE_BIT)
#define DGT_BUS_SET_START_GAME       (0x05 | MESSAGE_BIT)
#define DGT_BUS_SEND_FROM_START      (0x06 | MESSAGE_BIT)
#define DGT_BUS_PING                 (0x07 | MESSAGE_BIT)
#define DGT_BUS_END_BUSMODE          (0x08 | MESSAGE_BIT)
#define DGT_BUS_RESET                (0x09 | MESSAGE_BIT)
#define DGT_BUS_IGNORE_NEXT_BUS_PING (0x0a | MESSAGE_BIT)
#define DGT_BUS_SEND_VERSION         (0x0b | MESSAGE_BIT)
#define DGT_BUS_SEND_BRD_50B         (0x0c | MESSAGE_BIT)
// sends consequitively: CHANGES, CLOCK, BOARD:
#define DGT_BUS_SEND_ALL_D           (0x0d | MESSAGE_BIT) 


/* ------------------------------------------------------------------------ */
/* extra return headers for bus mode:                                       */
#define DGT_MSG_BUS_BRD_DUMP           (0x03 | MESSAGE_BIT)
#define DGT_MSG_BUS_BWTIME             (0x04 | MESSAGE_BIT)
#define DGT_MSG_BUS_UPDATE             (0x05 | MESSAGE_BIT)
#define DGT_MSG_BUS_FROM_START         (0x06 | MESSAGE_BIT)
#define DGT_MSG_BUS_PING               (0x07 | MESSAGE_BIT)
#define DGT_MSG_BUS_START_GAME_WRITTEN (0x08 | MESSAGE_BIT)
#define DGT_MSG_BUS_VERSION            (0x09 | MESSAGE_BIT)
#define DGT_MSG_BUS_BRD_DUMP_50B       (0x0a | MESSAGE_BIT)

/* ------------------------------------------------------------------------ */
/* extra defines for bus length info:                                       */
#define DGT_SIZE_BUS_PING               6
#define DGT_SIZE_BUS_START_GAME_WRITTEN 6
#define DGT_SIZE_BUS_VERSION            8        /* was 6 up to version 1.2 */

/* ------------------------------------------------------------------------ */
/* Definition of different commands & data

All commands DGT_BUS_xx have the following format:
byte 1: command, i.e. DGT_BUS_SEND_BDR (D7 always 1)
byte 2: MSB of addressed board (D7 always 0)
byte 3: LSB of addressed board (D7 always 0)
byte 4: checksum: this is the sum of all bytes from start of the message
	upto the last byte before the checksum. (D7 always 0)
	I.e. message code 0x81 0x10 0x06 will carry checksum byte 0x17

DGT_BUS_SEND_CLK
asks for clock information of addressed board.
Will result in a DGT_MSG_BUS_BWTIME message from the board.

DGT_BUS_SEND_BRD
asks for a board dump of addressed board.
Will result in a DGT_MSG_BUS_BRD_DUMP message from the board.

DGT_BUS_SEND_CHANGES
asks for all stored information changes from the moment of the last
DGT_BUS_SEND_CHANGES. Will result in a DGT_MSG_BUS_UPDATE message from 
the board.
In case these data do not arrive properly, the data can be asked again
with the DGT_BUS_REPEAT_CHANGES command.

DGT_BUS_REPEAT_CHANGES
Causes the board to send last sent packet of changes again.

DGT_BUS_SET_START_GAME
sets an EE_START_TAG tag in the internal board changes buffer, for use in the
following command DGT_BUS_SEND_FROM_START. After this EE_START_TAG the 
positions of the pieces are all logged in the file.
The command is answered with a DGT_MSG_BUS_START_GAME_WRITTEN message,
about 70 msec. after receipt of DGT_BUS_SET_START_GAME

DGT_BUS_SEND_FROM_START
causes the board to send a DGT_MSG_BUS_FROM_START message, containing
all update information starting with EE_START_TAG until the last registered
changes (excluding the moves that are to be sent with the DGT_BUS_SEND_CHANGES
command). Remember that after the EE_START_TAG all piece positions are written
in the eeprom file.

DGT_BUS_PING
causes the addressed board to send a DGT_MSG_BUS_PING message.
NB: when the DGT_BUS_PING command is sent with board address 0 (zero )
all connected boards will reply with a DGT_MSG_BUS_PING message, randomly
spread over a 1100 msec. interval. This to avoid collision. For reliable
identification of all connected boards, this process should be repeated
sometimes with checking of checksums!

DGT_IGNORE_NEXT_BUS_PING
is used in the process of detecting connected boards on a bus. After this 
command (which itself sends a DGT_MSG_BUS_PING as handshake) the first
following DGT_BUS_PING with address zero (!) is ignored. This command
can be used to suppress response of already detected boards, and decreases
the chance of bus collisions.
This command responds immediately with a DGT_MSG_BUS_PING.

DGT_BUS_END_BUSMODE
causes the board to quit busmode, and go into single-connection mode.
Be careful not to use this command in a multiple board configuration!
NOTE: Any single-board command arriving during bus mode will 
switch a board to single-board mode and will be processed. When sent
with address 0 the command is processed on all connected boards

DGT_BUS_RESET
forces a power-up reset procedure. NB: this procedure takes some seconds.
When sent with address 0 the command is processed on all conected boards

------------------------------------------------------------------------------

DEFINITION OF THE MESSAGE DATA FORMATS FROM BOARD TO PC
------------------------------------------------------------------------------

General: the message format is:
byte 1: message type byte (MSB = 1)
byte 2: message length MSB (from byte 1 to checksum) (D7=0)
byte 3: message length LSB (containing D0 to D6 of the length (D7 = 0)
byte 4: board address MSB (D7=0)
byte 5: board address LSB (D7=0)
< data bytes: 0 to theoretically 16K-6 bytes >
last byte: checksum. This is the sum of all byte values from byte 1 to
	   the byte before this checksum. D7 is forced to 0

DGT_MSG_BUS_BRD_DUMP
the data area contains the piece codes from field 1 to field 64, in format
identical as the single board command

DGT_MSG_BUS_BWTIME
the data area contains the clock time information, in format identical as
the single board command

DGT_MSG_BUS_UPDATE
the data area contains a variable amount of change information, formatted
as described in the DGT_DUMP_EEMOVES message

DGT_MSG_BUS_FROM_START
the data area contains a variable amount of change information, formatted
as described in the DGT_DUMP_EEMOVES message

DGT_MSG_BUS_PING
the data area is empty: a message of 6 bytes is returned.

DGT_MSG_BUS_START_GAME_WRITTEN
The same format as for DGT_MSG_BUS_PING

DGT_MSG_BUS_VERSION
The two data bytes contain binary version number: first byte main number
second byte sub number.

Tips for usage of the bus mode:

A. On connection of power and starting of the communication process:
- Check communication with addressed DGT_BUS_PING commands to all expected
  boards.
LOOP:
- Send DGT_BUS_IGNORE_NEXT_PING to all found boards
- Check eventually extra boards or unknown board busnumbers by using
  a DGT_BUS_PING with address zero.
- Register the found boards, and go to LOOP:, until no more boards are found


B. At the start of an event: when all boards have pieces in starting
 position, send DGT_BUS_SET_START_GAME commands to all boards.
- Read full clock times from all boards.

C. During a game: send DGT_BUS_SEND_CHANGES to all boards sequentially,
 once every few seconds. The returned data should logically match
 with the expected piece positions. When any mismatch occurs: ask full
 position with DGT_BUS_SEND_BRD.

D. When previous data are lost: send a DGT_BUS_SEND_FROM_START command
 which returns the full registered changes from the starting position.

On every sent message: The responce time at the board is within milliseconds
normally, except when the board is storing a measured change in the
internal EEPROM: Then the responce time can be up to 20 milliseconds.
So allow a time-out on sent messages of say 80 mS.

Checksum errors: when a received checksum does not match, resend the command
except on the DGT_BUS_SEND_CHANGES: then the command DGT_BUS_REPEAT_CHANGES
should be used, to avoid discarding of the changes sent by the board.

On clock data:
- reading data out of the clock and make them available
  for communication causes a delay of up to 1 second between clock display
  and received data.
*/
#endif

