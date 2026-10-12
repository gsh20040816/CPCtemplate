#include <bits/stdc++.h>
#include <cassert>
using namespace std;
#include "fixtures/wida_fraction/Frac.cpp"

int main()
{
    Frac<long long> x(2, 3);
    auto y = x / x;
    x /= x;
    assert(y == Frac<long long>(1));
    assert(x == Frac<long long>(1, 3));
    cout << "original x / x = " << y << "; original x /= x = " << x << '\n';
}
