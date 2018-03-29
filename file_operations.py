#/usr/bin/python
import os
import glob
import datetime
from shutil import copyfile
import time



def chomp(x):
  if x.endswith("\r\n"): return x[:-2]
  if x.endswith("\n"): return x[:-1]
  return x


def create_outputfile (inputFile="somefile"):
	backup = str(inputFile) + '.orig'
	#we have to handle this later
	if os.path.exists(backup):
		pass
	else:
		filename,extension = inputFile.split('.')
		searchname=filename + '_*.' + extension
		glob.glob(searchname)
		pass

	copyfile(inputFile, backup)
	n = datetime.datetime.now()                                                                                                                                                                                                                                                                                       
	unix_time = int( time.mktime(n.timetuple()) )
	filename, extension = inputFile.split('.')
	#outputFile = filename +'_' + str(unix_time) + '.' + extension
	#print outputFile
	return filename +'_' + str(unix_time) + '.' + extension



def list_all_files (location='pwd'):
	all_files = []
	if location == 'pwd':
		directory= os.getcwd()
	else:
		directory = location

	for root, dirs, files in os.walk(directory):
	  for file in files:
	    if file.endswith(".c"):
	      #print(os.path.join(root, file))
	      all_files.append(os.path.join(root, file))

	return all_files


if __name__ == '__main__':
	list_all_files('/home/parallels/Downloads/ctags-5.8')