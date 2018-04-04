#!/bin/sh

rm -rf $1 $1.bkp 
fileName=$(echo $1| cut -d '.' -f 1)
rm -rf ${fileName}_instru.c

mv $1.orig $1
