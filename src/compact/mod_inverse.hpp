#pragma once
#include <cassert>
#include "extended_gcd.hpp"

// BEGIN mod_inverse
inline long long mod_inverse(long long a, long long m)
{
    using i128 = __int128_t;
    assert(m > 0);
    a %= m;
    if (a < 0) a += m;
    i128 x, y;
    if (extended_gcd(a, m, x, y) != 1) return -1;
    return (x % m + m) % m;
}

// END mod_inverse
