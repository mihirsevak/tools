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

'''
Left to do as of March 30th 2018
1) creating a json file/datastructure which can keep track of instrumentation status
2) file nameing in a proper way so new file is created in a meaningful way

'''

import argparse
from function_instrument import shallow_function_instrument, deep_function_instrument, shallow_file_instrument, deep_file_instrument
from json_utility import init_json, finished_json






'''
Use cases 
debugger --tree shallow|deep
debugger file <function> shallow|deep

'''


import sys




init_json()
args=sys.argv[1:]
tree_mode=False
parser = argparse.ArgumentParser(description = "program")
if args and args[0].startswith("--"):
    parser.add_argument("--tree", nargs='?')
    parser.add_argument("--mode", nargs='?', default='shallow')
    parser.add_argument("--restore")
    parser.add_argument("--clean")
    tree_mode = True
else:
    parser = argparse.ArgumentParser(description = "program")
    parser.add_argument("file", nargs=2)
    parser.add_argument("--function", nargs='?')
    parser.add_argument("--mode", nargs='?', default='shallow')
    parser.add_argument("--restore")
    parser.add_argument("--clean")
    tree_mode = False
args = parser.parse_args()
#print args

if tree_mode == True:
	print 'We will instrument all source code files in this direcotry.'
	all_files = list_all_files()		
   	if args.mode == 'deep':
		print 'we will instrument all source code files in direcotry with deep mode.'
		for file in all_files:
			deep_file_instrument(file,startLine=0, endLine='EOF')
	else:
		print 'we will instrument all source code files in direcotry with shallow mode.'
		for file in all_files:
			shallow_file_instrument(file,startLine=0, endLine='EOF')

else: # WE are in file mode
	#print 'arg.file =', args.file
   	print 'arg.function =', args.function
   	#print 'arg.mode =', args.mode
	if args.function == None:
		if args.mode == 'deep':
			print 'we will instrument entire file {} in a deep mode'.format(args.file[1])
			deep_file_instrument(args.file[1])
		else:
			print 'we will instrument entire file {} in a shallow mode'.format(args.file[1])
			shallow_file_instrument(args.file[1])
	else:
		if args.mode == 'deep':
			print 'we will instrument file {} and function {} in a deep mode'.format(args.file[1], args.function)
			deep_function_instrument(args.file[1],args.function)
		else:
			print 'we will instrument file {} and function {} in a shallow mode'.format(args.file[1], args.function)
			shallow_function_instrument(args.file[1],args.function)


finished_json()
     
     

