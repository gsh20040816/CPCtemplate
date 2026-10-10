#pragma once
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

// BEGIN BurnsideAverage
struct BurnsideAverage
{
    using ll = long long;
    ll order, mod, sum = 0;

    BurnsideAverage(ll g, ll p) : order(g)
    {
        assert(g > 0 && p > 0 && __int128(g) * p <= LLONG_MAX / 2);
        mod = g * p;
    }

    ll power(ll a, long long k) const
    {
        assert(a >= 0 && k >= 0);
        a %= mod;
        ll ans = 1 % mod;
        while (k)
        {
            if (k & 1) ans = __int128(ans) * a % mod;
            a = __int128(a) * a % mod;
            k >>= 1;
        }
        return ans;
    }

    void add(ll fixed, ll multiplicity = 1)
    {
        assert(fixed >= 0 && multiplicity >= 0);
        sum = (sum + __int128(fixed) * multiplicity) % mod;
    }

    ll result() const
    {
        assert(sum % order == 0);
        return sum / order;
    }
};
// END BurnsideAverage

// BEGIN permutation_cycles
vector<int> permutation_cycles(const vector<int> &p)
{
    int n = p.size();
    vector<int> seen(n), lengths;
    for (int i = 0; i < n; i++)
    {
        if (seen[i]) continue;
        int u = i, len = 0;
        do
        {
            seen[u] = 1;
            len++;
            u = p[u];
        } while (u != i);
        lengths.push_back(len);
    }
    return lengths;
}
// END permutation_cycles

// BEGIN necklace_colorings
long long necklace_colorings(int n, long long colors, long long mod,
                             bool reflection = false)
{
    assert(n >= 1 && colors >= 0);
    BurnsideAverage avg((reflection ? 2LL : 1LL) * n, mod);
    vector<int> primes;
    int x = n;
    for (int p = 2; p <= x / p; p++)
    {
        if (x % p != 0) continue;
        primes.push_back(p);
        while (x % p == 0) x /= p;
    }
    if (x > 1) primes.push_back(x);
    auto add = [&](int d)
    {
        long long phi = d;
        for (int p : primes)
        {
            if (d % p == 0) phi = phi / p * (p - 1);
        }
        avg.add(avg.power(colors, n / d), phi);
    };
    for (int d = 1; d <= n / d; d++)
    {
        if (n % d != 0) continue;
        add(d);
        if (d != n / d) add(n / d);
    }
    if (reflection)
    {
        if (n & 1) avg.add(avg.power(colors, n / 2 + 1), n);
        else
        {
            avg.add(avg.power(colors, n / 2), n / 2);
            avg.add(avg.power(colors, n / 2 + 1), n / 2);
        }
    }
    return avg.result();
}
// END necklace_colorings
