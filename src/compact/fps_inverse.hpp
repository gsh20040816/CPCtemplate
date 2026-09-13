#pragma once
#include "ntt_convolution.hpp"

struct FpsInverse : NttConvolution<998244353>
{
    static constexpr int mod = 998244353;

    static Poly inverse(const Poly &a, int n)
    {
        assert(n > 0 && !a.empty() && a[0].v);
        Poly b{a[0].inv()};
        while ((int)b.size() < n)
        {
            int m = min(n, 2 * (int)b.size());
            Poly f(a.begin(), a.begin() + min(m, (int)a.size()));
            auto t = multiply(f, b);
            t.resize(m);
            for (auto &x : t) x = Z(0) - x;
            t[0] = t[0] + 2;
            b = multiply(b, t);
            b.resize(m);
        }
        return b;
    }
};
