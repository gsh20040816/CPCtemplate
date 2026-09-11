#include "../src/compact/algebra.hpp"
#include "../src/classic/algebra.hpp"
#include <climits>
#include <iostream>
#include <map>
#include <random>
using ll = long long;
using I = __int128_t;

ll norm(ll a, ll m)
{
    return (I(a) % m + m) % m;
}

void check(ll a, ll b, ll m, ll want)
{
    assert(DiscreteLog::solve(a, b, m) == want);
    assert(Discrete_Log::Solve(a, b, m) == want);
}

int main()
{
    // All residues until the first repeat give every attainable target and its first index.
    for (int m = 1; m <= 130; m++)
        for (int a = 0; a < m; a++)
        {
            vector<ll> first(m, -1);
            int value = 1 % m;
            ll exponent = 0;
            while (first[value] == -1)
            {
                first[value] = exponent++;
                value = value * a % m;
            }
            for (int b = 0; b < m; b++)
                check(a, b, m, first[b]);
            if (a % 11 == 0)
                for (int b = 0; b < m; b++)
                    check(a - 3LL * m, b - 2LL * m, m, first[b]);
        }
    mt19937_64 rng(4195);
    vector<ll> values{LLONG_MIN, LLONG_MAX, -1, 0, 1};
    for (int it = 0; it < 2000; it++)
    {
        ll m = 1 + rng() % 2000;
        ll a = values[rng() % values.size()];
        ll b = values[rng() % values.size()];
        vector<ll> first(m, -1);
        ll value = 1 % m, exponent = 0;
        while (first[value] == -1)
        {
            first[value] = exponent++;
            value = I(value) * norm(a, m) % m;
        }
        check(a, b, m, first[norm(b, m)]);
    }
    constexpr ll big = 1000000000000LL;
    check(1, 1, big, 0);
    check(1, 2, big, -1);
    check(0, 0, big, 1);
    check(0, 1, big, 0);
    check(0, 2, big, -1);
    check(big - 1, big - 1, big, 1);
    check(big - 1, 2, big, -1);
    // A=5 has order 2^(k-2) modulo 2^k. Enumerating a prefix independently proves minimality.
    for (auto [a, m] : vector<pair<ll, ll>>{{5, 1LL << 39}, {2, big}, {10, big}, {6, 1000000000}})
    {
        map<ll, ll> first;
        ll value = 1 % m;
        for (int e = 0; e <= 1200; e++)
        {
            first.emplace(value, e);
            if (e == 12 || e == 517 || e == 1200)
                check(a, value, m, first[value]);
            value = I(value) * a % m;
        }
    }
    // Repeated calls must not carry baby steps or stripped gcd state into the next input.
    for (int it = 0; it < 100; it++)
    {
        check(4, 2, 8, -1);
        check(4, 0, 8, 2);
        check(2, 4, 8, 2);
        check(2, 0, 8, 3);
        check(123, 456, 1, 0);
    }
    cout << "exBSGS dual exhaustive first-occurrence oracle, signed inputs and 1e12 boundary PASS\n";
}
