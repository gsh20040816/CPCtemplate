#include "../src/compact/expression.hpp"
#include <iostream>

// Reads one expression per line and prints its value.
int main()
{
    string line;
    while (getline(cin, line)) cout << Expression(line).eval() << '\n';
}
