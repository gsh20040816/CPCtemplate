#include <bits/stdc++.h>
#include "../../src/compact/q_binomial.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        unsigned long long n, k;
        int q, p;
        cin >> n >> k >> q >> p;
        cout << q_binomial(n, k, q, p) << '\n';
    }
}
