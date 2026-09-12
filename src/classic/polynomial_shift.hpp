#pragma once
#include "ntt_convolution.hpp"

// BEGIN Polynomial_Shift
template <int mod = 998244353, int primitive = 3>
vector<Mod_Int<mod>> Polynomial_Shift(const vector<Mod_Int<mod>> &f, Mod_Int<mod> c)
{
    using N = Ntt_Convolution<mod, primitive>;
    using Z = typename N::Z;
    using Poly = typename N::Poly;
    if ( f.empty() )
        return {};
    assert(f.size() <= (N::max_size + 1ULL) / 2);
    int n = f.size();
    Poly fact(n), inv(n), a(n), b(n);
    fact[0] = 1;
    for ( int i = 1; i < n; i++ )
        fact[i] = fact[i - 1] * i;
    inv[n - 1] = fact[n - 1].Inv();
    for ( int i = n - 1; i > 0; i-- )
        inv[i - 1] = inv[i] * i;
    Z power = 1;
    for ( int i = 0; i < n; i++ )
    {
        a[n - 1 - i] = f[i] * fact[i];
        b[i] = power * inv[i];
        power = power * c;
    }
    auto product = N::Multiply(a, b);
    for ( int i = 0; i < n; i++ )
        a[i] = product[n - 1 - i] * inv[i];
    return a;
}

// END Polynomial_Shift
