#include "../src/compact/interpolation.hpp"
#include <climits>
#include <iostream>
#include <random>

// Direct polynomial evaluation and the general Lagrange struct as independent references.
using ll = long long;
mt19937_64 rng(23);

ll eval(const vector<ll> &c, ll x, ll p)
{
    __int128 r = 0, xx = (x % p + p) % p;
    for (int i = (int)c.size() - 1; i >= 0; i--) r = (r * xx + c[i]) % p;
    return (ll)r;
}

int main()
{
    long long checks = 0;
    for (int p : {2, 3, 5, 7, 13, 998244353, 1000000007, INT_MAX})
        for (int it = 0; it < 300; it++)
        {
            int n = rng() % (min<ll>(p, 40) + 1);
            vector<ll> c(n);
            for (auto &x : c) x = rng() % p;
            vector<ll> ys(n), xs(n);
            for (int i = 0; i < n; i++) xs[i] = i, ys[i] = eval(c, i, p) + (ll)(rng() % 3) * p - p; // unnormalised inputs
            Lagrange general(xs, ys, p);
            for (int q = 0; q < 20; q++)
            {
                ll k = q < 4 ? (ll)(rng() % max(n, 1)) : q < 6 ? (q == 4 ? LLONG_MIN : LLONG_MAX) : (ll)rng();
                ll got = lagrange_consecutive(ys, k, p);
                assert(got == (n ? eval(c, k, p) : 0));
                assert(got == general.query(k));
                checks++;
            }
        }
    // power sums 1^d + ... + k^d from d+2 samples
    const int p = 1000000007;
    for (int d = 0; d <= 12; d++)
    {
        vector<ll> ys(d + 2);
        for (int i = 1; i < d + 2; i++)
        {
            ll t = 1;
            for (int j = 0; j < d; j++) t = t * i % p;
            ys[i] = (ys[i - 1] + t) % p;
        }
        ll brute = 0;
        for (ll k = 0; k <= 300; k++)
        {
            if (k)
            {
                ll t = 1;
                for (int j = 0; j < d; j++) t = t * k % p;
                brute = (brute + t) % p;
            }
            assert(lagrange_consecutive(ys, k, p) == brute);
            checks++;
        }
    }
    assert(lagrange_consecutive({}, 5, 7) == 0);
    cout << "Consecutive Lagrange: random polynomials over 8 primes incl. n=p and full ll k, "
            "general-struct agreement and power sums PASS (" << checks << " checks)\n";
}
