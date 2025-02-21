#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>
#include <unistd.h>

#define CHILDREN 2  // Binary Trie for IP addresses

typedef struct TrieNode {
    struct TrieNode *children[CHILDREN];
    bool isEndOfIP;
    int port;  // Store the port number
} TrieNode;

TrieNode* createNode() {
    TrieNode *node = (TrieNode *)malloc(sizeof(TrieNode));
    node->isEndOfIP = false;
    node->port = -1;  // Initialize port to an invalid value
    for (int i = 0; i < CHILDREN; i++) {
        node->children[i] = NULL;
    }
    return node;
}

void insert(TrieNode *root, unsigned int ip, int port) {
    TrieNode *node = root;
    for (int i = 31; i >= 0; i--) {
        int bit = (ip >> i) & 1;
        if (!node->children[bit]) {
            node->children[bit] = createNode();
        }
        node = node->children[bit];
    }
    node->isEndOfIP = true;
    node->port = port;
}

int search(TrieNode *root, unsigned int ip) {
    TrieNode *node = root;
    for (int i = 31; i >= 0; i--) {
        int bit = (ip >> i) & 1;
        if (!node->children[bit]) {
            return -1;  // IP address not found
        }
        node = node->children[bit];
    }
    return node->isEndOfIP ? node->port : -1;
}

int decToHex(int input)
{
	int decimal_num, remainder, i = 0;
    char hexadecimal_num[100];

    printf("Enter a decimal number: ");
    scanf("%d", &decimal_num);

    while (decimal_num != 0) {
        remainder = decimal_num % 16;
        if (remainder < 10) {
            hexadecimal_num[i] = remainder + 48;
        } else {
            hexadecimal_num[i] = remainder + 55;
        }
        i++;
        decimal_num /= 16;
    }

    printf("Hexadecimal equivalent: ");
    for (int j = i - 1; j >= 0; j--) {
        printf("%c", hexadecimal_num[j]);
    }
    printf("\n");

    return 0;
}

int main(int argc, char ** argv) {

	char ip_address[20];
    unsigned int ip_parts[4];
    unsigned int ip_hex;
	int port;
	int uflag = 0;
  	char *svalue = NULL;
  	char *ivalue = NULL;
  	int index;
  	int c;

  	opterr = 0;



	while ((c = getopt (argc, argv, "s:ui:")) != -1)
    switch (c)
      {
      case 's':
        svalue = optarg;
        break;
      case 'u':
        uflag = 1;
        break;
      case 'i':
        ivalue = optarg;
        break;
      case '?':
        if (optopt == 'c')
          fprintf (stderr, "Option -%c requires an argument.\n", optopt);
        else if (isprint (optopt))
          fprintf (stderr, "Unknown option `-%c'.\n", optopt);
        else
          fprintf (stderr,
                   "Unknown option character `\\x%x'.\n",
                   optopt);
        return 1;
      default:
        abort ();
      }

	printf ("uflag = %d, ivalue = %s, svalue = %s\n", uflag, ivalue, svalue);

#if 0
    printf("Enter the IP address in dotted decimal notation (e.g., 192.168.1.1): ");
    scanf("%s", ip_address);

    if (sscanf(ip_address, "%u.%u.%u.%u", &ip_parts[0], &ip_parts[1], &ip_parts[2], &ip_parts[3]) != 4) {
        printf("Invalid IP address format.\n");
        return 1;
    }

    ip_hex = (ip_parts[0] << 24) | (ip_parts[1] << 16) | (ip_parts[2] << 8) | ip_parts[3];

    printf("The IP address in hexadecimal is: %08X\n", ip_hex);

    printf("Enter the port number (e.g., 8080): ");
    scanf("%d", &port);
	return 0;
#endif 

    //printf("Enter the IP address in dotted decimal notation (e.g., 192.168.1.1): ");
    //scanf("%s", ip_address);

    if (sscanf(ivalue, "%u.%u.%u.%u:%d", &ip_parts[0], &ip_parts[1], &ip_parts[2], &ip_parts[3], &port) != 5) {
        printf("Invalid IP:port format.\n");
        return 1;
    }

    ip_hex = (ip_parts[0] << 24) | (ip_parts[1] << 16) | (ip_parts[2] << 8) | ip_parts[3];

    printf("The IP address in hexadecimal is: %08X Port is: %d\n", ip_hex, port);

    TrieNode *root = createNode();

    // Insert IP addresses and ports
    insert(root, 0xC0A80001, 8080);  // 192.168.0.1 -> port 8080
    insert(root, 0xC0A80002, 9090);  // 192.168.0.2 -> port 9090
    insert(root, ip_hex, port);  // 192.168.0.1 -> port 8080

    // Search for IP addresses
    unsigned int ip1 = 0xC0A80001;  // 192.168.0.1
    unsigned int ip2 = 0xC0A80003;  // 192.168.0.3

    int port1 = search(root, ip1);
    int port2 = search(root, ip2);

    printf("IP 192.168.0.1 -> Port %d\n", port1);  // Should print 8080
    printf("IP 192.168.0.3 -> Port %d\n", port2);  // Should print -1 (not found)

    return 0;
}

