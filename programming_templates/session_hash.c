#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TABLE_SIZE 100

typedef struct {
    char src_ip[16];
    int src_port;
    char dest_ip[16];
    int dest_port;
} Connection;

typedef struct Node {
    Connection data;
    struct Node* next;
} Node;

//((size_t)(key.src.s_addr) * 59) ^ ((size_t)(key.dst.s_addr)) ^ ((size_t)(key.sport) << 16) ^ ((size_t)(key.dport)) ^ ((size_t)(key.proto));
unsigned int hash_function(const char* src_ip, int src_port, const char* dest_ip, int dest_port) {
    unsigned int hash = 0;
    while (*src_ip) hash = (hash << 5) + *src_ip++;
    hash += src_port;
    while (*dest_ip) hash = (hash << 5) + *dest_ip++;
    hash += dest_port;
    return hash % TABLE_SIZE;
}

Node* hash_table[TABLE_SIZE];

void init_table() {
    for (int i = 0; i < TABLE_SIZE; i++) {
        hash_table[i] = NULL;
    }
}

void insert(const char* src_ip, int src_port, const char* dest_ip, int dest_port) {
    unsigned int index = hash_function(src_ip, src_port, dest_ip, dest_port);
    Node* new_node = (Node*)malloc(sizeof(Node));
    strcpy(new_node->data.src_ip, src_ip);
    new_node->data.src_port = src_port;
    strcpy(new_node->data.dest_ip, dest_ip);
    new_node->data.dest_port = dest_port;
    new_node->next = hash_table[index];
    hash_table[index] = new_node;
}

Node* search(const char* src_ip, int src_port, const char* dest_ip, int dest_port) {
    unsigned int index = hash_function(src_ip, src_port, dest_ip, dest_port);
    Node* current = hash_table[index];
    while (current != NULL) {
        if (strcmp(current->data.src_ip, src_ip) == 0 &&
            current->data.src_port == src_port &&
            strcmp(current->data.dest_ip, dest_ip) == 0 &&
            current->data.dest_port == dest_port) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

void delete(const char* src_ip, int src_port, const char* dest_ip, int dest_port) {
    unsigned int index = hash_function(src_ip, src_port, dest_ip, dest_port);
    Node* current = hash_table[index];
    Node* prev = NULL;
    while (current != NULL) {
        if (strcmp(current->data.src_ip, src_ip) == 0 &&
            current->data.src_port == src_port &&
            strcmp(current->data.dest_ip, dest_ip) == 0 &&
            current->data.dest_port == dest_port) {
            if (prev == NULL) {
                hash_table[index] = current->next;
            } else {
                prev->next = current->next;
            }
            free(current);
            return;
        }
        prev = current;
        current = current->next;
    }
}

int main() {
    init_table();
    insert("192.168.1.1", 1234, "192.168.1.2", 80);
    Node* result = search("192.168.1.1", 1234, "192.168.1.2", 80);
    if (result) {
        printf("Connection found: %s:%d -> %s:%d\n", result->data.src_ip, result->data.src_port, result->data.dest_ip, result->data.dest_port);
    } else {
        printf("Connection not found.\n");
    }
    delete("192.168.1.1", 1234, "192.168.1.2", 80);
    return 0;
}

