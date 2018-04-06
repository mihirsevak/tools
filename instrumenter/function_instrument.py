#!/usr/bin/python

import sys
import subprocess
import glob
import time
import os.path
#from fresh_main import shallow_instrumented, deep_instrumented
from file_operations import create_outputfile, post_instrumentation_fileops, chomp
from collections import OrderedDict
from json_utility import add_func



def find_function_body(inputFile="Do_Not_Know",functionName="some_function"):
	#filename="/home/parallels/Downloads/ctags-5.8/readtags.c"
	cmd = "ctags -x --c-kinds=f " + inputFile + " | grep \'^" + functionName +" \' | awk '{ print $3 }'"
	print 'INSTRU-DEBUG:: cmd = ',cmd
	function_line = subprocess.check_output(cmd, shell=True)
	print 'INSTRU-DEBUG:: function definationLine = ' + function_line + ' for function = ' + functionName
	#Searching for openning brace
	try:
		cmd = "awk -v s=" + chomp(function_line) + "  'NR>=s && /{/              {c++} NR>=s && /{/ && c && !--c {print NR; exit}' " + inputFile
		beginning_line = subprocess.check_output(cmd,shell=True)
	except:
		#THIS IS A HACK AND WILL FIX WHEN WE ADD FUNCTIONALITY FOR C++ FUNCTION OVER LOADING
		#Write an entry in a result log that this function was not fully processed
		function_lines = function_line.split('\n');
		cmd = "awk -v s=" + chomp(function_line[0]) + "  'NR>=s && /{/              {c++} NR>=s && /{/ && c && !--c {print NR; exit}' " + inputFile
		beginning_line = subprocess.check_output(cmd,shell=True)
	print 'INSTRU-DEBUG:: function body beginningLine = ' + beginning_line + ' for function = ' + functionName
	#Searching for closing brace
	cmd = "awk -v s=" + chomp(beginning_line) + "  'NR>=s && /{/              {c++} NR>=s && /}/ && c && !--c {print NR; exit}' " + inputFile
	ending_line = subprocess.check_output(cmd,shell=True)
	print 'INSTRU-DEBUG:: function endingLine = ', ending_line
	return (beginning_line, ending_line)



def find_function_for_message(inputFile,message='This is MIHIR message'):
	if message == 'This is MIHIR message':
		#throw an exception 
		print 'IDIOT you did not pass the message you are searching for'
		return

	cmd = "grep -i -n \""  + message  + "\" " +  inputFile + " | awk -F ':' '{ print $1 }' "
	list_of_result = subprocess.check_output(cmd,shell=True).split('\n')
	list_of_result.remove('')
	list_of_result = sorted(map(int, list_of_result))
	print list_of_result


	#Build function name and line number dictionary
	cmd = "ctags -x --c-kinds=f " + inputFile + " | awk '{ print $1 }'"
	functionNameList = subprocess.check_output(cmd, shell=True).split('\n')
	cmd = "ctags -x --c-kinds=f " + inputFile + " | awk '{ print $3 }'"
	lineNumberList = subprocess.check_output(cmd, shell=True).split('\n')
	lineNumberList.remove('')
	lineNumberList = map(int, lineNumberList)
	#print functionNameList

	sorted_function_list = sorted(zip(lineNumberList, functionNameList))
	functions_to_be_instrumented = []
	for k,v in sorted_function_list:
		beginning_line = int(k)
		cmd = "awk -v s=" + str(beginning_line) + "  'NR>=s && /{/              {c++} NR>=s && /}/ && c && !--c {print NR; exit}' " + inputFile
		ending_line = subprocess.check_output(cmd,shell=True)
		for index in list_of_result:	
			if int(beginning_line) < int(index) and int(ending_line) > int(index):
				if v not in functions_to_be_instrumented:
					functions_to_be_instrumented.append(v)	

	print functions_to_be_instrumented
	return

