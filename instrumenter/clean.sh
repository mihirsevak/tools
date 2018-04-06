#!/bin/sh

fileName=$(echo $1| cut -d '.' -f 1)
rm -rf ${fileName}_instru.c

if [ -e $1.orig ]
then 
	rm -rf $1 $1.bkp 
	mv $1.orig $1
fi