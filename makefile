CC=gcc
CFAGS=-c -std=c99 -H -Wall
LDFLAGS=-lm


all: muon tobin


muon: muon.o
	$(CC) $(LDFLAGS) muon.o

muon.o: muon.c
	$(CC) $(CFLAGS) muon.c


tobin: tobin.o
	$(CC) tobin.o

tobin.o: tobin.c
	$(CC) $(CFLAGS) tobin.c 
