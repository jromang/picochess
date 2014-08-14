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

.. _manual-install-label:

Manual installation
-------------------

1. Requirements

PicoChess is mainly targetted for small devices like the `Raspberry Pi <http://www.raspberrypi.org>`_, however is also
runs on a desktop computer (Linux, OSX, Windows). You will need to install this first :
  
* `Python 3 <https://www.python.org/downloads/>`_ (on mac OS X, brew install python3)
  
* `pycrypto <https://pypi.python.org/pypi/pycrypto>`_ (on mac OS X, brew install pycrypto)
  
* `git <http://git-scm.com/>`_ (the git executable has to be in the system PATH)
  
* An UCI chess engine ; `Stockfish <http://stockfishchess.org/>`_ is probably the best choice !

2. Clone PicoChess's git repository::
  
  git clone https://github.com/jromang/picochess.git
  
3. Checkout the stable branch (needed to enable auto-updates):

  git checkout stable  
  
4. Run picochess from command line ; picochess has a lot of options type::
  
  python3 picochess.py -h
  
for a list. 
