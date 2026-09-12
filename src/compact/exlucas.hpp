#pragma once
#include <cassert>
#include <vector>
using namespace std;

struct ExLucas
{
    using ull = unsigned long long;
    using ll = long long;

    struct Factor
    {
        int p, q, exponent, start, crt;
    };

    int mod;
    vector<int> fac;
    vector<Factor> factors;

    static ll power(ll a, ull b, int m)
    {
        ll result = 1;
        while (b)
        {
            if (b & 1) result = result * a % m;
            a = a * a % m;
            b >>= 1;
        }
        return result;
    }

    ExLucas(int m) : mod(m)
    {
        assert(m >= 1);
        int x = m;
        for (int p = 2; p <= x / p; p++)
        {
            if (x % p) continue;
            int q = 1, e = 0;
            do
            {
                x /= p;
                q *= p;
                e++;
            } while (x % p == 0);
            add_factor(p, q, e);
        }
        if (x > 1) add_factor(x, x, 1);
    }

    void add_factor(int p, int q, int e)
    {
        int start = fac.size();
        fac.push_back(1);
        for (int i = 1; i < q; i++) fac.push_back(ll(fac.back()) * (i % p ? i : 1) % q);
        fac.push_back(fac.back());
        int phi = q - q / p;
        int crt = ll(mod / q) * power(mod / q % q, phi - 1, q) % mod;
        factors.push_back({p, q, e, start, crt});
    }

    static ull valuation(ull n, int p)
    {
        ull result = 0;
        while (n)
        {
            n /= p;
            result += n;
        }
        return result;
    }

    ll unit(ull n, const Factor &f) const
    {
        ll result = 1;
        while (n)
        {
            result = result * power(fac[f.start + f.q], n / f.q, f.q) % f.q;
            result = result * fac[f.start + n % f.q] % f.q;
            n /= f.p;
        }
        return result;
    }

    int choose(ull n, ull k) const
    {
        if (k > n || mod == 1) return 0;
        ll answer = 0;
        for (const auto &f : factors)
        {
            ull e = valuation(n, f.p) - valuation(k, f.p) - valuation(n - k, f.p);
            if (e >= ull(f.exponent)) continue;
            ll denominator = unit(k, f) * unit(n - k, f) % f.q;
            ll residue =
                unit(n, f) * power(denominator, f.q - f.q / f.p - 1, f.q) % f.q;
            residue = residue * power(f.p, e, f.q) % f.q;
            answer = (answer + residue * f.crt) % mod;
        }
        return answer;
    }
};
