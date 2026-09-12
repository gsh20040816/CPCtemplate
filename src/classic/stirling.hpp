#pragma once
#include "ntt_convolution.hpp"

// BEGIN Stirling_Second_Row
template <int mod = 998244353, int primitive = 3>
inline vector<Mod_Int<mod>> Stirling_Second_Row(unsigned long long n, int m)
{
    using N = Ntt_Convolution<mod, primitive>;
    assert(m >= 0 && m <= (N::max_size - 1) / 2);
    using Z = typename N::Z;
    typename N::Poly a(m + 1), b(m + 1);
    b[0] = 1;
    for ( int i = 1; i <= m; i++ )
        b[i] = b[i - 1] * i;
    b[m] = b[m].Inv();
    for ( int i = m; i > 0; i-- )
        b[i - 1] = b[i] * i;
    for ( int i = 0; i <= m; i++ )
    {
        Z value = i ? Z(i).Pow(n % (mod - 1)) : Z(n == 0);
        a[i] = value * b[i];
        if ( i % 2 )
            b[i] = Z(0) - b[i];
    }
    auto answer = N::Multiply(a, b);
    answer.resize(m + 1);
    return answer;
}

// END Stirling_Second_Row

// BEGIN Stirling_First_Row
template <int mod = 998244353, int primitive = 3>
inline vector<Mod_Int<mod>> Stirling_First_Row(int n)
{
    using N = Ntt_Convolution<mod, primitive>;
    assert(n >= 0 && n < N::max_size);
    using Z = typename N::Z;
    using Poly = typename N::Poly;
    if ( n == 0 )
        return {1};
    function<Poly(int, int)> Solve = [&](int l, int r) -> Poly
    {
        if ( r - l <= 16 )
        {
            Poly f(r - l + 1);
            f[0] = 1;
            for ( int j = l; j < r; j++ )
            {
                for ( int k = j - l + 1; k > 0; k-- )
                    f[k] = f[k - 1] + f[k] * j;
                f[0] = f[0] * j;
            }
            return f;
        }
        int m = (l + r) / 2;
        return N::Multiply(Solve(l, m), Solve(m, r));
    };
    return Solve(0, n);
}

// END Stirling_First_Row
