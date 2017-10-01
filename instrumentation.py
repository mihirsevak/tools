#!/bin/python

import re

filename="test.c"
outputfile="test2.c"
marker="main"
patternFound = False

with open(filename)as f, open(outputfile,'w') as f2:
    for line_of_text in f:
        matchObj = re.match(r'.*main.*',line_of_text,re.M|re.I)

        if patternFound == True:
            braceFound = re.match(r'.*{.*',line_of_text,re.M|re.I)
            if braceFound:
                f2.write(line_of_text)
                f2.write("%s %s %s\n" % ("printf(\"MIHIR-DEBUG:: came in function ", repr(marker), ");"));
            else:
                f2.write("%s %s %s\n" % ("printf(\"MIHIR-DEBUG:: came in function ", repr(marker), ");"));
            patternFound = False
            continue

        f2.write(line_of_text)
        if matchObj:
            patternFound = True
            print (line_of_text)

        #else:
        #    print 'no match'
        
