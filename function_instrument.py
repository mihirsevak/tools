#!/usr/bin/python
import subprocess

def chomp(x):
  if x.endswith("\r\n"): return x[:-2]
  if x.endswith("\n"): return x[:-1]
  return x


def find_function_body(inputFile="Do_Not_Know",functionName="some_function"):
	#filename="/home/parallels/Downloads/ctags-5.8/readtags.c"
	cmd = "ctags -x --c-kinds=f " + filename + " | grep " + functionName +" | awk '{ print $3 }'"
	beginning_line = subprocess.check_output(cmd, shell=True)
	#print beginning_line
	cmd = "awk -v s=" + chomp(beginning_line) + "  'NR>=s && /{/              {c++} NR>=s && /}/ && c && !--c {print NR; exit}' " + filename
	ending_line = subprocess.check_output(cmd,shell=True)
	#print ending_line
	return (beginning_line, ending_line)



def shallow_function_instrument(inputFile="Do_Not_Know",functionName="some_function"):
	# Write to a global datastructure that this function is instrumented
	if functionName in shallow_instrumented:
		return
	else:
		shallow_instrumented[functionName] == True

	startLine, endLine = find_function_body(inputFile,functionName)
	enter_instrument = startLine + 2
	exit_instrument = endLine - 1
	
	#First pass to build line offset list
	lineNumber = 0	
	line_offset = []

	offset = 0
	for line in inputFile:
	    line_offset.append(offset)
	    offset += len(line)
	inputFile.seek(0)
	endLine = line_offset[-1]

	#This is for output file
	resultFile = create_outputfile(fileName)
	print resultFile


	with open(fileName,'r') as inputFile, open(resultFile, 'a+') as outputFile:
		for line in inputFile:

			content = line
			lineNumber += 1
			print ("line = {}, lineNumber = {} and endLine = {}".format(line, lineNumber, endLine))
			if lineNumber == enter_instrument:
				if content.isspace() != True or content[-2] == ';' :
					#print ("last character in line = {}".format(line[-2]))
                    outputFile.write('printf("INSTRUMENTATION_TOOL::Entered into file %s: in function %s, at line number %d \\n", __FILE__, __func__, __LINE__);\n')
					outputFile.write(content);
			elif lineNumber == exit_instrument:
					print (content)
					outputFile.write(content);
                    outputFile.write('printf("INSTRUMENTATION_TOOL::Exiting function %s, at line number %d from file %s \\n", __func__, __LINE__, __FILE__);\n')
			else:
				print (content)
				outputFile.write(content);

		return



def deep_function_instrument(inputFile="Do_Not_Know",functionName="some_function"):
	# Write to a global datastructure that this function is instrumented
	if functionName in deep_instrumented:
		return
	else:
		deep_instrumented[functionName] == True

	startLine, endLine= find_function_body(inputFile,functionName)

	deep_file_instrument(inputFile, startLine, endLine)

	return



if __name__ == '__main__':
	shallow_instrument()