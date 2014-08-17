Installation
============

Easy method : using image files
-------------------------------

This is the easiest installation method, supported on the `Raspberry Pi <http://www.raspberrypi.org>`_.
Many other ARM boards can run picochess (like the powefull `Odroix-U3 <http://hardkernel.com/main/products/prdt_info.php?g_code=G138745696275>`_)
but you will need to do a :ref:`manual-install-label`.

You will have to download and install the latest PicoChess image file from the `PicoChess downloads <dl.picochess.org>`_ and write it
to a SD or micro SD card.

You will need to unzip the image with `7zip <http://www.7-zip.org/>`_ and write it to a suitable SD card
using the UNIX tool `dd <http://manpages.ubuntu.com/manpages/lucid/man1/dd.1.html>`_.
Windows users should use `Win32DiskImager <https://launchpad.net/win32-image-writer>`_. Do not try to drag and drop or otherwise copy over the image
without using dd or Win32DiskImager – it won’t work.

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

4. Use the 'dd' command to copy the image file to the entire disk: dd if=picochess-MK802II-vx.x.img of=/dev/sba bs=16m

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

1. Requirements

PicoChess is mainly targetted for small devices like the `Raspberry Pi <http://www.raspberrypi.org>`_, however is also
runs on a desktop computer (Linux, OSX, Windows). You will need to install this first :
  
* `Python 3 <https://www.python.org/downloads/>`_ (on mac OS X, brew install python3)
  
* `pycrypto <https://pypi.python.org/pypi/pycrypto>`_ (on mac OS X, brew install pycrypto)

* `tornado <http://www.tornadoweb.org>`_

* `flask <https://github.com/mitsuhiko/flask>`_

* `enum34 <https://pypi.python.org/pypi/enum34>`_
  
* `git <http://git-scm.com/>`_ (the git executable has to be in the system PATH)
  
* An UCI chess engine ; `Stockfish <http://stockfishchess.org/>`_ is probably the best choice !

2. Clone PicoChess's git repository::
  
  git clone https://github.com/jromang/picochess.git
  
3. Checkout the stable branch (needed to enable auto-updates):

  git checkout stable  
  
4. Run picochess from command line ; picochess has a lot of options type::
  
  python3 picochess.py -h
  
for a list. 
