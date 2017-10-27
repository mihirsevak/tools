#!/usr/bin/python

import re
import sys, os
import string
from shutil import copyfile, move
from utilities.py import chomp, is_single_line_prototype, is_opening_brace_with_prototype
                         find_end_of_function

#filename=$1
#outputfile="test2.c"
#marker="main"


def help():
    print 'to use this tool pass a c/c++ file name followed by instrumentation.py'
    print 'For example: ./instrumentaiton.py test.c'
    print '         or: python instrumentation.py test.c'
    sys.exit(0)

def multiline_function_operation(inputfile, outputfile, function_name):
    #print 'came in function multiline_function_operation inputfile = %s outputfile = %s function_name = %s' %(inputfile, outputfile, function_name)
    patternFound = False
    function_name_found = False
    with open(inputfile)as f, open(outputfile,'a+') as f2:
        for line_of_text in f:
            matchObj = re.match(r'.*%s.*'% function_name, line_of_text,re.M|re.I)
            if matchObj:
                #Handle brace in same line too
                if is_opening_brace_with_prototype(line_of_text, function_name) == True:
                    f2.write(line_of_text)
                    f2.write("%s \n" % ("printf(\"MIHIR-DEBUG:: came in function %s at line %d in file %s\\n\", __func__, __LINE__, __FILE__ );"))
                    f2.write("%s %s %s\n" % ("system(\"echo \'came in function ", function_name, " \' >> /tmp/mihir.log);"))
                    continue
                if is_single_line_prototype(line_of_text, function_name) == True:
                    patternFound = True

            if patternFound == True:
                print 'came in pattern found block to write debug lines'
                braceFound = re.match(r'.*{.*',line_of_text,re.M|re.I)
                semiColonFound = re.match(r'.*;.*',line_of_text,re.M|re.I)
                closeParanFound = re.match(r'.*\).*',line_of_text,re.M|re.I)
                f2.write(line_of_text)
                if braceFound:
                    print 'came in brace found block to write debug lines'
                    #f2.write(line_of_text)
                    f2.write("%s \n" % ("printf(\"MIHIR-DEBUG:: came in function %s at line %d in file %s\\n\", __func__, __LINE__, __FILE__ );"))
                    f2.write("%s %s %s\n" % ("system(\"echo \'came in function ", function_name, " \' >> /tmp/mihir.log);"))
                elif semiColonFound :
                    patternFound = False
                    fuction_name_found = False

                else :
                    #f2.write("%s \n" % ("printf(\"MIHIR-DEBUG:: came in function %s at line %d in file %s\\n\", __func__, __LINE__, __FILE__ );"))
                    ##f2.write("%s %s %s\n" % ("printf(\"MIHIR-DEBUG:: came in function ", repr(marker), ");"));
                    #f2.write("%s %s %s\n" % ("system(\"echo \'came in function ", function_name, " \' >> /tmp/mihir.log)"))
                    pass
                   
                continue

            # Handling multiline function 
            if function_name_found == True :
                print '############came in function_name_found block'
                print '#### ACTUAL LINE =', line_of_text
                #search for openning ( and turn on patternFound flag
                words_in_line = line_of_text.translate(None,string.whitespace)
                print 'words in line =', words_in_line
                first_word = words_in_line[0]
                print 'first word =', first_word
                if first_word == '(':
                    print 'turning on open paran found and patternFound flag'
                    patternFound = True

            ## DEFAULT WRITING
            f2.write(line_of_text)
            if function_name_found == True:
                print 'we found the function name but next line was not open ( so disable flag'
                function_name_found = False

            # Handling function name part
            if matchObj:
                words_in_line = chomp(line_of_text).strip().split(' ')
                print 'words_in_line =', words_in_line
                last_word=chomp(words_in_line[-1])
                word = last_word.translate(None, string.whitespace) 
                print last_word, last_word.strip(), last_word.rstrip(),'END'
                if word == function_name :
                    print line_of_text
                    print '***************multi_line_function process accordingly'
                    print '***************next line\'s first character must be ('
                    print '***************if ( is found just look for { and add your line after it'
                    function_name_found = True
                    continue
                else:
                    print 'function name = ', function_name, 'and last_word =', last_word.rstrip(),'END'
                    continue
                    patternFound = True
                    print (line_of_text)

            #else:
            #    print 'no match'

