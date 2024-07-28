INCLUDE_DIR =../include
BIN_DIR = ./bin

CC=gcc

CFLAGS=-I$(INCLUDE_DIR)

OBJ_DIR=./obj

_DEPS = stimseq.h
DEPS = $(patsubst %,$(INCLUDE_DIR)/%,$(_DEPS))

_OBJ = stimseq.o arg_parser.o 
OBJ = $(patsubst %,$(OBJ_DIR)/%,$(_OBJ))


$(OBJ_DIR)/%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

$(BIN_DIR)/stimseq: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) 

.PHONY: clean

clean:
	rm -f $(OBJ_DIR)/*.o *~ core $(INCDIR)/*~ 
	rm -f $(BIN_DIR)/*.o *~ core $(INCDIR)/*~ 