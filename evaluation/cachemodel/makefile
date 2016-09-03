# Executable
EXE    = completion

# Compiler, Linker Defines
CC      = g++
CFLAGS  = -Wall -O2 -Wno-deprecated
# LIBS    = ./lib/libsrilm.a ./lib/lm.a ./lib/misc.a ./lib/dstruct.a
LDFLAGS = $(LIBS)

# Compile and Assemble C++ Source Files into Object Files
%.o: %.cc
	echo compiling...$<
	$(CC) $(CFLAGS) -c $<
# -o $@
# Source and Object files
SRC    = $(wildcard *.cpp)
OBJ    = $(patsubst %.cpp, %.o, $(SRC))

# Link all Object Files with external Libraries into Binaries
$(EXE): $(OBJ)
	echo linking...
	$(CC) $(CFLAGS) $(OBJ) $(LDFLAGS) -o $(EXE) -lz

.PHONY: clean
clean:
	 -rm -f core *.o
