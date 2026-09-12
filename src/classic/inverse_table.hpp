#pragma once
#include <cassert>
#include <vector>
using namespace std;

// BEGIN Inverse_Table
inline vector<int> Inverse_Table(int n, int p)
{
    assert(p >= 2 && 0 <= n && n < p);
    vector<int> inverse(n + 1);
    if ( n )
        inverse[1] = 1;
    for ( int i = 2; i <= n; i++ )
        inverse[i] = p - 1LL * (p / i) * inverse[p % i] % p;
    return inverse;
}

// END Inverse_Table
