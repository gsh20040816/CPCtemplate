#pragma once
#include "ntt_convolution.hpp"

struct FpsInverse : NttConvolution<998244353>
{
    static constexpr int mod = 998244353;

    static Poly inverse(const Poly &a, int n)
    {
        assert(n > 0 && n <= max_size && !a.empty() && a[0].v);
        Poly b{a[0].inv()};
        while ((int)b.size() < n)
        {
            int k = b.size(), len = 2 * k;
            int m = min(n, len);
            Poly f(a.begin(), a.begin() + min(m, (int)a.size()));
            Poly g = b;
            f.resize(len);
            g.resize(len);
            ntt(f);
            ntt(g);
            for (int i = 0; i < len; i++)
                f[i] *= g[i];
            ntt(f, true);
            // Only the high half of a*b is free of cyclic wraparound.
            fill(f.begin(), f.begin() + k, Z(0));
            ntt(f);
            for (int i = 0; i < len; i++)
                f[i] *= g[i];
            ntt(f, true);
            b.resize(m);
            for (int i = k; i < m; i++)
                b[i] = Z(0) - f[i];
        }
        return b;
    }
};
