Welcome to the PicoChess wiki.

## Introduction

The goal the this project is to create a dedicated chess computer based on tiny ARM computers, the Stockfish chess engine (http://www.stockfishchess.com/), the DGT eboard, and DGT XL Clock (http://www.dgtprojects.com/) via the dgtnix driver (http://dgtnix.sourceforge.net/).

Currently Rikomagic MK 802 II, O-droidx (http://store.cloudsto.com/rikomagic/rikomagic-mk802-ii-detail.html), and the Raspberry Pi (http://www.raspberrypi.org/) are supported.

One can also simply run the program on a desktop/laptop if you do not (yet) own any of the above devices.

![MK802 II](http://www.geeky-gadgets.com/wp-content/uploads/2012/08/Android-MK802-II.jpg)

## Download and installation for MK 802 II/Raspberry Pi

You will have to download and install the latest PicoChess image file from [the PicoChess website](http://www.picochess.org) and write it to a micro SD card.

You will need to unzip the image with [7zip](http://www.7-zip.org/) and write it to a suitable SD card using the UNIX tool [dd](http://manpages.ubuntu.com/manpages/lucid/man1/dd.1.html). Windows users should use [Win32DiskImager](https://launchpad.net/win32-image-writer). Do not try to drag and drop or otherwise copy over the image without using dd or Win32DiskImager – it won’t work.

#### Copying the image to an SD Card on Windows

1. Insert the SD card into your SD card reader and check what drive letter it was assigned. You can easily see the drive letter (for example G:) by looking in the left column of Windows Explorer. If the card is not new, you should format it; otherwise Win32DiskImager may hang.
1. Download the [Win32DiskImager utility](https://launchpad.net/win32-image-writer). The download links are on the right hand side of the page, you want the binary zip.
1. Extract the executable from the zip file. Note: the file after extraction should end in .img. Prior to extraction, it ends in .xz. 
1. Run the Win32DiskImager utility. You may need to run the utility as Administrator.
1. Select the picochess-MK802II-vx.x.img image file you extracted earlier
1. Select the drive letter of the SD card in the device box. Be careful to select the correct drive; if you get the wrong one you can destroy your computer's hard disk!
1. Click Write and wait for the write to complete.
1. Exit the imager and eject the SD card.

#### Copying the image to an SD Card on Linux

1. The following commands should be executed as root. It's popular to prefix the commands with 'sudo', but you can also become root apriori by using the command (may vary depending on distribution):
sudo su
1. Plug in your SD card and then use the following command to see which /dev/ node it's located on (be sure of this!):
fdisk -l
1. Unmount the disk (using /dev/sba as example, verify with step 2):
umount /dev/sba*
1. Use the 'dd' command to copy the image file to the entire disk:
dd if=picochess-MK802II-vx.x.img of=/dev/sba bs=16m
1. After the previous step is complete, execute "sudo sync" to ensure that the data is fully written before you eject.
1. Eject the card

#### Copying the image to an SD Card on Mac OS X

1. The following commands should be executed as root. It's popular to prefix the commands with 'sudo', but you can also become root apriori by using the command:
sudo su
1. Plug in your SD card and then use the following command to see which /dev/ node it's located on (be sure of this!):
diskutil list
1. Unmount the disk where "N" is the number of the disk taken from the above command:
    diskutil unmountDisk /dev/diskN
If the above command was successful, you will see:
Unmount of all volumes on diskN was successful
1. Use the 'dd' command to copy the image file to the entire disk:
    dd if=picochess-MK802II-vx.x.img of=/dev/rdiskN bs=16m
Note: rdiskN (raw disk) is far faster than diskN on Mac OS X.
Alternatively 
    pv picochess-MK802II-vx.x.img | dd of=/dev/rdiskN bs=100m
allows one to see progress during the write
1. After the previous step is complete, execute "sudo sync" to ensure that the data is fully written before you eject.
1. Eject the card

Misc Tip to do the reverse process - 

1. To burn in the reverse direction (from the sd card to an image) use
pv /dev/rdiskN|dd of=picochess-MK802II-v0.x.img bs=100m
1. xz -9e imagename.img to compress the image

## Starting PicoChess
### Playing vs the MK802II pocket computer
1. Insert the card in the MK802II
1. Connect it to a DGT eboard and XL clock, power on the clock and set it to mode '23'
1. Power on the MK802II.  After booting (takes 1-2 minutes) the clock will beep and display 'Picxxx', where xxx is the PicoChess version number.
1. Play !

### Playing vs the quad core ARM based O-droidx! - http://www.hardkernel.com/renewal_2011/products/prdt_info.php
1. Ensure that your hands are free of static electricity.
1. Use a 3.25" floppy disk as the base to place the O-droidx on. Alternatively, you can order a case from ebay or make your own. The O-droidx forums seem to have a wealth of information - http://odroid.foros-phpbb.com/
1. I recommend purchasing the wifi module and the power supply from hardkernel.com. 
1. If you are living in the US, a $2 simple adapter is needed to connect the hardkernel charger to the wall outlet. If you are living in Europe, you can skip this step! The wall charger sold by hardkernel fits well in the adapter. If there is no electronic store near you sporting the adapter, try http://www.amazon.com/BoxWave-European-American-Outlet-Adapter/dp/B0019DERAG/
1. You need a micro-hdmi to HDMI cable. You can get that from a nearby electronics store. Note that you need MICRO hdmi, mini-hdmi WONT work. If you cannot find this in a nearby electronics store, you can order one from the hardkernel site or from amazon at http://www.amazon.com/Cable-Matters-Premium-Motorola-portable/dp/B004C3HZCC/
1. Burn the appropriate image for the O-droidx. Currently, this image requires an 8GB SD card. Note: If you are burning the image in windows, you NEED a 16GB SD card. Javier has found out that windows for some reason cannot fit this image within 8GB. Until the issue is resolved, use a 16GB SD card for image burning in windows.
1. Connect the sd-card to the slot (you should hear a soft click when you settle in the card).
1. Connect the DGT board via USB.
1. Connect the power cable.
1. Press and hold the SW1 button on the odroid-x board for about 1 second, you should see the blue lights turning on. The bottom most blue light is a system heartbeat and should blink every few seconds.
1. After 20-30 seconds, you can play vs picochess.

#### Advanced extras for the O-droid

1. The username is linaro by default and the password is "picochess".
1. You can connect the computer to the network by using the top right menu on the desktop. This is useful if you want to test out developer versions of Picochess. Note that you can also plug in a network cable before booting.
1. To reduce the cpu speed and increase the NPS
  1. Go to a terminal
  1. Type in "sudo su"
  1. Type in the following. Note that it has to be done for each CPU. 1.6 Ghz is recommended.
  1.    echo 1600000 > /sys/bus/cpu/devices/cpu0/cpufreq/scaling_max_freq
  1.    echo 1600000 > /sys/bus/cpu/devices/cpu1/cpufreq/scaling_max_freq
  1.    echo 1600000 > /sys/bus/cpu/devices/cpu2/cpufreq/scaling_max_freq
  1.    echo 1600000 > /sys/bus/cpu/devices/cpu3/cpufreq/scaling_max_freq
1. To benchmark the o-droid
  1. Execute "sudo /etc/init.d/stockfish stop" to stop picochess (temporarily).
  1. Go to the code directory: 'cd /home/miniand/git/Stockfish/src'
  1. Execute "./stockfish"
  1. Type in "bench 4 128"
  1. You can also try "go infinite".
  1. You should be able to get close to 850K nodes per second! All hail the o-droidx!
  1. Type in "exit"
  1. Remember to execute "sudo /etc/init.d/stockfish start" to restart picochess.

### Playing vs a desktop/laptop PC
1. Either execute "git clone https://github.com/jromang/Stockfish" or download a release zip and extract file.
1. Go to the src folder.
1. Execute "make" to get help.
1. Run the appropriate make. For example, run "make profile-build ARCH=osx-x86-64" on a modern Mac.
1. Execute "sudo make install" to install the opening books to a central location that picochess will use during the game.
1. Connect your desktop/laptop to the DGT eboard and XL clock, power on the clock and set in in mode '23'
1. Execute "./stockfish dgt (usb serial device location)"
   1. On Linux, this is typically /dev/ttyUSB0
   1. On Mac OS X, look for /dev/cu.usbserial-* and fill in the appropriate entry. Note that one should use /dev/cu.usbserial-* instead of /dev/tty.usbserial-* because cu.usbserial does not require a software/hardware handshake like tty.usbserial-*. This is peculiar only to Mac OS X.

### Using a Serial DGT board

1. Need to get a USB serial to USB converter. A standard one works but one can use http://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_Chipi-X.pdf
1. You might need to provide separate power to the board.
1. Install the "Chipi-X" software on the linux image (usually not necesarry on most modern linux distros)
1. To convert serial to USB permanently, refer to http://www.youtube.com/watch?v=0r9XNL2aZXI (The price for the conversion kit is 115 € + VAT at the official DGT webstore.) 

### Using a Bluetooth DGT board or PCS Revelation II chessbot.
This now seems to work automatically and is plug and play! Simply insert a bluetooth dongle and boot up, the bluetooth connection will be made automatically. 
If not, refer to https://github.com/jromang/Stockfish/wiki/DGT-Bluetooth-eboard-configuration


## Troubleshooting

If the board isn't responding correctly, you may have a USB power source issue. You need at least a 5V/2A USB charger. A powered 5V/4A USB hub is even better.

If placing an extra queen on the board does not bring up menu options, check that the starting position is correctly set up (a piece not fully centralized on its square can cause this issue).

## Choosing skill level
Put the extra **black** queen on your DGT board to select skill level.  Putting it on square **A6** will select level 0 (easiest level), while **B6** selects level 1, **C6** selects level 2, etc.  If no skill level is selected, PicoChess uses level 20 (the highest level) by default.  Level 20 can also be selected by placing the extra black queen on square **E4**.

* Level 0  estimates about 1100 Elo ( Absolute beginner )
* Level 10 estimates about 1750 Elo ( Mediate clubplayer )
* Level 20 estimates about 2570 Elo  ( Advanced tournament player )

## Choosing opening books
Opening books are also selected with the extra **black** queen:

1. **A3** - No book
1. **B3** - Fun
1. **C3** - Anand
1. **D3** - Korchnoi
1. **E3** - Larsen
1. **F3** - Pro
1. **G3** - GM_2001 : GM games from 2001 to mid-September, 2012
1. **H3** - Varied. (**Default**)
1. **H4** - GM_1950 (> 2500 ELO GM games from 1950 till mid-Sept, 2012)
1. **G4** - Performance
1. **F4** - Stockfish optimized book v 2.11 by Salvo Spitaleri

## Setting up time controls
Time controls are set with the extra **white** queen. Remove the extra black queen if it is still on the board.

1. **A6** - 1 second per move
1. **B6** - 3 seconds per move
1. **C6** - 5 seconds per move
1. **D6** - 10 seconds per move
1. **E6** - 15 seconds per move
1. **F6** - 30 seconds per move
1. **G6** - 60 seconds per move
1. **H6** - 120 seconds per move

## Blitz Levels
Blitz time controls are set with the extra **white** queen. Remove the extra black queen if it is still on the board.

1.	**A4** - 1 minute game
1.	**B4** - 3 minute game
1.	**C4** - 5 minute game
1.	**D4** - 10 minute game
1.	**E4** - 15 minute game
1.	**F4** - 30 minute game
1.	**G4** - 60 minute game (1 hour)
1.	**H4** - 90 minute game (1 hour and 30 minutes)

## Fischer Increment Blitz Levels
These are set with the extra **white** queen. Remove the extra black queen if it is still on the board.

1. **A3** - 3 minute game with 2 second Fischer increment
2. **B3** - 4 minute game with 2 second Fischer increment
3. **C3** - 5 minute game with 3 second Fischer increment
4. **D3** - 5 minute game with 5 second Fischer increment
1. **E3** - 15 minute game with 5 second Fischer increment
1. **F3** - 25 minute game with 5 second Fischer increment
1. **G3** - 90 minute game with 30 second Fischer increment

##PicoChess with White
To force PicoChess to play with White just take the black king off the board and put it back. If you want to play with White again just take the white king off the board and put it back. Note: **You have to be in the starting position!**

## System shutdown
From the start position, replace the white king with the extra white queen; this will shut down the MK802II (takes a few seconds until the blue light turns off). You can also do it with only the two white queens on the board (on e1,d1).

## Book/Training Modes
When using these modes, please be patient and dont rush moves. Allow a few seconds for the book moves to appear. If you see any bug when rushing moves, let us know on the mailing list.

1. Book mode is enabled by putting the **white** queen on the **A5** square. Book mode will return the top 3 book moves in descending order (by score) to you when it is your turn. Descending order means that the last move on the clock is the best book move. This is useful when you want to play against the computer but are not confident in your opening preparation.

2. Analysis mode (enabled by **white** queen on **B5**) is Book mode + the computer does not play. After you move pieces, you can see the book moves or position score if out of book followed by the best move suggestion. You can play over games and see the computer evaluation. The display keeps refreshing every 2 seconds with the depth (e.g. d17), the score in centipawns (e.g. 17) OR a mate in x (e.g. m 2), followed by the recommended move. Note that the score is from the perspective of the side to move. A n100 score means the side to move is worse by about a pawn, whereas a 100 score means that the side to move is ahead by a pawn.

3. Training mode (enabled by **white** queen on **C5**) is Analysis mode but without displaying the best move. It only continuously displays the depth and score. This is useful when you want to train yourself on the values of different moves.

4. Game mode is the regular mode, but if you used one of the above modes, you can return back to game mode by putting a **white** queen on **D5**.

Todo: In a later version, the score will always be from white's perspective to be more consistent.

## Position setup
Setting up a custom position is now possible.

1. To set up a position with white to move, place both **white** queens on **A1** and **H1** and remove ALL other pieces from the board.
1. The "Setup" message should flash on the DGT clock.
1. Now setup a custom position.
1. After you are done setting up the position, remove the **white** king and place it back (can also be the black king) if you want to play the position against the computer with you having while to move.
1. If instead you want to analyze the position, remove any other piece excepting a king and place it back on the same square. 
1. You should get a "New Game" message.
1. Now make a move for white, and the computer will either play against you or analyze depending on what you chose.
1. To have a position with black to move, repeat the above procedure with **black** queens on **A8** and **H8**.
1. If you want white to play but have the board reversed, place the queens on the squares and remove and replace a queen once after to get the "Setup" message.

## Clock button support (supported from version 0.17 onwards)
1. The first clock button shows the last move.
1. The second clock button shows an evaluation followed by a move hint.
1. The third clock button toggles between top level menus, currently "Setup", "Level", "Book", "Time", "None", "Engine", and "System". The last two menus dont provide any functionality yet.
1. The fourth clock button will switch sides and the computer will make your move.
1. The fifth clock button switches game modes.

1. To move between top level menus, use the home button. If you want to change a level for example, use the home button until you see "Level". Then hit the 2nd and/or 4th clock buttons to toggle levels. Then, use the last clock button to select an option. With level, you can use the 4th button to increase to level 10 and then hit the last button to select level 10.
1. On the setup menu, the options are white, black, reverse board, and scan position. This means white to move, black to move, reverse board orientation, and scan the board position.
1. The chatty game mode will return the evaluation every two seconds, while playing a game.
1. Use the home button to switch to the "None" to use the clock buttons during a game.

## PGN file support (from version 0.17 onwards)
1. All moves of the played game along with engine evaluations and the principal variation are stored. 
1. Every game played with picochess is stored in the source tree folder as "game.pgn". This is overwritten when you restart pico chess.
1. If a position is undone, another game will be created within game.pgn.


## For Advanced Users
### Wireless enabling the Rikomagic

1. Once the micro sd card is entered on the device, connect it to an HDMI display. Attach a USB mouse and keyboard, a one time connect is sufficient.
1. Log on the Lubuntu session with username "miniand" and password "picochess".
1. Go to the bottom right of the screen and right click on the wireless icon.
1. Configure your SSID and key.
1. Once you see a successful connection, you are done!

### Getting Stockfish output on the rikomagic
To see the stockfish output, ssh to the box (or start a terminal on the HDMI display itself if you don't have wireless). Execute:

1. For windows users, download putty from http://the.earth.li/~sgtatham/putty/latest/x86/putty.exe
1. Double click that file
1. Get the ip address of your device. For the rikomagic and the o-droidx, use the hdmi connection, start a terminal (left click on top left menu icon and find the terminal application), and type in "ifconfig". You should see the ip address. Typically the ip will be the same for a long time (dhcp renewal can change the ip address).
1. Type in the ip address of your rikomagic or O-droidx in the host name
1. Click connect
1. For username, use "miniand" for rikomagic, and "linaro" for o-droidx. The password is "picochess" for both devices.
1. You should now see a terminal. Type in the below commands to get stockfish output.
1. "sudo su" (to become root)
1. "screen -ls" (sample output below)

There is a screen on:  
	513.sf	(06/10/12 15:48:52)	(Detached)  
1 Socket in /var/run/screen/S-root.  
You want to connect to this "screen". "screen" is nothing more than a fancy name for a named "terminal" session. In this example, 513.sf is the correct screen for me. Use the right screen value for you in the next command.
1. "screen -D -R -S 513.sf" (note that it must exactly match the output of screen -ls).
To detach from this screen, you need to enter "Ctrl-a d". This is cryptic unfriendly notation for detach. If you execute "Ctrl-C" instead, picochess will be stopped!

Now you can see the output of picochess and monitor it. To restart pico chess in case you accidentally stopped it, issue:
"sudo /etc/init.d/stockfish start" or even "sudo /etc/init.d/stockfish stop" followed by "sudo /etc/init.d/stockfish start"

### Build a custom image on the rikomagic

1. Install lubuntu ; described here :
(http://rikomagic.co.uk/forum/viewtopic.php?f=2&t=90)
1. Once it is installed, login and configure your wireless network
(some clicks in the graphical user interface)
1. Open a termial, and install necessary tools : 'sudo apt-get install
git build-essential'
1. Always in this terminal, create the git directory : 'mkdir git && cd git'
1. Clone the picochess repository : 'git clone
git://github.com/jromang/Stockfish.git'
1. Go to the source directory : 'cd Stockfish/src'
1. Build the engine : 'make profile-build ARCH=general-32'
1. Change permissions : 'sudo chown root stockfish' and 'sudo chmod
4755 stockfish'
1. Create the startup script in the file /etc/init.d/stockfish  (Use nano to copy / paste this file
https://github.com/jromang/Stockfish/blob/dgt/stockfish.init)
1. Launch at boot time : 'sudo update-rc.d stockfish defaults'

### Updating Picochess on the rikomagic/o-droidx

ONE time setup on the O-droidx:
You have to do the following steps only ONLY ONCE on the o-droidx. This links the books folder.

1. Execute 'sudo su'
1. 'mkdir -p /home/miniand/git/Stockfish'
1. 'ln -s /home/linaro/git/Stockfish/books/ /home/miniand/git/Stockfish'
1. Execute 'exit'

Steps on both rikomagic and the O-droidx:

1. Go to the code directory: 'cd /home/miniand/git/Stockfish' or 'cd /home/linaro/git/Stockfish' on the odroid-x.
1. Execute 'git pull'
1. Go to the source directory: 'cd src'
1. Clean the build just in case: 'make clean'
1. Build the engine : 'make profile-build ARCH=armv7'
1. Change permissions : 'sudo chown root stockfish' and 'sudo chmod
4755 stockfish'
1. Restart stockfish using '/etc/init.d/stockfish stop' followed by '/etc/init.d/stockfish start'

### Building a new image

1. Shutdown the device or simply remove the power from the o-droidx/rikomagic/raspberry pi.
1. Connect SD card to your desktop.
1. Start win32diskimager (if on windows), select the SD card and backup the card to an image file.
1. Use 7zip to compress this image as much as possible.
1. Upload image to server (if you want to volunteer to build images, email us and we can provide a place to upload images).

### Network enabling retrieval of game.pgn

1. One time setup on any device - "sudo apt-get install python-tornado"
1. Start or via /etc/init.d go to /home/miniand/git/Stockfish and start "python app.py"
1. Then executing http://<ip>:8080/game.pgn will retrieve game.pgn

## Pycochess 0.21

A new version of Picochess supporting the Raspberry Piface is now in Beta.

### To run

1. Image now available.
1. Simply download an extract to card and run as usual.
1. The back rocker switch changes modes, while the front buttons enable disable options within a mode.
1. The back rocker switch changes modes - Engine, Database, System, Setup Position, Play Menu
1. In the engine menu, the first button allows changing level, the second buttons changes opening books, the third button changes time controls, the fourth button toggles tablebases on and off. (Off by default). The last button displays the stockfish build version.
1. In the system menu, the first button gets the IP, the third button scans for software updates (if you are connected to the internet), the fifth button shuts down the Pi.
1. In the setup position menu, the first button toggles between white to play and black to play (default is white to play), the second button toggles between computer plays black and white (default is comp plays black), the third button reverses board orientation, the fifth button scans the position on the board.
1. In the Play menu, the first button displays the last menu, the second button displays book moves or a hint if the position is out of book, the third button shows the current evaluation, the fourth button turns on silent mode, the fifth button toggles between game and analysis mode (default is game mode). Silent mode can hide computer analysis in analysis mode.
1. In the alternate input mode menu, moves can be keyed using from and destination squares. Special commands include "a1a1" for taking back a move, "b1b1" for starting a new game, "e8e8" for letting the computer play white, "e1e1" for letting the computer play black (default).

## Bluetooth via Pycochess (courtesy of Uwe Lauer)
Thanks for Eric Singer for making the script.

1. log in via ssh or open a terminal if you have a monitor connected: ```sudo -s```
1. update package information: ```sudo apt-get update```
1. install the BT-package: ```apt-get install bluez python-gobject```
1. look for your BT-dongle: ```hcitool dev```
  (you will see something like this: Devices: hci0 12:34:56:78:91:01)
1. look fpr BT-devices: ```hcitool scan```
  (You will see something like this:
  Scanning ...
  11:22:33:44:55:66 "names of the devces"
  Now you have the MAC-address of your board)
1. bind the board: ```bluez-simple-agent hci0 11:22:33:44:55:66```
  (take the MAC-address of your board, not 11:22:33:44:55:66)
  you will see somethings like this:
  Enter PIN Code: Release
  New device (...)
1. enter the following code: ```0000```
1. connect the board: ```bluez-test-input connect 11:22:33:44:55:66```
  (remember to take the MAC-Address of your board, not 11:22:33.....)
1. you have to trust the new device, otherwise after a reboot, all is gone: ```bluez-test-device trusted 11:22:33:44:55:66 yes```
  (remember the hint with the MAC-address)
1. reboot: ```sudo su reboot```

