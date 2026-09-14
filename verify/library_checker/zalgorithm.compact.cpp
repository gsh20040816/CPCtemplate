#include "../../src/compact/string.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    auto z = z_function(s);
    for (int i = 0; i < (int)z.size(); i++)
        cout << z[i] << (i + 1 == (int)z.size() ? '\n' : ' ');
}
