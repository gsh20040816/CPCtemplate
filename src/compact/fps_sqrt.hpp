#pragma once
#include "fps_inverse.hpp"
#include "modular_sqrt.hpp"

struct FpsSqrt : FpsInverse
{
    static optional<Poly> sqrt(const Poly &a, int n)
    {
        assert(n >= 0 && n <= max_size / 2);
        int k = 0;
        while (k < n && (k >= (int)a.size() || a[k].v == 0)) k++;
        if (k == n) return Poly(n);
        if (k & 1) return nullopt;
        auto roots = mod_sqrt(a[k].v, mod);
        if (roots.empty()) return nullopt;
        Poly b{Z(roots[0])};
        int target = n - k;
        while ((int)b.size() < target)
        {
            int m = min(target, 2 * (int)b.size());
            Poly f(a.begin() + k, a.begin() + min(k + m, (int)a.size()));
            auto t = multiply(f, inverse(b, m));
            t.resize(m);
            for (int i = 0; i < (int)b.size(); i++) t[i] += b[i];
            for (auto &x : t) x *= Z((mod + 1) / 2);
            b = move(t);
        }
        b.insert(b.begin(), k / 2, Z(0));
        b.resize(n);
        return b;
    }
};