def function_operation(inputfile, outputfile, function_name):
    print 'came in function function_operation inputfile = %s outputfile = %s function_name = %s' %(inputfile, outputfile, function_name)
    patternFound = False
    with open(inputfile)as f, open(outputfile,'a+') as f2:
        for line_of_text in f:
            matchObj = re.match(r'.*%s.*'% function_name, line_of_text,re.M|re.I)

            if patternFound == True:
                braceFound = re.match(r'.*{.*',line_of_text,re.M|re.I)
                if braceFound:
                    f2.write(line_of_text)
                    f2.write("%s \n" % ("printf(\"MIHIR-DEBUG:: came in function %s at line %d in file %s\\n\", __func__, __LINE__, __FILE__ );"))
                    f2.write("%s %s %s\n" % ("system(\"echo \'came in function ", function_name, " \' >> /tmp/mihir.log)"))
                else:
                    f2.write("%s \n" % ("printf(\"MIHIR-DEBUG:: came in function %s at line %d in file %s\\n\", __func__, __LINE__, __FILE__ );"))
                    #f2.write("%s %s %s\n" % ("printf(\"MIHIR-DEBUG:: came in function ", repr(marker), ");"));
                    f2.write("%s %s %s\n" % ("system(\"echo \'came in function ", function_name, " \' >> /tmp/mihir.log)"))
                patternFound = False
                continue

            f2.write(line_of_text)
            if matchObj:
                patternFound = True
                print (line_of_text)

            #else:
            #    print 'no match'
            
def find_all_functions(filename="NO_FILE_PROVIDED",line_numbers=False,handle_multiline_func=True):
    '''
        1) look for ( and ) 
           1.a) bot ( and ) may not be in a same line
           1.b) in between there may be special characters
        2) ) must be followed by {
        3) ( must not be preceded by if, else or elif
        4) the word just before ( is a function name
        5) ) must not be followed by ;
        6) There must not be = before (

    Algo:
        look for (
        store previous word and make sure previous word is not 'if', 'else' or there is no = in words before (
        look for ) followed by { 
        make sure ) is not followed by ;
    ''' 

    ''' 
    #To run this function in a stand alone mode
    if ( len(sys.argv) <= 1 ):
        help()
    else:
        filename = sys.argv[1]
    '''

    if filename == "NO_FILE_PROVIDEDE" :
        print "ERROR:: You idiot you haven't provided file to process"
        sys.exit(-1)

    num = 0
    open_paren_difference = 0
    multi_line = False
    all_functions_info = []

    with open(filename) as f:
        for line_of_text in f:
            num += 1

            #Multiline handling
            if handle_multiline_func == True:
                if multi_line == True:
                    #Just check for paren match and ;
                    num_of_open_paren = line_of_text.count('(')
                    num_of_close_paren = line_of_text.count(')')
                    paren_diff = num_of_open_paren - num_of_close_paren
                    if (open_paren_difference + paren_diff) == 0 :
                        #print '#######seems like end of multiline expression has arrived', line_of_text.strip()[-1]
                        multi_line = False
                        if line_of_text.strip()[-1] == ';':
                            #print '#######This is not a function we are interested in'
                            continue
                    else:
                        #print '#######multiline expression is still going on'
                        continue

                if '(' in line_of_text:
                    # count opne paren and close paren and until they match its a same line is running.
                    num_of_open_paren = line_of_text.count('(')
                    num_of_close_paren = line_of_text.count(')')
                    paren_diff = num_of_open_paren - num_of_close_paren
                    if num_of_open_paren > num_of_close_paren:
                        #print '#######This is a multi-line function:', line_of_text
                        open_paren_difference = paren_diff
                        multi_line = True
                        continue
            #Multiline handling ends
                
            openParen = re.match(r'.*\(.*', line_of_text, re.M | re.I)
            if openParen:
                #print 'this can be a function line', line_of_text
                words = line_of_text.partition('(')
                #in some cases ppl write function open param in a new line. Trying to capture that.
                if words[0] != '(' or '(' not in words[0] :
                    #print 'checking the first word in words list'
                    # in an average case words[0] will contain function name. If a return type and 
                    # static argument is included still last word (in english) would be function 
                    # name. So we have to split word[0] on spaces and capture the last element
                    individual_words = words[0].split(' ')
                    
                    #Handling variable assignment 
                    if '=' in words[0]:
                        continue

                    func_name='default_name'
                    #print individual_words, len(individual_words)
                    if len(individual_words) > 1 :
                        #print 'more than one words before the ('
                        func_name = individual_words[len(individual_words)-1]
                    else :
                        #print 'exactly 1 word before ('
                        func_name = words[0] 

                    #Handling if or else cases 
                    if func_name == "if" or func_name == "else" or func_name == "while" or func_name == "defined":
                        continue

                    #end of line checkings
                    if ';' in line_of_text:
                        continue

                    func_name = func_name.strip()
                    if func_name != '':
                        #if line_numbers == True:
                        #    print num,':' ,
                        #print func_name
                        all_functions_info.append((num,func_name))
    return all_functions_info


