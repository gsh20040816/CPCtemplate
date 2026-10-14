#include "../src/compact/bernoulli.hpp"
#include <iostream>

// Prints B_0..B_n mod 998244353 for n read from stdin.
int main()
{
    int n;
    cin >> n;
    for (auto x : bernoulli(n)) cout << x.v << ' ';
    cout << '\n';
}
