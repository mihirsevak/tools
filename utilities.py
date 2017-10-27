import sys
import re

def chomp(x):
    if x.endswith("\r\n"): return x[:-2]
    if x.endswith("\n"): return x[:-1]
    return x[:] 

def is_single_line_prototype(line_of_text, function_name):
    print 'came in single_line_prototype'
    oneLineFuncPrototype = re.match(r'.*%s(\s?)+\(.*\)(\s?)+'% function_name, line_of_text,re.M|re.I)
    if oneLineFuncPrototype:
        print 'it is a single line prototype'
        return True

def is_opening_brace_with_prototype(line_of_text, function_name):
    print 'came in single_line_prototype'
    oneLineFuncPrototype = re.match(r'.*%s(\s?)+\(.*\)(\s?)+\{(\s?)+'% function_name, line_of_text,re.M|re.I)
    if oneLineFuncPrototype:
        print 'it is a brace with function prototype'
        return True

def find_end_of_function (inputfile, startLine=0):
    braces = 0
    lineNumber = 0
    init = True
    with open(inputfile,'r') as f:
        for line_of_text in f:
            lineNumber = lineNumber + 1
            if startLine > lineNumber:
                continue
            openBraceFound = re.match(r'.*{.*',line_of_text,re.M|re.I)
            closeBraceFound = re.match(r'.*}.*',line_of_text,re.M|re.I)
            if openBraceFound:
                braces = braces + 1;
                init = False
            if closeBraceFound:
                braces = braces - 1;

            if braces == 0 and init == False:
                print 'end of function at line number %d' % lineNumber
                return

inputfile = str(sys.argv[1])
startLine = int(sys.argv[2])
find_end_of_function(inputfile, startLine)