def shallow_function_instrument(inputFile="Do_Not_Know",functionName="some_function"):
	if add_func(functionName, 'shallow') == True:
		return

	startLine, endLine = find_function_body(inputFile,functionName)
	enter_instrument = int(startLine) + 1
	exit_instrument = int(endLine) - 1
	#print 'INSTRU-DEBUG:: function {}, startLine = {}, endLine = {}, enter_instrument = {} and exit_instrument = {}'.format(current_item[1], startLine[:-1], endLine[:-1], enter_instrument, exit_instrument)
	
	#First pass to build line offset list
	lineNumber = 0	
	line_offset = []

	offset = 0
	with open(inputFile,'r') as fileName:
		for line in fileName:
			line_offset.append(offset)
			offset += len(line)
		fileName.seek(0)
	endLine = line_offset[-1]

	#This is for output file
	readinFile, resultFile = create_outputfile(inputFile)
	#print resultFile


	with open(readinFile,'r') as input, open(resultFile, 'a+') as outputFile:
		for line in input:

			content = line
			lineNumber += 1
			#print ("line = {}, lineNumber = {} and endLine = {}".format(line, lineNumber, endLine))
			if lineNumber == enter_instrument:
				#if content.isspace() == True or chomp(content)[-1] == ';' :
					#print ("last character in line = {}".format(line[-2]))
				outputFile.write('printf("INSTRUMENTATION_TOOL::Entered into file %s: in function %s, at line number %d \\n", __FILE__, __func__, __LINE__);\n')
				outputFile.write(content);
			elif lineNumber == exit_instrument:
				#print (content)
				outputFile.write(content);
				outputFile.write('printf("INSTRUMENTATION_TOOL::Exiting function %s, at line number %d from file %s \\n", __func__, __LINE__, __FILE__);\n')
			else:
				#print (content)
				outputFile.write(content);

	post_instrumentation_fileops(inputFile, readinFile, resultFile)

	return



def deep_file_instrument(fileName="Do_Not_Know",startLine=0, endLine='EOF'):
	
	lineNumber = 0	
	line_offset = []

	readinFile, resultFile = create_outputfile(fileName)
	print resultFile


	# First pass only if we don't know the end point for processing this instrumentation
	if endLine == 'EOF':
		# To collect a start point of first function
		cmd = "ctags -x --c-kinds=f " + fileName + " | awk '{ print $3 }'"
		lineNumberList = subprocess.check_output(cmd, shell=True).split('\n')
		startLine = min(lineNumberList)
		if startLine == '':
			lineNumberList.remove(startLine)
		startLine = min(lineNumberList)
		with open(fileName,'r') as inputFile:
			#To process EOF we have to read the file once any way so building a 
			#line_offset data structure out of entire file
			offset = 0
			for line in inputFile:
			    line_offset.append(offset)
			    offset += len(line)
			inputFile.seek(0)
		endLine = line_offset[-1]



	with open(readinFile,'r') as inputFile, open(resultFile, 'a+') as outputFile:
		for line in inputFile:

			content = line
			lineNumber += 1
			#print ("line = {}, lineNumber = {}, startLine = {} and endLine = {}".format(line, lineNumber, startLine, endLine))
			if int(lineNumber) > int(startLine) and int(lineNumber) <= int(endLine):
				#print ("came in instrumentation block");
				if content.isspace() != True and chomp(content)[-1] == ';' :
					#print ("last character in line = {}".format(line[-1]))
					outputFile.write('printf("INSTRUMENTATION_TOOL::In file %s: in function %s, at line number %d \\n", __FILE__, __func__, __LINE__);\n')
					outputFile.write(content);
				else:
					#print (content)
					outputFile.write(content);
			else:
				#print (content)
				outputFile.write(content);

	post_instrumentation_fileops(fileName, readinFile, resultFile)

	return




