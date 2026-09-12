#pragma once
#include "number_theory.hpp"

template <int mod, int primitive = 3> struct Ntt_Convolution
{
    static_assert(mod >= 2 && primitive >= 1 && primitive < mod);
    static constexpr int max_size = (mod - 1) & -(mod - 1);
    using Z = Mod_Int<mod>;
    using Poly = vector<Z>;

    // mod is prime, primitive is a primitive root modulo mod.
    static void Ntt(Poly &a, bool invert = false)
    {
        int n = a.size();
        assert(n > 0 && (n & (n - 1)) == 0 && n <= max_size);
        for ( int i = 1, j = 0; i < n; i++ )
        {
            int bit = n >> 1;
            for ( ; j & bit; bit >>= 1 )
                j ^= bit;
            j ^= bit;
            if ( i < j )
                swap(a[i], a[j]);
        }
        for ( int half = 1; half < n; half *= 2 )
        {
            int len = half * 2;
            Z step = Z(primitive).Pow((mod - 1) / len);
            if ( invert )
                step = step.Inv();
            for ( int i = 0; i < n; i += len )
            {
                Z w = 1;
                for ( int j = 0; j < half; j++ )
                {
                    Z u = a[i + j], v = a[i + j + half] * w;
                    a[i + j] = u + v;
                    a[i + j + half] = u - v;
                    w = w * step;
                }
            }
        }
        if ( invert )
        {
            Z inverse = Z(n).Inv();
            for ( auto &x : a )
                x = x * inverse;
        }
    }

    static Poly Multiply(Poly a, Poly b)
    {
        if ( a.empty() || b.empty() )
            return {};
        assert(a.size() + b.size() - 1 <= max_size);
        int size = a.size() + b.size() - 1, n = 1;
        while ( n < size )
            n *= 2;
        a.resize(n);
        b.resize(n);
        Ntt(a);
        Ntt(b);
        for ( int i = 0; i < n; i++ )
            a[i] = a[i] * b[i];
        Ntt(a, true);
        a.resize(size);
        return a;
    }
};
