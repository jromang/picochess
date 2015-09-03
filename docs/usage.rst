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
Put the extra **black** queen on your DGT board to select skill level. Putting it on square A6 will select level 0 (easiest), while B6 selects level 1, C6 selects level 2, etc. If no skill level is selected, PicoChess uses level 20 (the highest level) by default. Level 20 can also be selected by placing the extra black queen on square E4.
(Remove the extra white queen if it is still on the board.)

* Level  0 estimates about 1100 Elo (Absolute beginner)
* Level 10 estimates about 1750 Elo (Mediate club player )
* Level 20 estimates about 2570 Elo (Advanced tournament player)

Another way to choose the skill level is by entering the "Level" menu with the clock buttons. Detailed explanation is below.

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
* **H3** - Varied. (Default)
* **H4** - GM_1950 (> 2500 ELO GM games from 1950 till 2013)
* **G4** - Performance
* **F4** - Stockfish optimized book v 2.11 by Salvo Spitaleri

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
* **H6** - 120 seconds per move

Blitz Levels
------------

Blitz time controls are set with the extra **white** queen.
(Remove the extra black queen if it is still on the board)

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

These are set with the extra **white** queen.
(Remove the extra black queen if it is still on the board)

* **A3** - 3 minute game with 2 second Fischer increment
* **B3** - 4 minute game with 2 second Fischer increment
* **C3** - 5 minute game with 3 second Fischer increment
* **D3** - 5 minute game with 5 second Fischer increment
* **E3** - 15 minute game with 5 second Fischer increment
* **F3** - 25 minute game with 5 second Fischer increment
* **G3** - 90 minute game with 30 second Fischer increment


Clock button support (general)
------------------------------

The fifth (right most) button toggles between "Game", "Position", "Level", "Time", "Engine", "Book", "System" menus.
Depending with menu you choose, the other 4 buttons have different functionality. Its explained in detail below.

* **Game Menu** - Regular Menu Shows Infos during game playing
* **Position Menu** - Setup a custom position
* **Level Menu** - Change the skill level
* **Time Menu** - Change time controls
* **Engine Menu** - Change the engine
* **Book Menu** - Change the opening book
* **System Menu** - Shutdown/Reboot the machine

Clock buttons (in Game menu)
----------------------------

* First button shows the last move
* Second button toggles between showing the position value (or "book") and the best/ponder (or book move)
* Third button will
    - in **Game mode** switch sides and the computer will make next move (your turn) or stop the search and play out the best move (computer turn)
    - in **Observe/Remote mode** halt/start the clock
    - in **Analysis/Kibitz mode** no function. An error message is displayed
* The fourth will toggle between the playing modes (Game, Analysis, Kibitz, Observe, Remote)

Clock buttons (in Position menu)
--------------------------------

First setup your position.

* First button chooses the side to move, Black or White
* Second button chooses the board orientation, "b" & "w" showing the starting side for each color. So for example white pawns moving from w to b side
* Third button scans in the position on board. Clock will respond with "scan" and "new game". Now picochess is waiting for your next move. If you want picochess to start press the third button
* Fouth button has no function

Clock buttons (in Level menu)
-----------------------------

* First button shows the current selected skill level
* Second button goes down in skill level
* Third button chooses the current selected level
* Fourth button goes up in skill level

Clock buttons (in Time menu)
----------------------------

* First button cycles through "Fischer", "Fixed" and "Blitz" time controls
* Second button goes down in the time control list of the type currently in use ("Fischer", "Fixed" or "Blitz")
* Third button chooses the selected time control
* Fourth button goes up in the time control list of the type currently in use ("Fischer", "Fixed" or "Blitz")

Clock buttons (in Engine menu)
------------------------------

* First button shows the current selected engine name
* Second button goes down in the engines list
* Third button chooses the current selected engine
* Fourth button goes up in the engines list

It should be noted that not all engines work at the same speed. If you switch engines whilst in 'Analyze' or 'Kibitz' training modes
and (after the 'Ok' message) picoChess seems sluggish or not updating, probably a slow engine has been selected.

Clock buttons (in Book menu)
----------------------------

* First button shows the current selected book name
* Second button goes down in the books list
* Third button chooses the current selected book
* Fourth button goes up in the book list

It is possible to select any additional books you may have installed from the clock buttons, but the selection from the board is fixed.
Books must be in the Polyglot (.bin) format and must be named <letter><"-"><book name>, eg "a-nobook.bin" or "m-benoni.bin". Books appear in alphabetical order in the menu. 
Books "a" to "j" are used for setting from the board and contain the existing system books; they can be changed to make others available from the board.

Clock Buttons (in System menu)
------------------------------

* First button has no function
* Second button has no function
* Third button shutdown the machine. You have to press twice to activate this shutdown (for your safety). Pressing another button cancels it
* Fourth button reboots the machine. You have to press twice to activate this reboot (for your safety). Pressing another button cancels it

System shutdown
---------------

From the start position, replace the white king with the extra white queen; this will shut down the machine (takes a few seconds until the blue light turns off). You can also do it with only the two white queens on the board (on e1,d1).

PGN file support
----------------

All moves of the played game along with engine are stored.
Every game played with picochess is stored in the /opt/picochess folder as "games.pgn".
