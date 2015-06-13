Usage
=====

Choosing skill level
--------------------
Put the extra **black** queen on your DGT board to select skill level. Putting it on square A6 will select level 0 (easiest), while B6 selects level 1, C6 selects level 2, etc. If no skill level is selected, PicoChess uses level 20 (the highest level) by default. Level 20 can also be selected by placing the extra black queen on square E4.

* Level  0 estimates about 1100 Elo (Absolute beginner)
* Level 10 estimates about 1750 Elo (Mediate club player )
* Level 20 estimates about 2570 Elo (Advanced tournament player)

Choosing opening books
----------------------

Opening books are also selected with the extra **black** queen:

* **A3** - No book
* **B3** - ECO A - Flank
* **C3** - ECO B - Semiopen
* **D3** - ECO C - Open
* **E3** - ECO D - Closed
* **F3** - ECO E - Indian
* **G3** - Fun
* **H3** - Varied. (Default)
* **H4** - GM_1950 (> 2500 ELO GM games from 1950 till 2013)
* **G4** - Performance
* **F4** - Stockfish optimized book v 2.11 by Salvo Spitaleri

Setting up time controls
------------------------

Time controls are set with the extra **white** queen.
(Remove the extra black queen if it is still on the board.)

* **A6** - 1 second per move
* **B6** - 3 seconds per move
* **C6** - 5 seconds per move
* **D6** - 10 seconds per move
* **E6** - 15 seconds per move
* **F6** - 30 seconds per move
* **G6** - 60 seconds per move
* **H6** - 120 seconds per move

Blitz Levels
------------

Blitz time controls are set with the extra **white** queen. Remove the extra black queen if it is still on the board.

* **A4** - 1 minute game
* **B4** - 3 minute game
* **C4** - 5 minute game
* **D4** - 10 minute game
* **E4** - 15 minute game
* **F4** - 30 minute game
* **G4** - 60 minute game (1 hour)
* **H4** - 90 minute game (1 hour and 30 minutes)

Fischer Increment Blitz Levels
------------------------------

These are set with the extra **white** queen. Remove the extra black queen if it is still on the board.

* **A3** - 3 minute game with 2 second Fischer increment
* **B3** - 4 minute game with 2 second Fischer increment
* **C3** - 5 minute game with 3 second Fischer increment
* **D3** - 5 minute game with 5 second Fischer increment
* **E3** - 15 minute game with 5 second Fischer increment
* **F3** - 25 minute game with 5 second Fischer increment
* **G3** - 90 minute game with 30 second Fischer increment

PicoChess with White
--------------------

To force PicoChess to play with White just take the black king off the board and put it back. If you want to play with White again just take the white king off the board and put it back. Note: You have to be in the starting position!

System shutdown
---------------

From the start position, replace the white king with the extra white queen; this will shut down the machine (takes a few seconds until the blue light turns off). You can also do it with only the two white queens on the board (on e1,d1).

Playing/Training Modes
----------------------

When using these modes, please be patient and don't rush moves. Allow a few seconds for the scores and moves to appear. If you see any bug when rushing moves, let us know on the mailing list.

* Game mode is enabled by putting the **white** queen on the **A5** square. This is the default mode. You can play against the computer. The clock displays the remaining thinking time for both sides. Press the second button to show the position evaluation, expressed in centipawns. Press again to show a hint ("ponder move").
* Analysis mode (enabled by **white** queen on **B5**): the computer is watching the game, it does not play itself. The clock continually displays the best move for the side to play.
* Kibitz mode (enabled by **white** queen on **C5**): the computer is watching the game, it does not play itself. The clock continually displays the position score in centipawns for the side to play. For example: if it's White's turn and the clock displays 33, then White is ahead 33 centipawns (or 0.33 pawns). A negative score means that the other side is ahead.
* Observe mode (enabled by **white** queen on **D5**): the computer is watching the game, it does not play itself. The clock displays the remaining thinking time for both sides. Press the second button once to show the position evaluation, twice to show a hint.

Game mode is the regular mode. If you used one of the other modes, you can return back to game mode by putting the extra **white** queen on **A5**.

(Todo: In a later version, the score will always be from White's perspective to be more consistent.)

Position setup
--------------

Before setting custom position, choose your level and time controls with pieces in starting position as usual.

Setup your position. Press the rightmost button until "Position" is displayed on the clock.
Press the leftmost button to choose side to move, Black or White.
Press the second button to choose the board orientation, Normal or Reversed.
Press center button, clock will respond with "Scan". Move.

Clock button support
--------------------

* First button shows the last move.
* Second button toggles between showing the value and the best/ponder move.
* Third button will switch sides and the computer will make your move.
* The fourth toggles between the game modes (Game, Analyse, Kibitz, Observe)
* The fifth toggles between "Position", "Engine", "System", "Game" options. Some of the options provide no functionality yet.

PGN file support
----------------

All moves of the played game along with engine are stored.
Every game played with picochess is stored in the /opt/picochess folder as "games.pgn".
If a position is undone, another game will be created within games.pgn.
