#!/usr/bin/python

import sys
import subprocess
import glob
import time
import os.path
#from fresh_main import shallow_instrumented, deep_instrumented
from file_operations import create_outputfile, post_instrumentation_fileops, chomp
from collections import OrderedDict




def find_function_body(inputFile="Do_Not_Know",functionName="some_function"):
	#filename="/home/parallels/Downloads/ctags-5.8/readtags.c"
	cmd = "ctags -x --c-kinds=f " + inputFile + " | grep " + functionName +" | awk '{ print $3 }'"
	beginning_line = subprocess.check_output(cmd, shell=True)
	#print beginning_line
	cmd = "awk -v s=" + chomp(beginning_line) + "  'NR>=s && /{/              {c++} NR>=s && /}/ && c && !--c {print NR; exit}' " + inputFile
	ending_line = subprocess.check_output(cmd,shell=True)
	#print ending_line
	return (beginning_line, ending_line)



def shallow_function_instrument(inputFile="Do_Not_Know",functionName="some_function"):
	# TODO: Write to a global datastructure that this function is instrumented
	#if functionName in shallow_instrumented:
	#	return
	#else:
	#	shallow_instrumented[functionName] 
	#print functionName

	startLine, endLine = find_function_body(inputFile,functionName)
	enter_instrument = int(startLine) + 2
	exit_instrument = int(endLine) - 1
	
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
	#print functionNameList

	#This is for output file
	readinFile, resultFile = create_outputfile(fileName)
	print resultFile

	lineNumber = 0	

	sorted_function_list = sorted(zip(lineNumberList, functionNameList))
	element = 0
	current_item =	sorted_function_list[element]	
	if current_item[0] == '':
		element += 1
		current_item =	sorted_function_list[element]	
	startLine, endLine = find_function_body(fileName,current_item[1])
	enter_instrument = int(startLine) + 2
	exit_instrument = int(endLine) - 1
	inputFile = fileName
	with open(readinFile,'r') as input, open(resultFile, 'a+') as outputFile:
		input.seek(0)
		for line in input:
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
					outputFile.write(content);
					outputFile.write('printf("INSTRUMENTATION_TOOL::Exiting function %s, at line number %d from file %s \\n", __func__, __LINE__, __FILE__);\n')
					if element < len(sorted_function_list) - 1 :
						element += 1
						current_item =	sorted_function_list[element]	
						startLine, endLine = find_function_body(fileName,current_item[1])
						enter_instrument = int(startLine) + 2
						exit_instrument = int(endLine) - 1

			else:
				if content.isspace() == False and ( content.split()[0] == 'return' or content.split()[0] == 'return;' ) :
						outputFile.write('printf("INSTRUMENTATION_TOOL::Exiting function %s, at line number %d from file %s \\n", __func__, __LINE__, __FILE__);\n')
						outputFile.write(content);
				else:
					#print (content)
					outputFile.write(content);

	post_instrumentation_fileops(fileName, readinFile, resultFile)

	return


def deep_function_instrument(inputFile="Do_Not_Know",functionName="some_function"):
	# TODO: Write to a global datastructure that this function is instrumented
	#if functionName in deep_instrumented:
	#	return
	#else:
	#	deep_instrumented[functionName] == True
	startLine, endLine= find_function_body(inputFile,functionName)

	deep_file_instrument(inputFile, startLine, endLine)

	return




if __name__ == '__main__':
		#deep_file_instrument('test.c')
		#deep_function_instrument('test.c','display_tree')
		shallow_file_instrument('test.c')
		#shallow_function_instrument('test.c','main')