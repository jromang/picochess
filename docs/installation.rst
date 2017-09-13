Installation
============

Easy method : using image files
-------------------------------

This is the easiest installation method, supported on the `Raspberry Pi <http://www.raspberrypi.org>`_.
Many other ARM boards can run picochess (like the powerful `Odroid-XU4 <http://www.hardkernel.com/main/products/prdt_info.php?g_code=G143452239825>`_),
but you will need to do a `manual-install-label`_.

You will have to download and install the latest PicoChess image file from the `PicoChess downloads <http://picochess.com/picochess-images>`_ and write it
to an SD card or to a micro SD card.

You will need to unzip the image with `7zip <http://www.7-zip.org/>`_ and write it to a suitable SD card
using the UNIX tool `dd <http://manpages.ubuntu.com/manpages/lucid/man1/dd.1.html>`_.
Windows users should use `Win32DiskImager <https://launchpad.net/win32-image-writer>`_. Mac OS X users should use `ApplePi-Baker <http://www.tweaking4all.com/hardware/raspberry-pi/macosx-apple-pi-baker/>`_. Do not try to drag and drop or otherwise copy over the image
without using dd or Win32DiskImager or ApplePi-Baker – it won’t work.

After booting from the new image, you might want to tinker with the machine (i.e. set defaults in the picochess.ini file or install alternative engines). This is done by connecting via ssh:

1. On Raspberry Pi, the hostname on local network is 'raspberrypi.local', username:pi, pass:picochess.

2. On Odroid, the hostname on local network is 'odroid.local', username:odroid, pass:odroid.


Copying the image to an SD Card on Windows
------------------------------------------

1. Insert the SD card into your SD card reader and check what drive letter it was assigned. You can easily see the drive letter (for example G:) by looking in the left column of Windows Explorer. If the card is not new, you should format it; otherwise Win32DiskImager may hang.

2. Download the `Win32DiskImager utility <http://sourceforge.net/projects/win32diskimager/>`_.

3. Extract the Win32DiskImager executable from the zip file. Note: the PicoChess file after extraction should end in .img. Prior to extraction, it ends in .xz.

4. Run the Win32DiskImager utility. You may need to run the utility as Administrator.

5. Select the Picochess-RaspberryPix-vx.xx.img image file you extracted earlier.

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

6. Eject the card.

Copying the image to an SD Card on Mac OS X
-------------------------------------------

1. Insert the SD card into your SD card reader.

2. Download the `ApplePi-Baker utility <http://www.tweaking4all.com/hardware/raspberry-pi/macosx-apple-pi-baker/>`_.

3. Start the ApplePi-Baker utility. You will be asked for your administrator password.

4. Under "Pi-Crust", select the SD card.

5. Under "Pi-Ingredients", select the Picochess-RaspberryPix-vx.xx.img file you extracted earlier (press the "..." button to locate the image file).

6. Press "Restore Backup" to start writing the PicoChess image file to the SD card. Wait for the write to complete.

7. Exit ApplePi-Baker and eject the SD-card.

Alternatively, if you prefer working with Terminal commands, you can follow the following procedure.

1. The following commands should be executed as root. It's popular to prefix the commands with 'sudo', but you can also become root apriori by using the command: sudo su

2. Plug in your SD card and then use the following command to see which /dev/ node it's located on (be sure of this!): diskutil list

3. Unmount the disk where "N" is the number of the disk taken from the above command: diskutil unmountDisk /dev/diskN If the above command was successful, you will see: Unmount of all volumes on diskN was successful

4. Use the 'dd' command to copy the image file to the entire disk: dd if=picochess-MK802II-vx.x.img of=/dev/rdiskN bs=16m Note: rdiskN (raw disk) is far faster than diskN on Mac OS X. Alternatively pv picochess-MK802II-vx.x.img | dd of=/dev/rdiskN bs=100m allows one to see progress during the write.

5. After the previous step is complete, execute "sudo sync" to ensure that the data is fully written before you eject.

6. Eject the card.


.. _manual-install-label:

Manual installation
-------------------

1. **Prerequisites**

  PicoChess is mainly targetted for small devices like the `Raspberry Pi <http://www.raspberrypi.org>`_,
  however it also runs on a desktop computer (Linux, Mac OS X, Windows). You will need to install this first:

  * `Python 3.4 or newer (also comes with pip) <https://www.python.org/downloads/>`_
    (on Mac OS X, ``brew install python3``)

  * `git <http://git-scm.com/>`_ (``sudo apt-get install git``, git executable has to be in the system PATH)

  * zeroconf (``sudo apt-get install avahi-daemon avahi-discover libnss-mdns``, included on Mac OS X)

  * espeak and festival (``sudo apt-get install espeak festival``) to enable voice for versions < 0.79

  * vorbis-tools (``sudo apt-get install vorbis-tools``) to enable voice for versions >= 0.79

  * sox (``sudo apt-get install sox``) to enable voice speed for versions >= 0.88

  * develop libraries (``sudo apt-get install python3-dev libffi-dev libssl-dev``)

