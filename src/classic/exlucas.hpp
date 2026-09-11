#pragma once
#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Ex_Lucas
{
    using ull = unsigned long long;
    using ll = long long;

    struct Factor
    {
        int p, q, exponent, start, crt;
    };

    int mod;
    int fac[N + 1], used;
    vector<Factor> factors;

    static ll Power(ll a, ull b, int m)
    {
        ll result = 1;
        while ( b )
        {
            if ( b & 1 )
                result = result * a % m;
            a = a * a % m;
            b >>= 1;
        }
        return result;
    }

    void Init(int m)
    {
        assert(1 <= m && m <= N);
        mod = m;
        used = 0;
        factors.clear();
        int x = m;
        for ( int p = 2; p <= x / p; p++ )
        {
            if ( x % p )
                continue;
            int q = 1, e = 0;
            do
            {
                x /= p;
                q *= p;
                e++;
            } while ( x % p == 0 );
            Add_Factor(p, q, e);
        }
        if ( x > 1 )
            Add_Factor(x, x, 1);
    }

    void Add_Factor(int p, int q, int e)
    {
        int start = used;
        fac[used++] = 1;
        for ( int i = 1; i < q; i++ )
        {
            fac[used] = ll(fac[used - 1]) * (i % p ? i : 1) % q;
            used++;
        }
        fac[used] = fac[used - 1];
        used++;
        int phi = q - q / p;
        int crt = ll(mod / q) * Power(mod / q % q, phi - 1, q) % mod;
        factors.push_back({p, q, e, start, crt});
    }

    static ull Valuation(ull n, int p)
    {
        ull result = 0;
        while ( n )
        {
            n /= p;
            result += n;
        }
        return result;
    }

    ll Unit(ull n, const Factor &f) const
    {
        ll result = 1;
        while ( n )
        {
            result = result * Power(fac[f.start + f.q], n / f.q, f.q) % f.q;
            result = result * fac[f.start + n % f.q] % f.q;
            n /= f.p;
        }
        return result;
    }

    int Choose(ull n, ull k) const
    {
        if ( k > n || mod == 1 )
            return 0;
        ll answer = 0;
        for ( const auto &f : factors )
        {
            ull e = Valuation(n, f.p) - Valuation(k, f.p) - Valuation(n - k, f.p);
            if ( e >= ull(f.exponent) )
                continue;
            ll denominator = Unit(k, f) * Unit(n - k, f) % f.q;
            ll residue =
                Unit(n, f) * Power(denominator, f.q - f.q / f.p - 1, f.q) % f.q;
            residue = residue * Power(f.p, e, f.q) % f.q;
            answer = (answer + residue * f.crt) % mod;
        }
        return answer;
    }
};
