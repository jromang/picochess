picochess
=========

Requirements:

  1. python3
  1. crypto

Steps:
  
  1. Install python3 (on mac OS X, brew install python3)
  1. Install pycrypto (on mac OS X, brew install pycrypto)
  1. Execute "python3 picochess.py -h" for a list of options
  
  Options:
  
  picochess.py [-h] [-d DGT_PORT] [-e ENGINE] [-hs HASH_SIZE] [-t THREADS]
               [-l {notset,debug,info,warning,error,critical}]
               [-lf LOG_FILE] [-r REMOTE] [-u USER] [-p PASSWORD]
               [-k KEY_FILE] [-pgn PGN_FILE]


optional arguments:

  -h, --help            show this help message and exit
  -d DGT_PORT, --dgt-port DGT_PORT
                        enable dgt board on the given serial port such as
                        /dev/ttyUSB0
  
  -e ENGINE, --engine ENGINE
                        stockfish executable path
  
  -hs HASH_SIZE, --hash-size HASH_SIZE
                        hashtable size in MB (default:64)
  
  -t THREADS, --threads THREADS
                        number of engine threads (default:1)
  
  -l {notset,debug,info,warning,error,critical}, --log-level {notset,debug,info,warning,error,critical}
                        logging level
  
  -lf LOG_FILE, --log-file LOG_FILE
                        log to the given file
  
  -r REMOTE, --remote REMOTE
                        remote server running the engine
  
  -u USER, --user USER  remote user on server running the engine
  
  -p PASSWORD, --password PASSWORD
                        password for the remote user
  
  -k KEY_FILE, --key-file KEY_FILE
                        key file used to connect to the remote server
  
  -pgn PGN_FILE, --pgn-file PGN_FILE
                        pgn file used to store the games

Sample Run command:

  1. python3 picochess.py -e <engine location> -ldebug (to run with a desired engine)
  2. python3 picochess.py -e "/Applications/Deep HIARCS 14 WCSC/DeepHiarcs14WCSC" -d/dev/rfcomm0 -ldebug (to run hiarcs with bluetooth)
  3. python3 picochess.py -e <engine location> -d<device> -ldebug -r<server> -u<username> -p<password> (to run a remote engine)
  
