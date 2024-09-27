#include <iostream>
#include <string>
#include <fstream>

using namespace std;

string rotate(string input)
{

	srand((unsigned)time(0));
	int x = rand(); 

   	int rand_num = static_cast<int>( x % (input.length()) );
	//cout << "split loc: " << rand_num << " Input Password: " << input << endl;

	string substr1 = input.substr(0, rand_num);
	string substr2 = input.substr(rand_num);

	string output = substr2 + substr1;
	//cout << output << endl;

	return output;
}

/// To Do: update existing password entry
int update_password(string app="default", string username="default", string password="default")
{
	ifstream passwordfile;
	passwordfile.open("password.db");
	int curLine = 0;
	string line;

	while(getline(passwordfile, line)) { // I changed this, see below
    	curLine++;
    	if (line.find(app, 0) != string::npos) {
			if (line.find(username, 0) != string::npos) {
			   if (line.find(password, 0) == string::npos) {
					cout << "Line with Application and Username found. Password needs updating." << endl;
        			cout << "found: " << username << "line: " << curLine << endl;
					return 0;
				}
			}
		}
    }

	return 1;
}


void store_password(string input)
{
	string application;
	string username;

	cout << "Which application this password is for?: ";
	cin >> application;

	cout << "What is the username?: ";
	cin >> username;

	if ( update_password(application, username, input) == 0 )
		return;

	/// To Do: Search for existing entry to update.
	ofstream passwordfile;
	passwordfile.open("password.db");
	passwordfile << application << " username:" << username << " password:" <<input << endl;
	passwordfile.close();
	
	/// To Do: Encrypt password file to avoid hacking

}


/// To Do: remove existing password entry
void remove_password(string app="default", string username="default", string password="default")
{


}

/// To Do: retreive existing password
void retreive_password()
{
	// Decrypt password file 

	// Serch for password and display it

}

int main()
{
	int length;
	char isUpper, isNumerical, isSpecial;
	char c;
	int i = 0;
	string password;

	char upper[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
	char lower[] = "abcdefghijklmnopqrstuvwxyz";
	char special[] = "~!@#$%^&*()";

	cout << "Please enter minimum length of password: ";
	cin >> length;
	cout << "Do we need upper letters?(y/n): ";
	cin >> isUpper;
	cout << "Do we need numbers?(y/n): ";
	cin >> isNumerical;
	cout << "Do we need sepcial characters?(y/n): ";
	cin >> isSpecial;
	
	// Seedign for random number
	srand((unsigned)time(0));

	while ( i < length-2 ) {

		// x is in [0,1[
	    int x = rand(); 

   		// [0,1[ * (max - min) + min is in [min,max[
   		int rand_num = static_cast<int>( x % (3) );

		//cout << x << " " << rand_num << endl;

		switch (rand_num) {
			case 1:
				//cout << "came in case 1" << endl;
				c = lower[rand() % 26];
				break;
			case 2:
				//cout << "came in case 2" << endl;
				c = upper[rand() % 26];
				break;
			case 3:
				//cout << "came in case 3" << endl;
				c = special[rand() % 9];
				break;
			default:
				//cout << "came in default case" << endl;
				c = lower[rand() % 26];
				break;
			
		}    
		
		password = password + c;

		i++;
	}
	c = special[rand() % 9];
	password = password + c;
	
	
	int n = rand() % 9;
	//cout << n << endl;
	password = password + to_string(n);

	password = rotate(password);

	store_password(password);
	//cout << password << endl;

	return 0;
}

