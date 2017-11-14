#makefile to compile Rodent III on Linux
# PREFIX=/usr/local
PREFIX=/opt/picochess/engines/rodent3

#define the directory for the executable file
BINDIR = $(PREFIX)/bin

#define the directory for the data files
# DATADIRBOOKS = $(PREFIX)/share/rodentIII-books
DATADIRBOOKS = $(PREFIX)/books
# DATADIRPERSONALITIES = $(PREFIX)/share/rodentIII-persons
DATADIRPERSONALITIES = $(PREFIX)/personalities

# Define the CPP compiler
# CXX = g++
# LocutusOfPenguin: use this instead => cross compile with ubuntu 16.04 - rodent3 needs the c++14 (so use last line!)
# sudo apt install gcc-4.9-arm-linux-gnueabihf g++-4.9-arm-linux-gnueabihf pkg-config-arm-linux-gnueabihf   <<< c++11
# sudo apt install gcc-arm-linux-gnueabihf  g++-arm-linux-gnueabihf pkg-config-arm-linux-gnueabihf   <<< c++14
CXX = arm-linux-gnueabihf-g++

# Define features
# Other options are -DBOOKGEN -DNO_THREADS
CFG = -DNDEBUG -DUSEGEN -DUSE_THREADS -DBOOKSPATH=$(DATADIRBOOKS) -DPERSONALITIESPATH=$(DATADIRPERSONALITIES)
CFG1 = -DUSEGEN -DUSE_THREADS -DBOOKSPATH=$(DATADIRBOOKS) -DPERSONALITIESPATH=$(DATADIRPERSONALITIES)

# Define compiler flags
CXXFLAGS = -g -std=c++14 -Wall -Wno-unknown-pragmas -O3 -fno-rtti -pthread $(CFG)
CXX1FLAGS = -g -std=c++14 -Wall -Wno-unknown-pragmas -pthread $(CFG1)

# Define linker options
# LDFLAGS = -s -Wl,--no-as-needed,--gc-sections
# LocutusOfPenguin: use this instead => Jessie system (c++14 not installed cause of gcc4.9) needs cross compile to work!
LDFLAGS = -s -static -static-libgcc -static-libstdc++ -Wl,--no-as-needed,--gc-sections
LD1FLAGS = -lm

# Command line switches
lto = yes
native = no

# Compile with Link Time Optimisation
ifeq ($(lto),yes)
	CXXFLAGS += -flto
	LDFLAGS += -flto
endif

# Optimise for local machines
ifeq ($(native),yes)
	CXXFLAGS += -march=native
	LDFLAGS += -march=native
endif

# Define outpout name and settings file
EXENAME= rodentIII
CONFIGFILE = basic.ini

.PHONY: clean install update remove help

default: build

build:
	@echo "Type make help for additional options"
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo "SHOW_OPTIONS" > $(CONFIGFILE)

build-popcnt:
	@echo "Type make help for additional options"
	$(CXX) $(CXXFLAGS) -msse3 -mpopcnt $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo "SHOW_OPTIONS" > $(CONFIGFILE)

