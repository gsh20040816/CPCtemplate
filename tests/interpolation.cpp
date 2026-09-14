#include "../src/compact/interpolation.hpp"
#include "../src/classic/interpolation.hpp"
#include <algorithm>
#include <climits>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
using ll = long long;
using I = __int128_t;

ll normalize(I x, int p)
{
    return (x % p + p) % p;
}

ll horner(const vector<ll> &c, ll x, int p)
{
    I result = 0;
    for (int i = int(c.size()) - 1; i >= 0; i--)
        result = normalize(result * normalize(x, p) + c[i], p);
    return result;
}

void check(const vector<ll> &c, const vector<ll> &xs, int p)
{
    Lagrange_Interpolation<100> classic;
    vector<ll> y, consecutive;
    for (ll x : xs)
        y.push_back(horner(c, x, p));
    for (int i = 0; i < int(xs.size()); i++)
        consecutive.push_back(horner(c, i, p));
    Lagrange a(xs, y, p);
    Lagrange b(consecutive, p);
    classic.Init(xs, y, p);
    vector<ll> queries = xs;
    for (int x = -7; x <= 12; x++)
        queries.push_back(x);
    queries.insert(queries.end(), {LLONG_MIN, LLONG_MAX, p, -ll(p), ll(p) * 3});
    for (ll x : queries)
    {
        ll want = horner(c, x, p);
        assert(a.query(x) == want);
        assert(b.query(x) == want);
        assert(classic.Query(x) == want);
    }
    classic.Consecutive(consecutive, p);
    for (ll x : queries)
        assert(classic.Query(x) == horner(c, x, p));
    classic.Init({}, {}, p);
    assert(classic.Query(LLONG_MIN) == 0);
    a = Lagrange({}, p);
    assert(a.query(LLONG_MAX) == 0);
}

int main()
{
    for (int p : {2, 3, 5})
        for (int mask = 0; mask < (1 << p); mask++)
        {
            vector<ll> xs;
            for (int x = 0; x < p; x++)
                if (mask >> x & 1)
                    xs.push_back(x - p);
            int count = 1;
            for (int i = 0; i < int(xs.size()); i++)
                count *= p;
            for (int code = 0; code < count; code++)
            {
                vector<ll> c(xs.size());
                int value = code;
                for (auto &x : c)
                {
                    x = value % p;
                    value /= p;
                }
                check(c, xs, p);
            }
        }
    mt19937_64 rng(4781);
    for (int p : {97, 998244353, 1000000007, INT_MAX})
        for (int it = 0; it < 120; it++)
        {
            int n = 1 + rng() % 30;
            vector<ll> c(n), xs;
            for (auto &x : c)
                x = rng() % p;
            set<ll> residues;
            while (int(xs.size()) < n)
            {
                ll x = rng() % p;
                if (residues.insert(x).second)
                    xs.push_back(x - ll(p) * 2);
            }
            check(c, xs, p);
        }
    // Input normalization itself: signed extremes in both coordinates and values.
    Lagrange_Interpolation<4> b;
    vector<ll> xs{LLONG_MIN, LLONG_MAX}, ys{LLONG_MAX, LLONG_MIN};
    Lagrange a(xs, ys, 998244353);
    b.Init(xs, ys, 998244353);
    for (int i = 0; i < 2; i++)
    {
        assert(a.query(xs[i]) == normalize(ys[i], 998244353));
        assert(b.Query(xs[i]) == normalize(ys[i], 998244353));
    }
    // WIDA application: sum of d-th powers, including points shifted by the modulus.
    for (int p : {7, 97, 998244353})
        for (int d = 0; d <= min(p - 2, 20); d++)
        {
            vector<ll> sums(401);
            for (int i = 1; i <= 400; i++)
            {
                I term = 1;
                for (int k = 0; k < d; k++)
                    term = term * i % p;
                sums[i] = (sums[i - 1] + term) % p;
            }
            vector<ll> y(sums.begin(), sums.begin() + d + 2);
            Lagrange_Interpolation<22> classic;
            Lagrange dynamic(y, p);
            classic.Consecutive(y, p);
            for (int n = 0; n <= 400; n++)
            {
                assert(dynamic.query(n) == sums[n]);
                assert(classic.Query(n) == sums[n]);
            }
        }
    // General 2000-point construction and linear 200000-point construction.
    vector<ll> x(2000), y(2000);
    iota(x.begin(), x.end(), 0);
    for (int i = 0; i < 2000; i++)
        y[i] = (ll(i) * i + i + 7) % 998244353;
    a = Lagrange(x, y, 998244353);
    assert(a.query(123456789) == horner({7, 1, 1}, 123456789, 998244353));
    y.resize(200000);
    for (int i = 0; i < 200000; i++)
        y[i] = (ll(i) * i + i + 7) % 998244353;
    static Lagrange_Interpolation<200000> large;
    a = Lagrange(y, 998244353);
    large.Consecutive(y, 998244353);
    assert(a.query(123456789) == horner({7, 1, 1}, 123456789, 998244353));
    assert(large.Query(123456789) == a.query(123456789));
    cout << "Lagrange dual exhaustive fields, Horner oracle, power sums and large consecutive nodes PASS\n";
}
