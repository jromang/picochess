Installation
============

Easy method : using image files
-------------------------------

Manual installation
-------------------

* Requirements

  PicoChess is mainly targetted for small devices like the `Raspberry Pi <http://www.raspberrypi.org>`_, however is also
  runs on a desktop computer. You will need to install this first :
  
  1. `Python 3 <https://www.python.org/downloads/>`_ (on mac OS X, brew install python3)
  
  2. `python-crypto <https://pypi.python.org/pypi/pycrypto>`_
  
  3. `git <http://git-scm.com/>`_ (the git executable has to be in the system PATH)
  
  4. An UCI chess engine ; `Stockfish <http://stockfishchess.org/>`_ is probably the best choice !

* Steps

  1. Clone PicoChess's git repository::
    
    git clone https://github.com/jromang/picochess.git
  
  2. Checkout the stable branch (needed to enable auto-updates)
  
* Running picochess from command line

  Picochess has a lot of options ; type "python3 picochess.py -h" for a list 
