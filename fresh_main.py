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
Left to do as of April 4th 2018 in Beta version
1) creating a json file/datastructure which can keep track of instrumentation status 
   JSON file must be created per source file.
   A) Should this file reside in the same place as source code file?
   B) Should this file reside in /opt/debugger directory?
   C) When should this file be cleaned up?
   D) Should this JSON file be deleted when cleanup is run?

2) Throw exceptions and handle failures gracefully. Create a list for uninstrumented c files
3) Wire up cleanup 
4) Create an installer which installs all the files in /opt/debugger folder 
5) Check how can we work only with binary files and don't have to distribute python source code

Next version:
1) How to handle C++ where function signature may be over loaded and there may be multiple 
funcionts with the same name [create a list of function and line numbers]
2) Support for other programming languages

'''

import argparse
from function_instrument import shallow_function_instrument, deep_function_instrument, shallow_file_instrument, deep_file_instrument
from file_operations import script_cleanup, list_all_files
from json_utility import init_json, finished_json
from sys import exit





'''
Use cases 
debugger --tree (shallow|deep) | (cleanup)
debugger file (<function> shallow|deep) | (cleanup)

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
    parser.add_argument("--clean", nargs='?', default='True')
    tree_mode = True
else:
    parser = argparse.ArgumentParser(description = "program")
    parser.add_argument("file", nargs=2)
    parser.add_argument("--function", nargs='?')
    parser.add_argument("--mode", nargs='?', default='shallow')
    parser.add_argument("--restore")
    parser.add_argument("--clean", nargs='?', default='True')
    tree_mode = False
args = parser.parse_args()
#print args
print args.clean

if tree_mode == True:
	print 'We will instrument all source code files in this direcotry.'
	all_files = list_all_files()		
	if args.clean == None: 
		print 'going for cleanup entire tree'
		for file in all_files:
			script_cleanup(file)
		exit(0) 
   	elif args.mode == 'deep':
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
	if args.clean == None:
		print 'going for cleanup of file ', args.file[1]
		script_cleanup(args.file[1])
		exit(0) 
	elif args.function == None:
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
     
     