clang-profiled:
	@echo "Type make help for additional options"
	$(CXX) $(LDFLAGS) $(CXXFLAGS) -fprofile-instr-generate -o $(EXENAME) src/*.cpp
	@echo bench | ./rodentIII > /dev/null
	@llvm-profdata merge -output=default.profdata default.profraw
	$(CXX) $(CXXFLAGS) -fprofile-instr-use=default.profdata $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo "SHOW_OPTIONS" > $(CONFIGFILE)
	@rm -f *.profdata *.profraw

clang-popcnt-profiled:
	@echo "Type make help for additional options"
	$(CXX) $(CXXFLAGS) -msse3 -mpopcnt -fprofile-instr-generate $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo bench | ./rodentIII > /dev/null
	@llvm-profdata merge -output=default.profdata default.profraw
	$(CXX) $(CXXFLAGS) -msse3 -mpopcnt -fprofile-instr-use=default.profdata $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo "SHOW_OPTIONS" > $(CONFIGFILE)
	@rm -f *.profdata *.profraw

gcc-profiled:
	@echo "Type make help for additional options"
	$(CXX) $(CXXFLAGS) -fprofile-generate $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo bench | ./rodentIII > /dev/null
	$(CXX) $(CXXFLAGS) -fprofile-use $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo "SHOW_OPTIONS" > $(CONFIGFILE)
	@rm -f *.gcda

gcc-popcnt-profiled:
	@echo "Type make help for additional options"
	$(CXX) $(CXXFLAGS) -msse3 -mpopcnt -fprofile-generate $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo bench | ./rodentIII > /dev/null
	$(CXX) $(CXXFLAGS) -msse3 -mpopcnt -fprofile-use $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo "SHOW_OPTIONS" > $(CONFIGFILE)
	@rm -f *.gcda

build-static:
	@echo "Type make help for additional options"
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -static -o $(EXENAME) src/*.cpp
	@echo "SHOW_OPTIONS" > $(CONFIGFILE)

build-debug:
	@echo "Type make help for additional options"
	$(CXX) $(CXX1FLAGS) $(LD1FLAGS) -o $(EXENAME) src/*.cpp
	@echo "SHOW_OPTIONS" > $(CONFIGFILE)

gcc-lcov:
	@echo "Type make help for additional options"
	$(CXX) $(CXXFLAGS) -fprofile-generate -ftest-coverage $(LDFLAGS) -o $(EXENAME) src/*.cpp
	@echo bench | ./rodentIII > /dev/null
	@lcov --capture --directory . --no-external --gcov-tool gcov --output-file coverage.info > /dev/null
	@genhtml coverage.info --output-directory coveragedir > /dev/null
	@rm -f rodentIII *.gcda *.gcno coverage.info

bookgen:
	@echo "Type make help for additional options"
	$(CXX) $(CXXFLAGS) -DBOOKGEN $(LDFLAGS) -o $(EXENAME)-bookgen src/*.cpp
	@echo "SHOW_OPTIONS" > $(CONFIGFILE)
	@./$(EXENAME)-bookgen
	@rm -f $(EXENAME)-bookgen

clean:
	rm -rf $(EXENAME) $(EXENAME).exe book_gen.h basic.ini *.profdata *.profraw *.gcda *.gcno coverage.info coveragedir

install:
	mkdir -p $(BINDIR)
	mkdir -p $(DATADIRBOOKS)
	mkdir -p $(DATADIRPERSONALITIES)
	cp $(EXENAME) $(BINDIR)
	cp $(CONFIGFILE) $(DATADIRPERSONALITIES)
	#find ../books/ -name '*.bin' -type f -exec cp '{}' $(DATADIRBOOKS) \;
	#find ../personalities/ -name '*.ini' -type f -exec cp '{}' $(DATADIRPERSONALITIES) \;
	cp -r ../books/* $(DATADIRBOOKS)
	cp -r ../personalities/* $(DATADIRPERSONALITIES)
	chmod 755 $(BINDIR)/$(EXENAME)
	chmod -R 644 $(DATADIRBOOKS)/*
	find $(DATADIRBOOKS) -type d -exec chmod 755 {} \;
	chmod -R 644 $(DATADIRPERSONALITIES)/*
	find $(DATADIRPERSONALITIES) -type d -exec chmod 755 {} \;

# This just performs a copy of rodentIII engine
update:
	cp $(EXENAME) $(BINDIR)

remove:
	rm -f $(BINDIR)/$(EXENAME)
	rm -rf $(DATADIRBOOKS)
	rm -rf $(DATADIRPERSONALITIES)

help:
	@echo ""
	@echo "To compile RodentIII type:"
	@echo ""
	@echo "make build			> Build Rodent III"
	@echo "make build-popcnt		> Build with fast popcnt"
	@echo "make clang-profiled		> Build with pgo optimisations (clang++ required)"
	@echo "make clang-popcnt-profiled	> Build with pgo+popcnt optimisations (clang++ required)"
	@echo "make gcc-profiled		> Build with pgo optimisations (g++ required)"
	@echo "make gcc-popcnt-profiled	> Build with pgo+popcnt optimisations (g++ required)"
	@echo "make build-static		> Build a static binary"
	@echo "make build-debug		> Build a debug version"
	@echo "make gcc-lcov			> Code coverage with lcov (g++ required)"
	@echo "make bookgen			> Build internal book"
	@echo "make clean			> Clean up"
	@echo "make install			> Install RodentIII (root privileges required)"
	@echo "make update			> Update RodenIII engine (root privileges required)"
	@echo "make remove			> Remove RodenIII from your system (root privileges required)"
