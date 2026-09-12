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
    for (int i = 1; i <= m; i++) b[i] = b[i - 1] * i;
    b[m] = b[m].inv();
    for (int i = m; i > 0; i--) b[i - 1] = b[i] * i;
    for (int i = 0; i <= m; i++)
    {
        Z value = i ? Z(i).pow(n % (mod - 1)) : Z(n == 0);
        a[i] = value * b[i];
        if (i % 2) b[i] = Z(0) - b[i];
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
    Poly fact(n + 1), inv(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; i++) fact[i] = fact[i - 1] * i;
    inv[n] = fact[n].inv();
    for (int i = n; i > 0; i--) inv[i - 1] = inv[i] * i;
    function<Poly(int)> solve = [&](int len) -> Poly
    {
        if (len == 0) return {1};
        int m = len / 2;
        Poly f = solve(m);
        Poly a(m + 1), b(m + 1);
        Z power = 1;
        for (int i = 0; i <= m; i++)
        {
            a[m - i] = f[i] * fact[i];
            b[i] = power * inv[i];
            power = power * m;
        }
        auto c = N::multiply(a, b);
        for (int i = 0; i <= m; i++) a[i] = c[m - i] * inv[i];
        f = N::multiply(f, a);
        if (len % 2)
        {
            f.push_back(0);
            for (int i = len; i > 0; i--) f[i] = f[i - 1] + f[i] * (len - 1);
            f[0] = f[0] * (len - 1);
        }
        return f;
    };
    return solve(n);
}

// END stirling_first_row
