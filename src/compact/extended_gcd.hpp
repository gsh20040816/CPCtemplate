#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

// BEGIN extended_gcd
inline __int128_t extended_gcd(__int128_t a, __int128_t b, __int128_t &x, __int128_t &y)
{
    using i128 = __int128_t;
    if (!b)
    {
        x = 1;
        y = 0;
        return a;
    }
    i128 d = extended_gcd(b, a % b, y, x);
    y -= a / b * x;
    return d;
}

// END extended_gcd
