#pragma once
#include "set_convolution.hpp"

// BEGIN Subset_Convolution
// c[s] = sum_{t subset s} a[t] * b[s xor t].
template <int mod = 998244353>
vector<Mod_Int<mod>> Subset_Convolution(const vector<Mod_Int<mod>> &a,
                                        const vector<Mod_Int<mod>> &b)
{
    using F = Set_Convolution<mod>;
    using Poly = typename F::Poly;
    assert(!a.empty() && a.size() == b.size() && a.size() <= INT_MAX);
    int n = a.size(), m = 0;
    assert((n & (n - 1)) == 0);
    while ( (1 << m) < n )
        m++;
    vector<Poly> f(m + 1, Poly(n)), g(m + 1, Poly(n));
    vector<int> rank(n);
    for ( int s = 0; s < n; s++ )
    {
        rank[s] = __builtin_popcount(unsigned(s));
        f[rank[s]][s] = a[s];
        g[rank[s]][s] = b[s];
    }
    for ( int k = 0; k <= m; k++ )
    {
        F::Transform(f[k], '|');
        F::Transform(g[k], '|');
    }
    Poly answer(n), h(n);
    for ( int k = 0; k <= m; k++ )
    {
        fill(h.begin(), h.end(), 0);
        for ( int i = 0; i <= k; i++ )
            for ( int s = 0; s < n; s++ )
                h[s] = h[s] + f[i][s] * g[k - i][s];
        F::Transform(h, '|', true);
        for ( int s = 0; s < n; s++ )
            if ( rank[s] == k )
                answer[s] = h[s];
    }
    return answer;
}

// END Subset_Convolution
