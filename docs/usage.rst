Usage
=====

Setup the starting position
---------------------------
Place the pieces in starting position. It doesn't matter if you have the white or black pieces in front of you. Both ways will work. Keep in mind that with black pieces in front of you the (printed) coordinates of your dgt-board also reversed.
You can now start a game by moving a piece or press the middle button to let picochess start.

Also you can change the default settings of 5mins blitz against stockfish in strongest level by placing the white&black extra queen on the appropriate square or use the clock buttons (for detailed infomation see below).
Please keep in mind that placing the extra queens only working if you are in the starting position whereas the clock buttons always working regardless the chess position.

Playing/Training Modes
----------------------

When using these modes, please be patient and don't rush moves. Allow a few seconds for the scores and moves to appear. If you see any bug when rushing moves, let us know on the mailing list.

* Game mode is enabled by putting the **white** queen on the **A5** square. This is the default mode. You can play against the computer. The clock displays the remaining thinking time for both sides. Press the second button to show the position evaluation, expressed in centipawns. Press again to show a hint ("ponder move").
* Analysis mode (enabled by **white** queen on **B5**): the computer is watching the game, it does not play itself. The clock continually displays the best move for the side to play.
* Kibitz mode (enabled by **white** queen on **C5**): the computer is watching the game, it does not play itself. The clock continually displays the position score.
* Observe mode (enabled by **white** queen on **D5**): the computer is watching the game, it does not play itself. The clock displays the remaining thinking time for both sides. Press the second button once to show the position evaluation, twice to show a hint.
* Remote play mode (enabled by **white** queen on **E5**): this modus is right now not implemented (future use). It will allow you to play against someone over internet.

Game mode is the regular mode. If you used one of the other modes, you can return back to game mode by putting the extra **white** queen on **A5**.
You can also press the fourth button for toggling over the modes (Qa5-Qe5 only working in the starting position).

The position score will always be displayed in centipawns from White's perspective. For example when the clock displays 33, then White is ahead 33 centipawns (or 0.33 pawns). A negative score means black is ahead.

Choosing skill level
--------------------
Put the extra **black** queen on the 5th rank of your DGT board to select skill level. The skill range of ​​the currently selected engine is devided by 8 meaning a5 (easiest level) towards h5 (strongest level). Some engines support ELO level or even personalities instead of skill levels. If no skill level is selected, PicoChess uses the highest level if nothing choosen before or your last selected level by default.
(Remove the extra white queen if it is still on the board). Please notice that not all chess engines support levels.

In case of "stockfish" engine:
* Level  0 estimates about 1100 Elo (Absolute beginner)
* Level 10 estimates about 1750 Elo (Mediate club player )
* Level 20 estimates about 2570 Elo (Advanced tournament player)

Another way to choose the skill level is by entering the "engine" menu with the clock buttons. Detailed explanation is below.

Choosing opening books
----------------------

Opening books are set with the extra **black** queen.
(Remove the extra white queen if it is still on the board)

* **A3** - No book
* **B3** - ECO A - Flank
* **C3** - ECO B - Semiopen
* **D3** - ECO C - Open
* **E3** - ECO D - Closed
* **F3** - ECO E - Indian
* **G3** - Fun
* **H3** - Varied (Default)
* **A4** - GM_1950 (> 2500 ELO GM games from 1950 till 2013)
* **B4** - Performance
* **C4** - Stockfish optimized book v 2.11 by Salvo Spitaleri
* **D4** - Anand
* **E4** - Korchnoi
* **F4** - Larsen
* **G4** - Pro
* **H4** - GM 2001

Another way to choose the opening book is by entering the "Book" menu with the clock buttons. Detailed explanation is below.

Setting up time controls
------------------------

Picochess supports 3 variants of different time controls (Fixed, Blitz, Fischer). You can choose them by placing the extra **white** queen.
(Remove the extra black queen if it is still on the board).
Another way to choose the time control is by entering the "Time" menu with the clock buttons. Detailed explanation is below.

Fixed Levels
------------

Fixed time controls are set with the extra **white** queen.
(Remove the extra black queen if it is still on the board)

* **A6** - 1 second per move
* **B6** - 3 seconds per move
* **C6** - 5 seconds per move
* **D6** - 10 seconds per move
* **E6** - 15 seconds per move
* **F6** - 30 seconds per move
* **G6** - 60 seconds per move
* **H6** - 90 seconds per move

Blitz Levels
------------

Blitz time controls are set with the extra **white** queen.
(Remove the extra black queen if it is still on the board)

* **A4** - 1 minute game
* **B4** - 3 minute game
* **C4** - 5 minute game (Default)
* **D4** - 10 minute game
* **E4** - 15 minute game
* **F4** - 30 minute game
* **G4** - 60 minute game (1 hour)
* **H4** - 90 minute game (1 hour and 30 minutes)

Fischer Increment Blitz Levels
------------------------------

These are set with the extra **white** queen.
(Remove the extra black queen if it is still on the board)

* **A3** - 1 minute game with 1 second Fischer increment
* **B3** - 3 minute game with 2 second Fischer increment
* **C3** - 4 minute game with 2 second Fischer increment
* **D3** - 5 minute game with 3 second Fischer increment
* **E3** - 10 minute game with 5 second Fischer increment
* **F3** - 15 minute game with 10 second Fischer increment
* **G3** - 30 minute game with 15 second Fischer increment
* **H3** - 60 minute game with 30 second Fischer increment

Clock button support (general)
------------------------------

These chapters need to be written :-) Stay tuned.

System shutdown
---------------

From the start position, replace the white king with the extra white queen; this will shut down the machine (takes a few seconds until the blue light turns off). You can also do it with only the two white queens on the board (on e1,d1).

System reboot
---------------

From the start position, replace the black king with the extra black queen; this will reboot the machine (takes a few seconds until the blue light turns off). You can also do it with only the two black queens on the board (on e8,d8).

PGN file support
----------------

All moves of the played game along with engine are stored at the end of the game.
Every game played with picochess is stored in the /opt/picochess folder as "games.pgn".
If you want to end it before and write out the pgn file including the correct result, you can do as following:
Placing the two kings on opposite centre squares will signal a resignation:
    - If both kings on white, the result is white wins and the game recorded 1-0
    - If both kings on black, the result is black wins and the game recorded 0-1

Placing the kings on adjacent centre squares on the same rank signals a draw and the game recorded 1/2-1/2.
The 4 and 5 rank must be clear of other pieces - only kings.
