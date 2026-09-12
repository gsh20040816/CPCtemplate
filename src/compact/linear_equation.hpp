#pragma once
#include "number_theory.hpp"

// BEGIN linear_equation
inline bool
linear_equation(long long a, long long b, long long c, __int128_t &x, __int128_t &y)
{
    using i128 = __int128_t;
    x = 0;
    y = 0;
    if (!a && !b)
        return c == 0;
    i128 aa = a < 0 ? -i128(a) : i128(a);
    i128 bb = b < 0 ? -i128(b) : i128(b);
    i128 u, v;
    i128 g = NumberTheory::exgcd(aa, bb, u, v);
    if (c % g)
        return false;
    x = u * (c / g);
    y = v * (c / g);
    if (a < 0)
        x = -x;
    if (b < 0)
        y = -y;
    return true;
}

// END linear_equation
