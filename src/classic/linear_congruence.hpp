#pragma once
#include "number_theory.hpp"

// BEGIN Linear_Congruence
inline pair<long long, long long>
Linear_Congruence(long long a, long long b, long long m)
{
    assert(m > 0);
    using i128 = __int128_t;
    a %= m;
    if ( a < 0 )
        a += m;
    i128 x, y;
    i128 g = Number_Theory::Exgcd(a, m, x, y);
    if ( i128(b) % g )
        return {-1, -1};
    i128 period = m / g;
    x = x * (-i128(b) / g) % period;
    if ( x < 0 )
        x += period;
    return {(long long)x, (long long)period};
}

// END Linear_Congruence
