#include <iostream>
#include <string>
//#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <unistd.h>
#include <stdbool.h>

using namespace std;

int main(int argc, char **argv) {

    int opt;
    char *ifile, *ofile;  
    bool verbose = false;
	bool batch = false;
	string batchfile;

    // Long option definitions         
    struct option long_options[] = {
        {"verbose", no_argument, NULL, 'v'},
        {"input", required_argument, NULL, 'i'},
        {"output", required_argument, NULL, 'o'},
        {"batch", optional_argument, NULL, 'b'},
        {NULL, 0, NULL, 0}};


    // Long option parsing
    while((opt = getopt_long(argc, argv, "vi:o:b:", 
                    long_options, NULL)) != -1) {

        switch(opt) {
            case 'v':
                verbose = true;
                break;

            case 'i':
                ifile = optarg;
                break;

            case 'b':
                batchfile = optarg;
				batch = true;
                break;

            case 'o': 
                ofile = optarg;
                break;              
        }
    }

	cout << "Input file = " << ifile << " and output file = " << ofile << endl;
	cout << "Batch file = " << batchfile << endl;
    // Rest of logic

	if (optind < argc)
    {
      printf ("non-option ARGV-elements: ");
      while (optind < argc)
        printf ("%s ", argv[optind++]);
      putchar ('\n');
    }

    //copyFile(ifile, ofile, verbose);  

    return 0;
}