def shallow_file_instrument(fileName="Do_Not_Know",startLine=0, endLine='EOF'):
	#get all the function names and line numbers for a given file
	#ctags -x --c-kinds=f readtags.c
	cmd = "ctags -x --c-kinds=f " + fileName + " | awk '{ print $1 }'"
	functionNameList = subprocess.check_output(cmd, shell=True).split('\n')
	cmd = "ctags -x --c-kinds=f " + fileName + " | awk '{ print $3 }'"
	lineNumberList = subprocess.check_output(cmd, shell=True).split('\n')
	lineNumberList.remove('')
	lineNumberList = map(int, lineNumberList)
	#print 'INSTRU-DEBUG:: functionNameList = {} and lineNumberList = {} '.format(functionNameList, lineNumberList)
	if not functionNameList or not lineNumberList:
		#Write an entry in a result log that this file was not processed
		return 

	#This is for output file
	readinFile, resultFile = create_outputfile(fileName)
	print resultFile

	lineNumber = 0	

	sorted_function_list = sorted(zip(lineNumberList, functionNameList))
	element = 0
	current_item =	sorted_function_list[element]	
	#print current_item
	#print sorted_function_list
	if current_item[0] == '':
		element += 1
		current_item =	sorted_function_list[element]	
	startLine, endLine = find_function_body(fileName,current_item[1])
	print 'MIHIR-DEBUG:: does it come here?'
	if chomp(startLine) == '' or chomp(endLine) == '':
		print 'came in endline is empty block'
		if len(sorted_function_list) > (element+1):
			#Add entry in a file showing this file has issue		
			element += 1
			current_item =	sorted_function_list[element]	
			startLine, endLine = find_function_body(fileName,current_item[1])
		else:
			#Add entry in a file showing this file has issue		
			return
	enter_instrument = int(startLine) + 1
	exit_instrument = int(endLine) 
	#if (int(startLine) + 2) < (int(endLine) -1) :
	#	exit_instrument = int(endLine) - 1
	#else:
	#	exit_instrument = int(endLine) 
	print 'INSTRU-DEBUG:: function {}, startLine = {}, endLine = {}, enter_instrument = {} and exit_instrument = {}'.format(current_item[1], startLine[:-1], endLine[:-1], enter_instrument, exit_instrument)
	inputFile = fileName
	with open(readinFile,'r') as input, open(resultFile, 'a+') as outputFile:
		input.seek(0)
		for line in input:
			#print 'INSTRU-DEBUG:: function {}, startLine = {}, endLine = {}, enter_instrument = {} and exit_instrument = {}'.format(current_item[1], startLine[:-1], endLine[:-1], enter_instrument, exit_instrument)
			content = line
			lineNumber += 1
			#print ("line = {}, lineNumber = {} and endLine = {}".format(line, lineNumber, endLine))
			if lineNumber == enter_instrument:
				outputFile.write('printf("INSTRUMENTATION_TOOL::Entered into file %s: in function %s, at line number %d \\n", __FILE__, __func__, __LINE__);\n')
				outputFile.write(content);
			elif lineNumber == exit_instrument:
				#print (content)
				# A case where a line above } is return statement
				if content.isspace() == False and ( content.split()[0] == 'return' or content.split()[0] == 'return;' ) :
						outputFile.write('printf("INSTRUMENTATION_TOOL::Exiting function %s, at line number %d from file %s \\n", __func__, __LINE__, __FILE__);\n')
						outputFile.write(content);
				else: # A case where a line above } is not a return statement
					outputFile.write('printf("INSTRUMENTATION_TOOL::Exiting function %s, at line number %d from file %s \\n", __func__, __LINE__, __FILE__);\n')
					outputFile.write(content);
					if element < len(sorted_function_list) - 1 :
						element += 1
						current_item =	sorted_function_list[element]	
						#print 'INSTRU-DEBUG:: functionName = ', current_item[1]
						startLine, endLine = find_function_body(fileName,current_item[1])
						if chomp(startLine) == '' or chomp(endLine) == '':
							print 'does it come here??'
							if len(sorted_function_list) > (element+1):
								#Add entry in a file showing this file has issue		
								element += 1
								current_item =	sorted_function_list[element]	
								startLine, endLine = find_function_body(fileName,current_item[1])
							else:
								#Add entry in a file showing this file has issue		
								return
						enter_instrument = int(startLine) + 1
						exit_instrument = int(endLine) 

			else:
				if content.isspace() == False and ( content.split()[0] == 'return' or content.split()[0] == 'return;' ) :
						outputFile.write('printf("INSTRUMENTATION_TOOL::Exiting function %s, at line number %d from file %s \\n", __func__, __LINE__, __FILE__);\n')
						outputFile.write(content);
				else:
					#print (content)
					outputFile.write(content);

	print 'INSTRU-DEBUG:: filename = {}, readinFile = {}, resultFile = {}'.format(fileName, readinFile, resultFile)
	post_instrumentation_fileops(fileName, readinFile, resultFile)

	return


def deep_function_instrument(inputFile="Do_Not_Know",functionName="some_function"):
	if add_func(functionName,'deep') == True:
		return

	startLine, endLine= find_function_body(inputFile,functionName)

	deep_file_instrument(inputFile, startLine, endLine)

	return




if __name__ == '__main__':
		#deep_file_instrument('test.c')
		#deep_function_instrument('test.c','display_tree')
		#shallow_file_instrument('test.c')
		#shallow_function_instrument('test.c','main')
		find_function_for_message('test.c',message='Address OF')