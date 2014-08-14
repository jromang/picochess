Installation
============

Easy method : using image files
-------------------------------

Manual installation
-------------------

1. Requirements
PicoChess is mainly targetted for small devices like the `Raspberry Pi <http://www.raspberrypi.org>`_, however is also
runs on a desktop computer (Linux, OSX, Windows). You will need to install this first :
  
* `Python 3 <https://www.python.org/downloads/>`_ (on mac OS X, brew install python3)
  
* `pycrypto <https://pypi.python.org/pypi/pycrypto>`_
  
* `git <http://git-scm.com/>`_ (the git executable has to be in the system PATH)
  
* An UCI chess engine ; `Stockfish <http://stockfishchess.org/>`_ is probably the best choice !

2. Clone PicoChess's git repository::
  
  git clone https://github.com/jromang/picochess.git
  
3. Checkout the stable branch (needed to enable auto-updates):

  git checkout stable  
  
4. Run picochess from command line ; picochess has a lot of options type::
  
  python3 picochess.py -h
  
for a list. 
