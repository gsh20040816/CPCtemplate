#include "../src/compact/modular_sqrt.hpp"
#include "../src/classic/modular_sqrt.hpp"
#include <climits>
#include <iostream>
using ll = long long;
using I = __int128_t;

ll power(ll a, ll b, ll p)
{
    I result = 1;
    while (b)
    {
        if (b & 1)
            result = result * a % p;
        a = I(a) * a % p;
        b >>= 1;
    }
    return result;
}

void check(ll a, int p, const vector<ll> &want)
{
    assert(mod_sqrt(a, p) == want);
    assert(Mod_Sqrt(a, p) == want);
}

int main()
{
    for (int p = 2; p <= 2000; p++)
    {
        bool prime = true;
        for (int d = 2; d <= p / d; d++)
            if (p % d == 0)
                prime = false;
        if (!prime)
            continue;
        vector<vector<ll>> roots(p);
        for (int x = 0; x < p; x++)
            roots[x * x % p].push_back(x);
        for (int a = 0; a < p; a++)
        {
            check(a, p, roots[a]);
            check(a - ll(p) * 2, p, roots[a]);
        }
    }
    mt19937_64 rng(5491);
    for (int p : {998244353, 1000000007, 1000000009, 2147483629, INT_MAX})
    {
        for (int d = 2; d <= p / d; d++)
            assert(p % d != 0);
        for (int it = 0; it < 3000; it++)
        {
            ll x = rng() % p;
            ll a = I(x) * x % p;
            vector<ll> want{x};
            if (x)
            {
                want.push_back(p - x);
                sort(want.begin(), want.end());
            }
            check(a, p, want);
        }
        for (ll a : {LLONG_MIN, LLONG_MAX, -1LL, 0LL, 1LL})
        {
            ll normalized = (I(a) % p + p) % p;
            auto x = mod_sqrt(a, p);
            auto y = Mod_Sqrt(a, p);
            assert(x == y);
            bool exists = !normalized || power(normalized, (p - 1) / 2, p) == 1;
            assert(!x.empty() == exists);
            if (exists)
            {
                assert(x.size() == size_t(normalized ? 2 : 1));
                assert(is_sorted(x.begin(), x.end()));
                for (ll root : x)
                    assert(0 <= root && root < p && I(root) * root % p == normalized);
            }
        }
        for (int i = 0; i < 200; i++)
        {
            ll a = 1 + rng() % (p - 1);
            if (power(a, (p - 1) / 2, p) == p - 1)
                check(a, p, {});
        }
    }
    check(LLONG_MIN, 2, {0});
    check(LLONG_MAX, 2, {1});
    cout << "Modular sqrt dual exhaustive prime roots, planted large roots, nonresidues and int64 inputs PASS\n";
}
