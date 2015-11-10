all: muon tobin

muon: muon.o
	gcc -o muon muon.o -lm 

muon.o: muon.c
	gcc muon.c -c -std=c99 -H -Wall

tobin: tobin.o
	gcc -o tobin tobin.o

tobin.o: tobin.c
	gcc tobin.c -c -std=c99 -H -Wall
