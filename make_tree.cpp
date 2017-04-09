#include <iostream>
#include <signal.h>
#include <vector>
#include <map>

using namespace std;

//global enteties
bool interrupt_raised = 0;

typedef struct Node {
	int value;
	Node* left = NULL;
	Node* right = NULL;
} Node;

map <int, vector<int> > tree;

//functions

void display_tree()
{
	for (map<int, vector<int> >::iterator it=tree.begin(); it != tree.end(); ++it ){
		cout << "Depth = " << it->first << ": ";
		for(vector<int>::const_iterator v=(it->second).begin(); v != (it->second).end(); ++v )
			cout << *v << ", ";

		cout << endl;
	}
}

void print_tree(Node* head, int depth)
{
	cout << "Depth=" << depth+1 << ": "; 
	while ( head != NULL ) {
		//cout << "PRINT_TREE " << "head address  " << head << endl;
		cout << head->value << endl;
	    tree[depth+1].push_back(head->value);	
		if (head->left != NULL) {
			cout << "Left: " ;
			print_tree(head->left, depth+1);
		}
		if (head->right != NULL) {
			cout << "Right: " ;
			print_tree(head->right, depth+1);
		}
		return;
	}

}

void build_tree(Node* head, int value)
{

	//cout << "address of head node:" <<  head << endl;
	if ( value < head->value ) { 
		if (head->left == NULL) {
			head->left = new Node;
			head->left->value = value;
			head->left->left = NULL;
			head->left->right = NULL;
			//cout  << head->left << " and value =" << head->left->value << endl;
		} else {
			build_tree(head->left, value);
		}
	} else {	
		if (head->right == NULL) {
			head->right = new Node;
			head->right->value = value;
			head->right->left = NULL;
			head->right->right = NULL;
			//cout  << head->right << " and value =" << head->right->value << endl;
		} else {
			build_tree(head->right, value);
		}
	}

}


void signal_handler(int a)
{
	cout << "^c was caught" << endl;
	interrupt_raised = 1;
}


//main
int main()
{

	Node* root = NULL;

	signal(SIGINT, signal_handler);	

	while (interrupt_raised == 0) {
		cout << "please enter some value:";
		int value;
		cin >> value;
		if ( root == NULL ) {
			root = new Node;
			root->value = value;
		} else {
			build_tree(root, value);
			//print_tree(root);
		}
	}

	print_tree(root, 0);
	cout << "***************************" << endl;
	cout << "Final tree looks like below" << endl;
	cout << "***************************" << endl;
	display_tree();

	return 0;
}
