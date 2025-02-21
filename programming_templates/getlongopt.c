#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
#include <ctype.h>

/* Flag set by ‘--verbose’. */
static int verbose_flag;

enum PROTOCOL { TCP=0, UDP, ARP, ICMP };

enum RULE { ACCEPT=0, DROP, FORWARD };

typedef struct header_info {
	unsigned int srcIp;
	unsigned int destIp;
	int srcPort;
	int destPort;
	enum PROTOCOL protocol;
	enum RULE rule;
}HEADER_INFO;

void to_uppercase(char *str) {
    for (int i = 0; str[i] != '\0'; i++) {
        str[i] = toupper(str[i]);
    }
}

int parse_ip(HEADER_INFO* ruleHeader, char * ipAddress, int srcIp)
{
    unsigned int ip_parts[4];
    unsigned int ip_hex;

    if (sscanf(ipAddress, "%u.%u.%u.%u", &ip_parts[0], &ip_parts[1], &ip_parts[2], &ip_parts[3]) != 4) {
        printf("Invalid IP address format.\n");
        return 1;
    }

    ip_hex = (ip_parts[0] << 24) | (ip_parts[1] << 16) | (ip_parts[2] << 8) | ip_parts[3];

    //printf("The IP address in hexadecimal is: %08X\n", ip_hex);

	if (srcIp)
		ruleHeader->srcIp=ip_hex;
	else
		ruleHeader->destIp=ip_hex;

	return 0;
}

int
main (int argc, char **argv)
{
  int c;
  HEADER_INFO ruleHeader;
  char* ipAddress;
  char* protocol_value;
  char* action_value;

  while (1)
    {
      static struct option long_options[] =
        {
          /* These options set a flag. */
          {"verbose", no_argument,       &verbose_flag, 1},
          {"brief",   no_argument,       &verbose_flag, 0},
          /* These options don’t set a flag.
             We distinguish them by their indices. */
          //{"srcport",     no_argument,       0, 'a'},
          {"srcport",  required_argument,       0, 'a'},
          {"destport",  required_argument,       0, 'b'},
          {"srcip",  required_argument, 0, 's'},
          {"destip",  required_argument, 0, 'd'},
          {"protocol",  required_argument, 0, 'p'},
          {"query",  required_argument, 0, 'q'},
          {"rule",  required_argument, 0, 'r'},
          {"file",    optional_argument, 0, 'f'},
          {0, 0, 0, 0}
        };
      /* getopt_long stores the option index here. */
      int option_index = 0;

      c = getopt_long (argc, argv, "a:b:s:d:p:r:f:",
                       long_options, &option_index);

      /* Detect the end of the options. */
      if (c == -1)
        break;

      switch (c)
        {
        case 0:
          /* If this option set a flag, do nothing else now. */
          if (long_options[option_index].flag != 0)
            break;
          printf ("option %s", long_options[option_index].name);
          if (optarg)
            printf (" with arg %s", optarg);
          printf ("\n");
          break;

        case 'a':
          //printf ("option -a(srcport) with value `%s'\n", optarg);
		  if(optarg == "*") {
			ruleHeader.srcPort = 0;
		  } else {
			  unsigned int port;
		  	  sscanf(optarg,"%u", &port);
			  ruleHeader.srcPort = port;
		  }
          break;

        case 'b':
          //printf ("option -b(destport) with value `%s'\n", optarg);
		  if(optarg == "*") {
			ruleHeader.srcPort = 0;
		  } else {
			  unsigned int port;
		  	  sscanf(optarg,"%u", &port);
			  ruleHeader.destPort = port;
		  }
          break;

        case 's':
          //printf ("option -s(srcip) with value `%s'\n", optarg);
		  ipAddress = optarg;
		  parse_ip(&ruleHeader, ipAddress, 1);
		  //printf("ruleHeader.srcIP = %08X\n",ruleHeader.srcIp);
          break;

        case 'd':
          //printf ("option -d(destip) with value `%s'\n", optarg);
		  ipAddress = optarg;
		  parse_ip(&ruleHeader, ipAddress, 0);
		  //printf("ruleHeader.destIP = %08X\n",ruleHeader.destIp);
          break;

        case 'p':
          //printf ("option -p(protocol) with value `%s'\n", optarg);
		  protocol_value = optarg;
		  to_uppercase(protocol_value);
		  //printf("protocol value = %s\n", protocol_value);
		  if (strncmp(protocol_value,"TCP",(long unsigned int)3) == 0) {
			  //printf("came in TCP\n");
			  ruleHeader.protocol = TCP;
		  } else if (strncmp(protocol_value,"UDP",(long unsigned int)3) == 0) {
			  //printf("came in UDP\n");
			  ruleHeader.protocol = UDP;
		  } else {
			  printf("unknown protocol\n");
		  }
          break;

        case 'q':
          printf ("option -q(query) with value `%s'\n", optarg);
          break;

        case 'r':
          //printf ("option -r(rule) with value `%s'\n", optarg);
    	  action_value = optarg;
		  to_uppercase(action_value);
		  //printf("rule value = %s\n", action_value);
		  if (strncmp(action_value,"DROP",(long unsigned int)4) == 0) {
			  //printf("came in DROP\n");
			  ruleHeader.rule = DROP;
		  } else if (strncmp(action_value,"ACCEPT",(long unsigned int)6) == 0) {
			  //printf("came in ACCEPT\n");
			  ruleHeader.rule = ACCEPT;
		  } else if (strncmp(action_value,"FORWARD",(long unsigned int)7) == 0) {
			  //printf("came in FORWARD\n");
			  ruleHeader.rule = FORWARD;
		  } else {
			  printf("Unkonwn action(rule)\n");
		  }
         break;

        case 'f':
          //printf ("option -f(file) with value `%s'\n", optarg);
          break;

        case '?':
          /* getopt_long already printed an error message. */
          break;

        default:
          abort ();
        }
    }

  /* Instead of reporting ‘--verbose’
     and ‘--brief’ as they are encountered,
     we report the final status resulting from them. */
  if (verbose_flag)
    puts ("verbose flag is set");

  /* Print any remaining command line arguments (not options). */
  if (optind < argc)
    {
      printf ("non-option ARGV-elements: ");
      while (optind < argc)
        printf ("%s ", argv[optind++]);
      putchar ('\n');
    }

   printf("ruleHeader.srcIp = %08X\n", ruleHeader.srcIp);
   printf("ruleHeader.destIp = %08X\n", ruleHeader.destIp);
   printf("ruleHeader.srcPort = %d\n", ruleHeader.srcPort);
   printf("ruleHeader.destPort = %d\n", ruleHeader.destPort);
   printf("ruleHeader.protocol = %d\n", ruleHeader.protocol);
   printf("ruleHeader.rule = %d\n", ruleHeader.rule);

  exit (0);
}
