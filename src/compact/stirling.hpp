#pragma once
#include "ntt_convolution.hpp"

// BEGIN stirling_second_row
template <int mod = 998244353, int primitive = 3>
inline vector<ModInt<mod>> stirling_second_row(unsigned long long n, int m)
{
    using N = NttConvolution<mod, primitive>;
    assert(m >= 0 && m <= (N::max_size - 1) / 2);
    using Z = typename N::Z;
    typename N::Poly a(m + 1), b(m + 1);
    b[0] = 1;
    for (int i = 1; i <= m; i++)
        b[i] = b[i - 1] * i;
    b[m] = b[m].inv();
    for (int i = m; i > 0; i--)
        b[i - 1] = b[i] * i;
    for (int i = 0; i <= m; i++)
    {
        Z value = i ? Z(i).pow(n % (mod - 1)) : Z(n == 0);
        a[i] = value * b[i];
        if (i % 2)
            b[i] = Z(0) - b[i];
    }
    auto answer = N::multiply(a, b);
    answer.resize(m + 1);
    return answer;
}

// END stirling_second_row

// BEGIN stirling_first_row
template <int mod = 998244353, int primitive = 3>
inline vector<ModInt<mod>> stirling_first_row(int n)
{
    using N = NttConvolution<mod, primitive>;
    assert(n >= 0 && n < N::max_size);
    using Z = typename N::Z;
    using Poly = typename N::Poly;
    if (n == 0)
        return {1};
    function<Poly(int, int)> solve = [&](int l, int r) -> Poly
    {
        if (r - l <= 16)
        {
            Poly f(r - l + 1);
            f[0] = 1;
            for (int j = l; j < r; j++)
            {
                for (int k = j - l + 1; k > 0; k--)
                    f[k] = f[k - 1] + f[k] * j;
                f[0] = f[0] * j;
            }
            return f;
        }
        int m = (l + r) / 2;
        return N::multiply(solve(l, m), solve(m, r));
    };
    return solve(0, n);
}

// END stirling_first_row
