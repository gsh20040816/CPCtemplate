#pragma once
#include "number_theory.hpp"

// BEGIN Floor_Moments
inline array<Mod_Int<998244353>, 3>
Floor_Moments(long long n, long long m, long long a, long long b)
{
    using Z = Mod_Int<998244353>;
    assert(n >= 0 && n <= 1000000001 && m >= 1 && m <= 1000000000);
    if ( !n )
        return {0, 0, 0};
    auto normalize = [&](long long &v)
    {
        long long q = v / m;
        if ( v % m < 0 )
            q--;
        v = (__int128_t(v) - __int128_t(q) * m);
        return Z(q);
    };
    Z x = normalize(a);
    Z y = normalize(b);
    Z count = n;
    Z s1 = count * Z(n - 1) * Z(499122177);
    Z s2 = count * Z(n - 1) * Z(2 * n - 1) * Z(166374059);
    Z f = 0, g = 0, h = 0;
    if ( a )
    {
        long long height = (a * (n - 1) + b) / m;
        auto [u, v, w] = Floor_Moments(height, a, m, m + a - b - 1);
        Z t = height;
        f = count * t - u;
        g = t * s1 - (w - u) * Z(499122177);
        h = count * t * t - Z(2) * v - u;
    }
    return {f + x * s1 + y * count,
            g + x * s2 + y * s1,
            h + x * x * s2 + y * y * count + Z(2) * x * y * s1 + Z(2) * x * g +
                Z(2) * y * f};
}

// END Floor_Moments
