CC=gcc
# CFLAGS=-c -std=c99 -H -Wall
CFLAGS=-c -std=c99
LDFLAGS=-lm

all: muon

muon: muon.o
	$(CC) $(LDFLAGS) muon.o -o muon

muon.o: muon.c
	$(CC) $(CFLAGS) muon.c