'''
To Do:
    1) Process commandline arguments in a professional way
    2) Start reading a headerfiles and figure out where does function resides? some library or user written library?
    3) Provide a way to create a logfile in a specified location and log the whole damn thing. Actually it should be all three options 
        3.a) instrumentation generated logfile
        3.b) printf to display on screen
        3.c) Some system generated log file
    4) Create different modes to instrument at different level
        4.a) Normal mode will instrument all the functions in the beginning to find out code path 
        4.b) Deep Function mode will instrument every single code line to find which line is breaking code
        4.c) Intense mode will print/check every variable and pointer in this specific code and report if something is out of memory or garbage value
        4.d) Test Mode will read a text file with input and expected output and find bugs
        4.e) Others: future expansions
    5) Apply object oriented design to this tool. Break in multi file, multi module software
    6) Which design patterns can be applied here? 
        6.a) Singleton -- only one instance has to run? 
        6.b) What other design patterns can be applied here?
    7) How can this be used in multi-threaded setting???
    8) Handle commented out functions. (Ignore all comments lines)
    *) Look into how we can create a binary out of this so we can distribute it 

'''



#USE CASE 1 #if a function to be instrumented is passed in as an argument.
operating_file = str(sys.argv[2])
inputfile = str(sys.argv[2])
backup_file = str(sys.argv[2]) + ".orig"
function_to_instrument = str(sys.argv[1])
outputfile='temp.c' #FIXME -- output filename has to be dynamically created

#FIXME -- this has to be done more intelligently 
if not os.path.exists(backup_file) :
    copyfile(operating_file, backup_file)

multiline_function_operation(inputfile, outputfile, function_name=function_to_instrument) 
move(outputfile, inputfile)



'''
#USE CASE 2 #IF all functions has to be instrumented
operating_file = str(sys.argv[1])
inputfile = str(sys.argv[1])
backup_file = str(sys.argv[1]) + ".orig"
outputfile='temp.c' #FIXME -- output filename has to be dynamically created

all_functions = find_all_functions(filename=str(sys.argv[1]),line_numbers=False,handle_multiline_func=True)

#FIXME -- this has to be done more intelligently 
if not os.path.exists(backup_file) :
    copyfile(operating_file, backup_file)

for i in all_functions:
    print i[0],": ", i[1] #i[0] is a line number and i[1] is a function name
    function_operation(inputfile, outputfile,function_name=i[1]) 
    move(outputfile, inputfile)
'''
