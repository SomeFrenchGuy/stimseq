INCLUDE_DIR =../include
BIN_DIR = ./bin

CC=gcc

CFLAGS=-I$(INCLUDE_DIR)

OBJ_DIR=./obj

_DEPS = stimseq.h
DEPS = $(patsubst %,$(INCLUDE_DIR)/%,$(_DEPS))

_OBJ = stimseq.o arg_parser.o logger.o sequence_parser.o
OBJ = $(patsubst %,$(OBJ_DIR)/%,$(_OBJ))


$(OBJ_DIR)/%.o: %.c $(DEPS)
	mkdir -p $(OBJ_DIR)
	$(CC) -c -o $@ $< $(CFLAGS)

$(BIN_DIR)/stimseq: $(OBJ)
	mkdir -p $(BIN_DIR)
	$(CC) -o $@ $^ $(CFLAGS) 

.PHONY: clean

clean:
	rm -f $(OBJ_DIR)/* *~ core $(INCDIR)/*~ 
	rm -f $(BIN_DIR)/* *~ core $(INCDIR)/*~ 