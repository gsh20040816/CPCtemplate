#pragma once
#include "number_theory.hpp"
#include <cassert>

struct Polynomial
{
    static constexpr int mod = 998244353;
    using Z = Mod_Int<mod>;
    using Poly = vector<Z>;
    static void Ntt(Poly &a, bool invert = false)
    {
        int n = (int)a.size();
        assert(n > 0 && (n & (n - 1)) == 0 && n <= (1 << 23));
        for ( int i = 1, j = 0; i < n; i++ )
        {
            int bit = n >> 1;
            for ( ; j & bit; bit >>= 1 )
                j ^= bit;
            j ^= bit;
            if ( i < j )
                swap(a[i], a[j]);
        }
        for ( int len = 2; len <= n; len *= 2 )
        {
            Z step = Z(3).Pow((mod - 1) / len);
            if ( invert )
                step = step.Inv();
            for ( int i = 0; i < n; i += len )
            {
                Z w = 1;
                for ( int j = 0; j < len / 2; j++, w = w * step )
                {
                    Z u = a[i + j], v = a[i + j + len / 2] * w;
                    a[i + j] = u + v;
                    a[i + j + len / 2] = u - v;
                }
            }
        }
        if ( invert )
        {
            Z Inv = Z(n).Inv();
            for ( auto &x : a )
                x = x * Inv;
        }
    }
    static Poly Multiply(Poly a, Poly b)
    {
        if ( a.empty() || b.empty() )
            return {};
        int size = (int)a.size() + (int)b.size() - 1, n = 1;
        assert(size <= (1 << 23));
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
    static Poly Inverse(const Poly &a, int n)
    {
        assert(n > 0 && !a.empty() && a[0].v);
        Poly b{a[0].Inv()};
        while ( (int)b.size() < n )
        {
            int m = min(n, 2 * (int)b.size());
            Poly f(a.begin(), a.begin() + min(m, (int)a.size()));
            auto t = Multiply(f, b);
            t.resize(m);
            for ( auto &x : t )
                x = Z(0) - x;
            t[0] = t[0] + 2;
            b = Multiply(b, t);
            b.resize(m);
        }
        return b;
    }
    static Poly Derivative(const Poly &a)
    {
        Poly b;
        for ( int i = 1; i < (int)a.size(); i++ )
            b.push_back(a[i] * i);
        return b;
    }
    static Poly Integral(const Poly &a)
    {
        Poly b(a.size() + 1);
        vector<Z> Inv(a.size() + 1);
        if ( !a.empty() )
            Inv[1] = 1;
        for ( int i = 2; i <= (int)a.size(); i++ )
            Inv[i] = Z(mod - mod / i) * Inv[mod % i];
        for ( int i = 0; i < (int)a.size(); i++ )
            b[i + 1] = a[i] * Inv[i + 1];
        return b;
    }
    static Poly Log(const Poly &a, int n)
    {
        assert(n > 0 && !a.empty() && a[0].v == 1);
        auto b = Multiply(Derivative(a), Inverse(a, n));
        b.resize(n - 1);
        return Integral(b);
    }
    static Poly Exp(const Poly &a, int n)
    {
        assert(n > 0 && (a.empty() || a[0].v == 0));
        Poly b{1};
        while ( (int)b.size() < n )
        {
            int m = min(n, 2 * (int)b.size());
            auto t = Log(b, m);
            for ( int i = 0; i < m; i++ )
                t[i] = (i < (int)a.size() ? a[i] : Z(0)) - t[i];
            t[0] = t[0] + 1;
            b = Multiply(b, t);
            b.resize(m);
        }
        return b;
    }
    static void Fwt(Poly &a, char op, bool invert = false)
    {
        int n = (int)a.size();
        assert(n > 0 && (n & (n - 1)) == 0);
        const Z inv2 = (mod + 1) / 2;
        for ( int len = 1; len < n; len *= 2 )
            for ( int i = 0; i < n; i += len * 2 )
                for ( int j = 0; j < len; j++ )
                {
                    Z &u = a[i + j], &v = a[i + j + len], x = u, y = v;
                    if ( op == '^' )
                    {
                        u = x + y;
                        v = x - y;
                        if ( invert )
                        {
                            u = u * inv2;
                            v = v * inv2;
                        }
                    }
                    else if ( op == '|' )
                        v = invert ? y - x : y + x;
                    else
                    {
                        assert(op == '&');
                        u = invert ? x - y : x + y;
                    }
                }
    }
    // c: s[n]=sum c[i-1]*s[n-i], i=1..L.
    static Poly Berlekamp_Massey(const Poly &s)
    {
        Poly c{1}, b{1};
        int l = 0, m = 1;
        Z last = 1;
        for ( int n = 0; n < (int)s.size(); n++ )
        {
            Z d = s[n];
            for ( int i = 1; i <= l; i++ )
                d = d + c[i] * s[n - i];
            if ( !d.v )
            {
                ++m;
                continue;
            }
            auto old = c;
            Z coef = d / last;
            if ( c.size() < b.size() + m )
                c.resize(b.size() + m);
            for ( int j = 0; j < (int)b.size(); j++ )
                c[j + m] = c[j + m] - coef * b[j];
            if ( 2 * l <= n )
            {
                l = n + 1 - l;
                b = old;
                last = d;
                m = 1;
            }
            else
                ++m;
        }
        c.erase(c.begin());
        for ( auto &x : c )
            x = Z(0) - x;
        return c;
    }
    static Z Recurrence(Poly init, const Poly &c, unsigned long long n)
    {
        int k = (int)c.size();
        if ( n < init.size() )
            return init[n];
        if ( !k )
            return 0;
        assert((int)init.size() >= k);
        auto combine = [&](const Poly &a, const Poly &b)
        {
            Poly t(2 * k - 1);
            for ( int i = 0; i < k; i++ )
                for ( int j = 0; j < k; j++ )
                    t[i + j] = t[i + j] + a[i] * b[j];
            for ( int i = 2 * k - 2; i >= k; i-- )
                for ( int j = 1; j <= k; j++ )
                    t[i - j] = t[i - j] + t[i] * c[j - 1];
            t.resize(k);
            return t;
        };
        Poly a(k), r(k);
        r[0] = 1;
        if ( k == 1 )
            a[0] = c[0];
        else
            a[1] = 1;
        for ( ; n; n >>= 1, a = combine(a, a) )
            if ( n & 1 )
                r = combine(r, a);
        Z ans = 0;
        for ( int i = 0; i < k; i++ )
            ans = ans + r[i] * init[i];
        return ans;
    }
};
