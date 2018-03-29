#!/usr/bin/python

'''
0) prepare environment 
    0.a) install ctags and readtags if not installed
    0.b) using ctags create a tags file in the root of the project
	0.c) create two json data structures to keep track of whether a function has been instrumented or not
		 X) shallow_instrumented (instrumented or not)
		 X) deeply_instrumented (if instrumentation is deep or shallow)
	
1) instru_open a file  
	1.a) create a backup of original file and create/open a working copy of the file
	1.b) create/open a file in a read only mode
	1.c) create file line offset list

2) instru_func_list from a file
	2.a) create a dictionary of list of all functions from a specific function 
	2.b) this dictionary should have list of all functions being called from a given function.
	total_source_dictionary = { 'main': [func1, func2, func3],
								'func1': [func4, func5,func6],
								'func2': none,
								'func3': [func2],
								'func4': [func1,func2],
								.....}
	2.c) run through this dictionary while keep checking with two json files. 




'''




# MIHIR-notes:
# ctags -x --c-kinds=f readtags.c  <-- to list all the functions in a file


import argparse
from function_instrument import shallow_function_instrument, deep_function_instrument
from file_instrument import shallow_file_instrument, deep_file_instrument




shallow_instrumented = {}
deep_instrumented = {}



parser = argparse.ArgumentParser()
parser.add_argument("mode", default="shallow", help="deep, shallow | Should I do deep instrumentation or shallow instrumentation. By default shallow mode.")
parser.add_argument("file", help="please provide a filename which needs to be instrumented")
#parser.add_argument("function", dest="function_name", help="please provide a function name which needs to be instrumented", nargs ='?' , action="store")
parser.add_argument('function', nargs=2, help='please provide a function name which needs to be instrumented')
parser.add_argument("tree",help="should I instrument entire source tree from this directory??", action = "store_false")
args = parser.parse_args()



if args.tree == True:
	print 'We will instrument all source code files in this direcotry.'
	all_files = list_all_files()		
	if args.mode == "deep":
		print 'we will instrument all source code files in direcotry with deep mode.'
		for file in all_files:
			deep_file_instrument(file,startLine=0, endLine='EOF')
	else:
		print 'we will instrument all source code files in direcotry with shallow mode.'
		for file in all_files:
			shallow_file_instrument(file,startLine=0, endLine='EOF')
else:
	if args.mode == "deep":
		if args.function:
			#print (parser.parse_args('function'.split()) )
			print 'we will instrument file {} and function {} in a deep mode'.format(args.file, args.function[1])
			deep_function_instrument(args.file,args.function[1])
		else:
			print 'we will instrument entire file {} in a deep mode'.format(args.file)
			deep_file_instrument(args.file,startLine=0, endLine='EOF')
	else:
		if args.function:
			#print (parser.parse_args('function'.split()) )
			print 'we will instrument file {} and function {} in a shallow mode'.format(args.file, args.function[1])
			shallow_function_instrument(args.file,args.function[1])
		else:
			print 'we will instrument entire file {} in a shallow mode'.format(args.file)
			shallow_file_instrument(args.file,startLine=0, endLine='EOF')

# if args.v :
# 	print 'we are in verbose mode'
# if args.b == 'magic.name':
#     print 'You nailed it!'








