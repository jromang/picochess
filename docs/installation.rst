Installation
============

Easy method : using image files
-------------------------------

This is the easiest installation method, supported on the `Raspberry Pi <http://www.raspberrypi.org>`_.
Many other ARM boards can run picochess (like the powefull `Odroix-U3 <http://hardkernel.com/main/products/prdt_info.php?g_code=G138745696275>`_)
but you will need to do a :ref:`manual-install-label`.

You will have to download and install the latest PicoChess image file from the `PicoChess downloads <http://dl.picochess.org>`_ and write it
to a SD or micro SD card.

You will need to unzip the image with `7zip <http://www.7-zip.org/>`_ and write it to a suitable SD card
using the UNIX tool `dd <http://manpages.ubuntu.com/manpages/lucid/man1/dd.1.html>`_.
Windows users should use `Win32DiskImager <https://launchpad.net/win32-image-writer>`_. Do not try to drag and drop or otherwise copy over the image
without using dd or Win32DiskImager – it won’t work.

After booting from the new image, you might want to tinker with the machine (i.e. set defaults in picochess.ini file or install alternative engines). This is done by connecting via ssh:

1. On Raspberry Pi, the hostname on local network is 'raspberrypi.local', username:pi, pass:picochess.

2. On Odroid, the hostname on local network is 'odroid.local', username:odroid, pass:odroid.


Copying the image to an SD Card on Windows
------------------------------------------

1. Insert the SD card into your SD card reader and check what drive letter it was assigned. You can easily see the drive letter (for example G:) by looking in the left column of Windows Explorer. If the card is not new, you should format it; otherwise Win32DiskImager may hang.

2. Download the `Win32DiskImager utility <https://launchpad.net/win32-image-writer>`_. The download links are on the right hand side of the page, you want the binary zip.

3. Extract the executable from the zip file. Note: the file after extraction should end in .img. Prior to extraction, it ends in .xz.

4. Run the Win32DiskImager utility. You may need to run the utility as Administrator.

5. Select the picochess-RaspberryPi-vx.x.img image file you extracted earlier

6. Select the drive letter of the SD card in the device box. Be careful to select the correct drive; if you get the wrong one you can destroy your computer's hard disk!

7. Click Write and wait for the write to complete.

8. Exit the imager and eject the SD card.

Copying the image to an SD Card on Linux
----------------------------------------

1. The following commands should be executed as root. It's popular to prefix the commands with 'sudo', but you can also become root apriori by using the command (may vary depending on distribution): sudo su

2. Plug in your SD card and then use the following command to see which /dev/ node it's located on (be sure of this!): fdisk -l

3. Unmount the disk (using /dev/sba as example, verify with step 2): umount /dev/sba*

4. Use the 'dd' command to copy the image file to the entire disk: dd if=picochess-MK802II-vx.x.img of=/dev/sba bs=16M

5. After the previous step is complete, execute "sudo sync" to ensure that the data is fully written before you eject.

6. Eject the card

Copying the image to an SD Card on Mac OS X
-------------------------------------------

1. The following commands should be executed as root. It's popular to prefix the commands with 'sudo', but you can also become root apriori by using the command: sudo su

2. Plug in your SD card and then use the following command to see which /dev/ node it's located on (be sure of this!): diskutil list

3. Unmount the disk where "N" is the number of the disk taken from the above command: diskutil unmountDisk /dev/diskN If the above command was successful, you will see: Unmount of all volumes on diskN was successful

4. Use the 'dd' command to copy the image file to the entire disk: dd if=picochess-MK802II-vx.x.img of=/dev/rdiskN bs=16m Note: rdiskN (raw disk) is far faster than diskN on Mac OS X. Alternatively pv picochess-MK802II-vx.x.img | dd of=/dev/rdiskN bs=100m allows one to see progress during the write

5. After the previous step is complete, execute "sudo sync" to ensure that the data is fully written before you eject.

6. Eject the card


.. todo:: Alternative and easier method : http://www.tweaking4all.com/hardware/raspberry-pi/macosx-apple-pi-baker/


.. _manual-install-label:

Manual installation
-------------------

1. **Prerequisites**

  PicoChess is mainly targetted for small devices like the
  `Raspberry Pi <http://www.raspberrypi.org>`_, however it also
  runs on a desktop computer (Linux, OSX, Windows). You will need to install this
  first:

  * `Python 3.4 or newer (also comes with pip) <https://www.python.org/downloads/>`_
    (on mac OS X, ``brew install python3``)

  * `git <http://git-scm.com/>`_ (use git executable has to be in the system PATH)

  * An UCI chess engine; `Stockfish <http://stockfishchess.org/>`_ is probably
    the best choice !

  * `zeroconf` (``apt-get install avahi-daemon avahi-discover libnss-mdns``, included on mac OS X)

2. **Get a copy of the source code**

  ``git clone --branch stable https://github.com/jromang/picochess.git``

  ``cd picochess``

3. **Recommended step for developers: Install virtualenv**

  Virtualenv provides clean and isolated development environments for your
  Python projects (``pip3 install virtualenv`` or
  ``apt-get install virtualenv``).

  Initialize a new environment: ``virtualenv -p python3 venv``

  Activate the environment: ``source venv/bin/activate``

  No need to use sudo to install Python packages now.

  See `The Hitchhiker's Guide to Python <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_
  for more information about virtual environments.

4. **Install dependencies**

  ``pip install --upgrade -r requirements.txt``

5. **Run picochess from command line**

  Picochess has a lot of options. Type ``python3 picochess.py -h`` for a list.

Bluetooth Connection
--------------------

1. Install bluetooth utilities. (apt-get install bluez-utils)

2. Connect bluetooth dongle and restart the Pi.

3. Start the GUI:

   startx

4. Go to Preferences/Bluetooth Manager.

5. Click search to find your device, right click and connect.

6. For Revelation II use the prepared pin 1234, for DGT bluetooth eboard 0000.

7. Then click to connect as a serial device.

8. Back on the bluetooth manager right click on the device again and click trusted. Job done!

9. Open Terminal app and shut down the machine:

   sudo shutdown -h now

10. Restart the pi without the keyboard and monitor and tada! the connection should work.

For more information check this `forum post <https://groups.google.com/forum/#!topic/picochess/7LSBZ6Qha64>`_.

Initial Settings
----------------

At start Picochess looks at the file

/opt/picochess/picochess.ini

... and sets itself up accordingly. Here is a list of some available options:

* enable-dgt-board-leds = true
* uci-option = Beginner Mode=true
* log-level = debug
* log-file = /opt/picochess/picochess.log
* uci-option = Threads = 4
* user-voice = en:Elsie
* computer-voice = en:Marvin
* disable-dgt-clock-beep

To set a particular setting, simply include appropriate line in the picochess.ini file.
For example, to disable default beep on a move, include this line in picochess.ini:

disable-dgt-clock-beep

To remove a setting, delete the appropriate line or comment it out using the Hash character (#) or set the option to false.
For example to turn OFF the LED's on the Revelation II chessbot, this line will do:

enable-dgt-board-leds = false

UCI engine options can be set using uci-option. For example, when using jromang's modified
`Stockfish Human Player engine <https://github.com/jromang/Stockfish/tree/human_player>`_, the line

uci-option = Beginner Mode=true

will dumb Stockfish down enough for play against children and total beginners to give
them a chance of beating the machine. If you are using our image files, you will probably find
stockfish_human engine already waiting for your kids in the /opt/picochess/engines folder.

An example .ini file can be found at /opt/picochess/picochess.ini.example.
Uncomment appropriate options and rename the file to picochess.ini.

