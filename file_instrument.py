#!/usr/bin/python
import sys
from shutil import copyfile
import time
import datetime
import os.path
import glob
import subprocess



def deep_file_instrument(fileName="Do_Not_Know",startLine=0, endLine='EOF'):
	
	lineNumber = 0	
	line_offset = []

	resultFile = create_outputfile(fileName)
	print resultFile


	# First pass only if we don't know the end point for processing this instrumentation

	if endLine == 'EOF':
		#To process EOF we have to read the file once any way so building a 
		#line_offset data structure out of entire file
		offset = 0
		for line in inputFile:
		    line_offset.append(offset)
		    offset += len(line)
		inputFile.seek(0)
		endLine = line_offset[-1]



	with open(fileName,'r') as inputFile, open(resultFile, 'a+') as outputFile:
		for line in inputFile:

			content = line
			lineNumber += 1
			print ("line = {}, lineNumber = {} and endLine = {}".format(line, lineNumber, endLine))
			if lineNumber > startLine and lineNumber <= endLine:
				if content.isspace() != True and content[-2] == ';' :
					#print ("last character in line = {}".format(line[-2]))
                                        outputFile.write('printf("In file %s: in function %s, at line number %d \\n", __FILE__, __func__, __LINE__);\n')
					outputFile.write(content);
				else:
					print (content)
					outputFile.write(content);
			else:
				print (content)
				outputFile.write(content);

		return


def shallow_file_instrument(fileName="Do_Not_Know",startLine=0, endLine='EOF'):
	#get all the function names and line numbers for a given file
	#ctags -x --c-kinds=f readtags.c
	cmd = "ctags -x --c-kinds=f " + fileName + " | awk '{ print $1 }'"
	functionNameList = subprocess.check_output(cmd, shell=True)
	for functionName in functionNameList:
		shallow_function_instrument(fileName,functionName):
	return


if __name__ == '__main__':
	# if len(sys.argv) == 4:
	# 	print ("filename = {}, startLine = {}, endLine = {}".format(sys.argv[1], sys.argv[2], sys.argv[3]) )
	# 	deep_file_instrument(str(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) )
	# elif len(sys.argv) == 3:
	# 	print ("filename = {}, startLine = {}".format(sys.argv[1], sys.argv[2]) )
	# 	deep_file_instrument(str(sys.argv[1]), int(sys.argv[2]) )
	# elif len(sys.argv) == 2:
	# 	print ("filename = {}".format(sys.argv[1]) )
	# 	deep_file_instrument(str(sys.argv[1]) )
	shallow_file_instrument("/home/parallels/Downloads/ctags-5.8/readtags.c")	




