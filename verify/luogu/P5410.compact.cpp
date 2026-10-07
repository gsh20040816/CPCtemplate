#include <iostream>
#include "../../src/compact/exkmp.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string a, b;
    cin >> a >> b;
    auto [z, p] = exkmp(a, b);
    long long x = 0, y = 0;
    for (int i = 0; i < (int)z.size(); i++)
        x ^= 1LL * (i + 1) * (z[i] + 1);
    for (int i = 0; i < (int)p.size(); i++)
        y ^= 1LL * (i + 1) * (p[i] + 1);
    cout << x << '\n' << y << '\n';
}