2. **Get a copy of the source code**

  ``cd /opt``

  ``sudo git clone --branch master https://github.com/jromang/picochess.git``

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

  To install the dependencies, you need to use pip3. If you are using Raspbian Jessie, your pip3 installation is
  probably outdated, resulting in IncompleteRead errors. You can update pip3 as follows:
  
  ``cd``
  
  ``curl -O https://bootstrap.pypa.io/get-pip.py``
  
  ``sudo python3 get-pip.py``
  
  ``rm get-pip.py``
  
  Once you have an up-to-date version of pip3 installed, you can continue to install the PicoChess dependencies:

  ``cd /opt/picochess``

  ``sudo pip3 install --upgrade -r requirements.txt``

5. **Build config files**

  Initialize the config files:

  ``sudo python3 ./build/engines.py``
  ``sudo python3 ./build/books.py``
  ``sudo python3 ./build/voices.py``

6. **Copy the dgtpi services into the correct place (ONLY needed if you have a DGTPi chess computer)**

  ``cd /opt/picochess/etc``

  ``sudo cp dgtpi.service /etc/systemd/system``

  ``sudo chmod a+x /etc/systemd/system/dgtpi.service``

  ``sudo systemctl enable dgtpi``

  ``sudo cp dgtpistandby.service /etc/systemd/system``

  ``sudo cp dgtpistandby.target /etc/systemd/system``

  ``sudo chmod a+x /etc/systemd/system/dgtpistandby.service``

  ``sudo systemctl enable dgtpistandby``

7. **Copy the picochess services into the correct place (ONLY needed if you want picochess to startup automatically)**

  ``cd /opt/picochess/etc``

  ``sudo cp picochess.service /etc/systemd/system``

  ``sudo chmod a+x /etc/systemd/system/picochess.service``

  ``sudo systemctl enable picochess``

  ``sudo cp hciuart.service /lib/systemd/system``

  ``sudo reboot``

8. **Run PicoChess: automatically or from the command line**

  If installed correctly, PicoChess will start automatically at boot (as a service see 6+7).
  You can also start PicoChess from the command line in standard mode or in console mode (use "console" flag for this).

  PicoChess has a lot of options. Type ``sudo python3 /opt/picochess/picochess.py -h`` for a list.

Make picochess sound better
---------------------------
If your output from the RPi audio jack socket is quite low and buzzes a lot add the following line to /boot/config.txt
``audio_pwm_mode=2``
Afterwards type ``sudo reboot``.

To make the volume instantly louder (it will also be kept after the reboot) type ``amixer sset PCM,0 90%``
Obviously the percentage can be set to any number, but 100% is too loud.

Bluetooth Connection
--------------------

Bluetooth connection should work out of the box. If it does not, then you can try the following troubleshooting steps:

1. Install Bluetooth utilities and Bluetooth Manager (in Raspbian Wheezy: sudo apt-get install bluez-utils blueman).

2. Connect the Bluetooth dongle and restart the Pi.

3. Start the GUI:

   startx

4. Go to Preferences/Bluetooth Manager.

5. Click Search to find your device, right click and connect.

6. For Revelation II use the prepared pin 1234, for DGT bluetooth eboard 0000.

7. Then click to connect as a serial device.

8. Back on the Bluetooth Manager right click on the device again and click trusted. Job done!

9. Open Terminal app and shut down the machine:

   sudo shutdown -h -P now

10. Restart the Pi without the keyboard and monitor and tada! the connection should work.

For more information check this `forum post <https://groups.google.com/forum/#!topic/picochess/7LSBZ6Qha64>`_.

Initial Settings
----------------

At start PicoChess looks at the file

/opt/picochess/picochess.ini

... and sets itself up accordingly. Here is a list of some available options:

* disable-revelation-leds = true
* log-level = debug
* log-file = /opt/picochess/picochess.log
* user-voice = en:al
* computer-voice = en:christina
* disable-confirm-message

To set a particular setting, simply include the appropriate line in the picochess.ini file.
For example, to the disable default confirmation message, include this line in picochess.ini:

disable-confirm-message

To remove a setting, delete the appropriate line or comment it out using the hash character (#) or set the option to false.
For example, to turn OFF the LED's on the Revelation II chessbot, this line will do:

disable-revelation-leds = true

UCI engine options can be set in the engines.uci configuration file which you will find in the
/opt/picochess/engines/<your_plattform> folder. To set the option, use the uci-option flag.

An example .ini file can be found at /opt/picochess/picochess.ini.example.
Uncomment the appropriate options and rename the file to picochess.ini.

Please keep in mind that your picochess.ini file must suit the version of picochess.
Old picochess.ini versions might not work with newer versions of picochess (picochess.ini.example is always valid).
If you update picochess by hand or by providing the "enable-update" flag please take a look for changed settings and
update picochess.ini accordingly.
