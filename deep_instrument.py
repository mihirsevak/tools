#!/usr/bin/python
import sys
from shutil import copyfile
import time
import datetime
import os.path

def create_outputfile (inputFile="somefile"):
	backup = str(inputFile) + '.orig'
	#we have to handle this later
	if os.path.exists(backup):
		pass
	else:
		pass

	copyfile(inputFile, backup)
	n = datetime.datetime.now()                                                                                                                                                                                                                                                                                       
	unix_time = int( time.mktime(n.timetuple()) )
	filename, extension = inputFile.split('.')
	#outputFile = filename +'_' + str(unix_time) + '.' + extension
	#print outputFile
	return filename +'_' + str(unix_time) + '.' + extension

def deep_instrument(fileName="Do_Not_Know",startLine=0, endLine='EOF'):
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
					outputFile.write('printf("In file %s at line number %d \\n", __FILE__, __LINE__);\n')
					outputFile.write(content);
				else:
					print (content)
					outputFile.write(content);
			else:
				print (content)
				outputFile.write(content);

		return



if __name__ == '__main__':
	if len(sys.argv) == 4:
		print ("filename = {}, startLine = {}, endLine = {}".format(sys.argv[1], sys.argv[2], sys.argv[3]) )
		deep_instrument(str(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) )
	elif len(sys.argv) == 3:
		print ("filename = {}, startLine = {}".format(sys.argv[1], sys.argv[2]) )
		deep_instrument(str(sys.argv[1]), int(sys.argv[2]) )
	elif len(sys.argv) == 2:
		print ("filename = {}".format(sys.argv[1]) )
		deep_instrument(str(sys.argv[1]) )
		



