#!/usr/bin/python
import re,sys
from shutil import copyfile, move

def cleanup (pattern, inputfile='test.c', outputfile="test.c.algoprog"):
    print "inputfile = %s, outputfile = %s" % (inputfile, outputfile)
    with open(inputfile)as f, open(outputfile,'a+') as f2:
        print 'successfully opened both files'
        myregex=r'.*'+re.escape(pattern)+'.*'
        print myregex
        for line in f:
            patternFound = re.match(myregex,line,re.M|re.I)
            if patternFound:
                continue
            else:
                print line
                f2.write(line)


if __name__ == "__main__":
    inputfile=str(sys.argv[1])
    outputfile=str(sys.argv[1])+".algoprog"
    if len(sys.argv) >= 3:
        pattern=str(sys.argv[2])
    else:
        pattern="MIHIR-DEBUG"
    print "inputfile = %s, outputfile = %s" % (inputfile, outputfile)
    cleanup(pattern,inputfile,outputfile)
    move(outputfile, inputfile)
