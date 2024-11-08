#include <iostream>
#include <vector>
#include <string>
#include <stdlib.h>
#include <getopt.h>
#include <unistd.h>
#include <stdbool.h>
#include <ctime>
#include <fstream>

using namespace std;

// Function to find the PID of a process
int find_pid(const char* process_name) {
    FILE* fp;
    char command[100];
    char pid_str[10];

    // Construct the command to search for the process
    snprintf(command, sizeof(command), "pgrep %s", process_name);

    // Execute the command and read the output
    fp = popen(command, "r");
    if (fp == NULL) {
        perror("Error executing command");
        return -1;
    }

    // Read the PID from the output
    if (fgets(pid_str, sizeof(pid_str), fp) != NULL) {
        pclose(fp);
        return atoi(pid_str);
    }

    pclose(fp);
    return -1; // Process not found
}

string log_memory(int pidVal)
{
    FILE* fp;
    char memory_str[100];
	
	//string cmd = "cat /proc/" + to_string(pidVal) + "/smaps | grep -i pss |  awk '{Total+=$2} END {print Total/1024/1024\" GB\"}'";
	string cmd = "cat /proc/self/smaps | grep -i pss |  awk '{Total+=$2} END {print Total/1024/1024\" GB\"}'";
	//cout << "Command to run = " << cmd << endl;

    // Execute the command and read the output
    fp = popen(cmd.c_str(), "r");
    if (fp == NULL) {
        perror("Error executing command");
        return "ERROR_TO_RUN_CMD";
    }

    // Read the memory from the output
    if (fgets(memory_str, sizeof(memory_str), fp) != NULL) {
        pclose(fp);
        return memory_str;
    }

	return "ERROR";
}

void print_help()
{
	cout << "This program can take process name to dump its memory" << endl;
	cout << "consumption or processID to dump its consumption." << endl;
	cout << "USAGE: memlogger -p <pid> " << endl;
	cout << "    or memlogger <processname>  " << endl;

	cout << "By default this program creates a logfile ProcessMemoryConsumption.log." << endl;
	cout << "You can override it by passing an argument. -l" << endl;
	exit(0);
}

/* Questions:
*
* 1) What if there are multiple instances of the same process? Decided we will come back and question which pid are we monitoring?
* 2) Do we add timestamp for each time?  Decided yes.
* 3) Do we want to create a deamon or offload it to cron or at? Decided to do Just-In-Time logging
* 4) Do we put memory consumption in bytes, MBs or GBs?
* 5) How do we know which processes are we monitoring? We should run this in stand-alone mode or batch mode. Batch mode will read an inputfile
* 6) Do we want to take just names or pids? Decided both parst with commandline options
*
*/

int main(int argc, char **argv)
{
	//const char* process_name = "python3"; // Change this to the desired process name
    int opt;
    bool isLogFile = false;
	bool isBatch = false;
	bool isPid = false;
	bool isOutput = false;
	string batchfile;
	string process_name;
    string pid;  
	string outputFileName;
	time_t rawtime;
  	struct tm * timeinfo;
  	char buffer[80];
	ofstream LogFile;


    // Long option definitions         
    struct option long_options[] = {
        {"help", no_argument, NULL, 'h'},
        {"self", no_argument, NULL, 's'},
        {"logfile", required_argument, NULL, 'l'},
        {"pid", optional_argument, NULL, 'p'},
        {NULL, 0, NULL, 0}};


    // Long option parsing
    while((opt = getopt_long(argc, argv, "hsl:p:", 
                    long_options, NULL)) != -1) {

        switch(opt) {
			case 'h':
				print_help();
				break;

			case 's':
				print_help();
				break;

            case 'l':
                isLogFile = true;
                outputFileName = optarg;
                break;

            case 'b':
                batchfile = optarg;
				isBatch = true;
                break;

            case 'p':
			    isPid = true;	
                pid = optarg;
                break;              
        }
    }

    int pidVal = -1;
	if ( (optind < argc) && (isPid == false) )
    {
      
      while (optind < argc) {
		process_name = argv[optind++];
		//cout <<"non-option ARGV-elements: " << process_name <<endl;
		pidVal = find_pid(process_name.c_str());
	  }
    } else if (isPid == true) {
		pidVal = stoi(pid);
	}

	if (isBatch)
		cout << "Batch file = " << batchfile << endl;
   

    if (pidVal != -1) {
		string used_memory=log_memory(pidVal);
  		time (&rawtime);
  		timeinfo = localtime(&rawtime);
  		strftime(buffer,sizeof(buffer),"%d-%m-%Y %H:%M:%S",timeinfo);
  		string timestamp(buffer);
  		//std::cout << timestamp;


		if (isLogFile)
			LogFile.open(outputFileName, std::ios_base::app);
		else
			LogFile.open("ProcessMemoryConsumption.log", std::ios_base::app);

		if (isPid) {
			LogFile << timestamp << " Process ID : " << pidVal << " Memory Consumption: " << used_memory;
			cout << timestamp << " Process ID : " << pidVal << " Memory Consumption: " << used_memory;
		} else {
			LogFile << timestamp << " Process Name: " << process_name << " Memory Consumption: " << used_memory;
			cout << timestamp << " Process Name: " << process_name << " Memory Consumption: " << used_memory;
		}

    } else {
		cout << "Process " << process_name << " is not running." << endl;
    }

	return 0;
}

