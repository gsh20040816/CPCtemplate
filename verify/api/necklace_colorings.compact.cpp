#include <bits/stdc++.h>
#include "../../src/compact/polya.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    long long colors, mod;
    cin >> n >> colors >> mod;
    cout << necklace_colorings(n, colors, mod) << '\n';
    cout << necklace_colorings(n, colors, mod, true) << '\n';
}
