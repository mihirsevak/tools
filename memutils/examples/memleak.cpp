// Program with memory leak
#include <bits/stdc++.h>
using namespace std;

// function with memory leak
void func_to_show_mem_leak()
{
    int* ptr = new int(1024);

    // body

    // return without deallocating ptr
    return;
}

// driver code
int main()
{

	char* ptr;
    // Call the function
    // to get the memory leak
	while(1) {
		ptr = (char*)malloc(1024);
    	func_to_show_mem_leak();
		cout << "Sleeping for 10 second..." << std::endl;
		this_thread::sleep_for(std::chrono::seconds(10));
		//cout << "Awake now!" << std::endl;
	}
	

    return 0;
}


