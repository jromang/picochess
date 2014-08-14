Usage
=====

Choosing skill level
--------------------
Put the extra black queen on your DGT board to select skill level. Putting it on square A6 will select level 0 (easiest), while B6 selects level 1, C6 selects level 2, etc. If no skill level is selected, PicoChess uses level 20 (the highest level) by default. Level 20 can also be selected by placing the extra black queen on square E4.

* Level  0 estimates about 1100 Elo (Absolute beginner)
* Level 10 estimates about 1750 Elo (Mediate club player )
* Level 20 estimates about 2570 Elo (Advanced tournament player)

Choosing opening books
----------------------

Opening books are also selected with the extra black queen:

* A3 - No book
* B3 - Fun
* C3 - Anand
* D3 - Korchnoi
* E3 - Larsen
* F3 - Pro
* G3 - GM_2001 : GM games from 2001 to mid-September, 2012
* H3 - Varied. (Default)
* H4 - GM_1950 (> 2500 ELO GM games from 1950 till mid-Sept, 2012)
* G4 - Performance
* F4 - Stockfish optimized book v 2.11 by Salvo Spitaleri

Setting up time controls
------------------------

Time controls are set with the extra white queen. Remove the extra black queen if it is still on the board.

* A6 - 1 second per move
* B6 - 3 seconds per move
* C6 - 5 seconds per move
* D6 - 10 seconds per move
* E6 - 15 seconds per move
* F6 - 30 seconds per move
* G6 - 60 seconds per move
* H6 - 120 seconds per move

Blitz Levels
------------

Blitz time controls are set with the extra white queen. Remove the extra black queen if it is still on the board.

* A4 - 1 minute game
* B4 - 3 minute game
* C4 - 5 minute game
* D4 - 10 minute game
* E4 - 15 minute game
* F4 - 30 minute game
* G4 - 60 minute game (1 hour)
* H4 - 90 minute game (1 hour and 30 minutes)

Fischer Increment Blitz Levels
------------------------------

These are set with the extra white queen. Remove the extra black queen if it is still on the board.

* A3 - 3 minute game with 2 second Fischer increment
* B3 - 4 minute game with 2 second Fischer increment
* C3 - 5 minute game with 3 second Fischer increment
* D3 - 5 minute game with 5 second Fischer increment
* E3 - 15 minute game with 5 second Fischer increment
* F3 - 25 minute game with 5 second Fischer increment
* G3 - 90 minute game with 30 second Fischer increment

PicoChess with White
--------------------

To force PicoChess to play with White just take the black king off the board and put it back. If you want to play with White again just take the white king off the board and put it back. Note: You have to be in the starting position!

System shutdown
---------------

From the start position, replace the white king with the extra white queen; this will shut down the machine (takes a few seconds until the blue light turns off). You can also do it with only the two white queens on the board (on e1,d1).
Book/Training Modes

When using these modes, please be patient and dont rush moves. Allow a few seconds for the book moves to appear. If you see any bug when rushing moves, let us know on the mailing list.

    Book mode is enabled by putting the white queen on the A5 square. Book mode will return the top 3 book moves in descending order (by score) to you when it is your turn. Descending order means that the last move on the clock is the best book move. This is useful when you want to play against the computer but are not confident in your opening preparation.

    Analysis mode (enabled by white queen on B5) is Book mode + the computer does not play. After you move pieces, you can see the book moves or position score if out of book followed by the best move suggestion. You can play over games and see the computer evaluation. The display keeps refreshing every 2 seconds with the depth (e.g. d17), the score in centipawns (e.g. 17) OR a mate in x (e.g. m 2), followed by the recommended move. Note that the score is from the perspective of the side to move. A n100 score means the side to move is worse by about a pawn, whereas a 100 score means that the side to move is ahead by a pawn.

    Training mode (enabled by white queen on C5) is Analysis mode but without displaying the best move. It only continuously displays the depth and score. This is useful when you want to train yourself on the values of different moves.

    Game mode is the regular mode, but if you used one of the above modes, you can return back to game mode by putting a white queen on D5.

Todo: In a later version, the score will always be from white's perspective to be more consistent.

Position setup
--------------

Setting up a custom position is now possible.

    To set up a position with white to move, place both white queens on A1 and H1 and remove ALL other pieces from the board.
    The "Setup" message should flash on the DGT clock.
    Now setup a custom position.
    After you are done setting up the position, remove the white king and place it back (can also be the black king) if you want to play the position against the computer with you having while to move.
    If instead you want to analyze the position, remove any other piece excepting a king and place it back on the same square.
    You should get a "New Game" message.
    Now make a move for white, and the computer will either play against you or analyze depending on what you chose.
    To have a position with black to move, repeat the above procedure with black queens on A8 and H8.
    If you want white to play but have the board reversed, place the queens on the squares and remove and replace a queen once after to get the "Setup" message.

Clock button support (supported from version 0.17 onwards)

    The first clock button shows the last move.
    The second clock button shows an evaluation followed by a move hint.
    The third clock button toggles between top level menus, currently "Setup", "Level", "Book", "Time", "None", "Engine", and "System". The last two menus dont provide any functionality yet.
    The fourth clock button will switch sides and the computer will make your move.

    The fifth clock button switches game modes.

    To move between top level menus, use the home button. If you want to change a level for example, use the home button until you see "Level". Then hit the 2nd and/or 4th clock buttons to toggle levels. Then, use the last clock button to select an option. With level, you can use the 4th button to increase to level 10 and then hit the last button to select level 10.
    On the setup menu, the options are white, black, reverse board, and scan position. This means white to move, black to move, reverse board orientation, and scan the board position.
    The chatty game mode will return the evaluation every two seconds, while playing a game.
    Use the home button to switch to the "None" to use the clock buttons during a game.

PGN file support (from version 0.17 onwards)

    All moves of the played game along with engine evaluations and the principal variation are stored.
    Every game played with picochess is stored in the source tree folder as "game.pgn". This is overwritten when you restart pico chess.
    If a position is undone, another game will be created within game.pgn.
