#include <bits/stdc++.h>
#include <cassert>
using namespace std;
#include "../src/compact/exkmp.hpp"
int main()
{
    string s, t;
    while (getline(cin, s) && getline(cin, t))
    {
        auto [z, p] = exkmp(s, t);
        for (int x : p)
            cout << x << ' ';
        cout << '\n';
    }
}
