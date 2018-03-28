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
