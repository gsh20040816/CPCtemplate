#include "../../src/compact/string.hpp"
#include <iostream>
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s, t;
    cin >> s >> t;
    for (int p : kmp_match(s, t)) cout << p + 1 << '\n';
    for (int x : prefix_function(t)) cout << x << ' ';
    cout << '\n';
}
