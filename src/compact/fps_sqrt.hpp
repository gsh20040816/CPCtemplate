#pragma once
#include "fps_inverse.hpp"
#include "modular_sqrt.hpp"

struct FpsSqrt : FpsInverse
{
    static optional<Poly> inverse_sqrt(const Poly &a, int n)
    {
        assert(n >= 0 && n <= max_size / 2);
        if (n == 0)
            return Poly{};
        if (a.empty() || a[0].v == 0)
            return nullopt;
        auto roots = mod_sqrt(a[0].v, mod);
        if (roots.empty())
            return nullopt;
        Poly b{Z(roots[0]).inv()};
        Z half = Z(2).inv();
        while ((int)b.size() < n)
        {
            int k = b.size(), len = 4 * k;
            int m = min(n, 2 * k);
            Poly f(a.begin(), a.begin() + min(m, (int)a.size()));
            Poly g = b;
            f.resize(len);
            g.resize(len);
            ntt(f);
            ntt(g);
            for (int i = 0; i < len; i++)
                f[i] *= g[i] * g[i] * g[i];
            ntt(f, true);
            // b <- (3*b - a*b^3)/2; cyclic wrap only reaches below k.
            b.resize(m);
            for (int i = k; i < m; i++)
                b[i] = Z(0) - f[i] * half;
        }
        return b;
    }

    static optional<Poly> sqrt(const Poly &a, int n)
    {
        assert(n >= 0 && n <= max_size / 2);
        int k = 0;
        while (k < n && (k >= (int)a.size() || a[k].v == 0))
            k++;
        if (k == n)
            return Poly(n);
        if (k & 1)
            return nullopt;
        int target = n - k;
        Poly f(a.begin() + k, a.begin() + min(n, (int)a.size()));
        auto inverse = inverse_sqrt(f, target);
        if (!inverse)
            return nullopt;
        Poly b = multiply(f, *inverse);
        b.resize(target);
        b.insert(b.begin(), k / 2, Z(0));
        b.resize(n);
        return b;
    }
};
