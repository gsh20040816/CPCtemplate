#pragma once
#include "ntt_convolution.hpp"

template <int mod = 998244353, int primitive = 3> struct Bostan_Mori
{
    using N = Ntt_Convolution<mod, primitive>;
    using Z = typename N::Z;
    using Poly = typename N::Poly;
    using U = unsigned long long;

    // Coefficient of x^n in p(x) / q(x), with q[0] != 0.
    static Z Coefficient(Poly p, Poly q, U n)
    {
        assert(!q.empty() && q[0].v != 0);
        assert(max(p.size(), q.size()) <= (N::max_size + 1ULL) / 2);
        while ( n && !p.empty() )
        {
            Poly r = q;
            for ( int i = 1; i < int(r.size()); i += 2 )
                r[i] = Z(0) - r[i];
            Poly a = N::Multiply(p, r);
            Poly b = N::Multiply(q, r);
            p.clear();
            q.clear();
            for ( int i = n & 1; i < int(a.size()); i += 2 )
                p.push_back(a[i]);
            for ( int i = 0; i < int(b.size()); i += 2 )
                q.push_back(b[i]);
            n >>= 1;
        }
        return p.empty() ? Z(0) : p[0] / q[0];
    }

    // a[i] = c[0]*a[i-1] + ... + c[k-1]*a[i-k], for i >= k.
    static Z Recurrence(const Poly &init, const Poly &c, U n)
    {
        assert(init.size() == c.size());
        int k = c.size();
        if ( k == 0 )
            return 0;
        if ( n < init.size() )
            return init[n];
        assert(k + 1ULL <= (N::max_size + 1ULL) / 2);
        Poly q(k + 1);
        q[0] = 1;
        for ( int i = 0; i < k; i++ )
            q[i + 1] = Z(0) - c[i];
        Poly p = N::Multiply(init, q);
        p.resize(k);
        return Coefficient(p, q, n);
    }
};
