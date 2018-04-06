#/usr/bin/python
import glob
import datetime
import subprocess
from shutil import copyfile, move
import time
from os import listdir,rename, symlink, readlink, unlink, getcwd, remove, walk
from os.path import isfile, join, islink, exists



def chomp(x):
  if x.endswith("\r\n"): return x[:-2]
  if x.endswith("\n"): return x[:-1]
  return x

'''
We want to create one backup file and only one instrumentation file.
if instrumetation file exists then we use instrumentaed file as an 
input otherwise we use original file as an input
'''
def create_outputfile (inputFile="somefile"):
	print 'INSTRU-DEBUG:: filename = ', inputFile
	backup = str(inputFile) + '.orig'
	# To preserve prestine copy of file all the time
	if not exists(backup):
		copyfile(inputFile, backup)
	try:
		filename,extension = inputFile.split('.')
	except:
		#following has to be tested for other types of files like java, ruby etc.
		extension = inputFile.split('.')[-1]
		filename = '.'.join(inputFile.split('.')[:-1])
	instrumented = filename + '_instru.' + extension  
	readinFile = inputFile
	resultFile = instrumented
	#we have to handle this later
	if exists(backup) :
		if exists(instrumented) :
			readinFile = instrumented
			resultFile = filename + '_instru_1.'+extension
	else:
		readinFile = inputFile
		resultFile = filename + '_instru.'+extension

	return (readinFile, resultFile)



'''
After that we want to link the instrumentated file or backup or original
file as the actual file.
'''
def post_instrumentation_fileops(originalFile, readinFile, resultFile ):
	backup = str(originalFile) + '.orig'
	try:
		filename,extension = originalFile.split('.')
	except:
		#following has to be tested for other types of files like java, ruby etc.
		extension = originalFile.split('.')[-1]
		filename = '.'.join(originalFile.split('.')[:-1])
	instrumented = filename + '_instru.' + extension  
	if str(resultFile) != instrumented:
		rename(resultFile,instrumented)
	if not exists (backup):
		rename(originalFile, backup)

	if exists(originalFile):
		newName = str(originalFile) + '.bkp'
		move(originalFile, newName)
		#symlink(instrumented, originalFile)
		if getcwd() not in str(instrumented): 
			INSTRUMENTED_PATH=getcwd()+'/'+str(instrumented)
		else:
			INSTRUMENTED_PATH=str(instrumented)
		if getcwd() not in str(originalFile): 
			ORIGINAL_PATH=getcwd()+'/'+str(originalFile)
		else:
			ORIGINAL_PATH=str(originalFile)
		#print 'instrumented_path = {} and original_path = {}'.format(INSTRUMENTED_PATH, ORIGINAL_PATH)
		symlink(INSTRUMENTED_PATH, ORIGINAL_PATH)
	return

'''
	searchname=filename + '_instru.' + extension
	glob.glob(searchname)
	pass

	copyfile(inputFile, backup)
	n = datetime.datetime.now()                                                                                                                                                                                                                                                                                       
	unix_time = int( time.mktime(n.timetuple()) )
	filename, extension = inputFile.split('.')
	#outputFile = filename +'_' + str(unix_time) + '.' + extension
	#print outputFile

	return filename +'_' + str(unix_time) + '.' + extension
'''

def list_all_files (location='pwd'):
	print 'came in list_all_files function'
	all_files = []
	if location == 'pwd':
		directory= getcwd()
	else:
		directory = location

	print directory
	for root, dirs, files in walk(directory):
	  for file in files:
	    if file.endswith(".c"):
	      print(join(root, file))
	      all_files.append(join(root, file))
	      #print(file)
	      #all_files.append(file)

	return all_files


def restore_original(fileName):
	originalFile = fileName + '.orig'
	print originalFile
	if exists(originalFile):
		unlink(fileName)
		copyfile(originalFile,fileName)
	return


def restore_all_original(location='pwd'):
	all_files = []
	if location == 'pwd':
		directory= getcwd()
	else:
		directory = location
	
	onlylinks = [f for f in listdir(directory) if islink(join(directory, f))]
	for file in onlylinks:
		restore_original(file)


def remove_instru(fileName):
	filename,extension = fileName.split('.')
	originalFile = fileName + '.orig'
	instrumented = filename + '_instru.' + extension  
	if exists (instrumented) :
		if islink(fileName) and readlink(fileName) == str(instrumented) :
			unlink(fileName)
			copyfile(originalFile,fileName)
		remove(instrumented)	
	return


def remove_all_instru(location='pwd'):
	current_directory = getcwd()
	if location != 'pwd':
		directory = location
		chdir(directory)
	else:
		directory = getcwd()
	all_files = []
	all_files += [each for each in listdir(directory) if each.endswith('.c')]
	for file in all_files:
		cleanup_instru(file)


def cleanup(fileName='somefile',location='pwd') :
	'''
	1) if it is just a file restore original file 
	2) remove .orig file related to file
	3) remove instru files related to file

	if it is a whole directory -- 
	1) get all the files in a directory and repeat the above listed process 
	'''
	if fileName != 'somefile' :
		restore_original(fileName)
		remove_instru(fileName)
		origFileName = str(fileName) + '.orig'
		remove(origFileName)
	if location != 'pwd' :
		all_files = list_all_files(location)
		for file in all_files:
			restore_original(fileName)
			remove_instru(fileName)
			origFileName = str(fileName) + '.orig'
			remove(origFileName)

	return	

def script_cleanup(fileName):
	cmd = "clean.sh "+ fileName
	result = subprocess.call(cmd, shell=True)
	if result == '0':
		return;
	else:
		#Throw some exception and get out
		pass

	return 


if __name__ == '__main__':
	print 'came in file_operations.py script'
	print list_all_files(location='pwd')
	print 'just called list_all_files function'
	#print create_outputfile('test.c')
	#print post_instrumentation_fileops('test.c', 'test_instru.c','test_instru_1.c')
	#print post_instrumentation_fileops('test.c', 'test.c','test_instru.c')
	#restore_original('test.c')
	#print remove_all_instru()
