#!/usr/bin/python

import re
import sys

#filename=$1
outputfile="test2.c"
marker="main"
patternFound = False


def help():
    print 'to use this tool pass a c/c++ file name followed by instrumentation.py'
    print 'For example: ./instrumentaiton.py test.c'
    print '         or: python instrumentation.py test.c'
    sys.exit(0)

def function_operation():
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
            
def find_all_functions(line_numbers=False,handle_multiline_func=True):
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
    if ( len(sys.argv) <= 1 ):
        help()
    else:
        filename = sys.argv[1]

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
    2) Start reading a headerfiles and figure out where does function lie? some library or user written library?
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
    *) Look into how we can create a binary out of this so we can distribute it 

'''




all_functions = find_all_functions(line_numbers=False,handle_multiline_func=True)
for i in all_functions:
    print i[0],": ", i[1]
