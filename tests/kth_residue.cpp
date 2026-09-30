#include "../src/compact/kth_residue.hpp"
#include "residue_oracle.hpp"
using U = unsigned long long;
using L = long long;

L power(L a, U k, L p)
{
    L x = a, result = 1;
    while (k)
    {
        if (k & 1) result = (__int128)result * x % p;
        x = (__int128)x * x % p;
        k >>= 1;
    }
    return result;
}

void check(L a, U k, L p, L g, bool enumerate)
{
    auto x = KthResidue::solve(a, k, p, g);
    if (!enumerate) assert(x);
    L target = a % p;
    if (target < 0) target += p;
    vector<L> want;
    if (enumerate)
        for (L i = 0; i < p; i++)
            if (power(i, k, p) == target) want.push_back(i);
    if (!x)
    {
        assert(!enumerate || want.empty());
        return;
    }
    assert(power(x->first, k, p) == target);
    assert(power(x->ratio, k, p) == 1);
    assert(x->count == (target == 0 ? 1 : gcd(U(p - 1), k)));
    if (enumerate)
    {
        vector<L> got;
        L v = x->first;
        for (L i = 0; i < x->count; i++)
        {
            got.push_back(v);
            v = (__int128)v * x->ratio % p;
        }
        sort(got.begin(), got.end());
        assert(got == want);
    }
}

int main()
{
    for (int p = 2; p < 100; p++)
    {
        bool prime = true;
        for (int d = 2; d * d <= p; d++)
            if (p % d == 0) prime = false;
        if (!prime) continue;
        auto roots = generators(p);
        for (int g : roots)
            for (U k = 1; k <= 10; k++)
                for (L a = -p; a <= p; a++) check(a, k, p, g, true);
        for (U k : {U(p - 1), U(p), ULLONG_MAX, U(1) << 63})
            for (L a : {LLONG_MIN, LLONG_MAX, L(0), L(1), L(-1)})
                check(a, k, p, roots[0], true);
    }
    L p = 998244353, g = 3;
    check(1, U(p - 1), p, g, false);
    auto all = KthResidue::solve(1, p - 1, p, g);
    assert(all && all->count == p - 1 && all->first == 1);
    assert(power(all->ratio, p - 1, p) == 1);
    for (L factor : {2, 7, 17}) assert(power(all->ratio, (p - 1) / factor, p) != 1);
    assert(!KthResidue::solve(g, p - 1, p, g));
    mt19937_64 rng(20260917);
    for (int t = 0; t < 30; t++)
    {
        U k = rng();
        if (!k) k = 1;
        L root = 1 + rng() % (p - 1), a = power(root, k, p);
        check(a, k, p, g, false);
    }
    L big = 999999999989LL;
    for (L d = 2; d <= big / d; d++) assert(big % d);
    L remaining = big - 1;
    vector<L> factors;
    for (L d = 2; d <= remaining / d; d++)
        if (remaining % d == 0)
        {
            factors.push_back(d);
            while (remaining % d == 0) remaining /= d;
        }
    if (remaining > 1) factors.push_back(remaining);
    L generator = 2;
    while (true)
    {
        bool good = true;
        for (L d : factors)
            if (power(generator, (big - 1) / d, big) == 1) good = false;
        if (good) break;
        generator++;
    }
    check(power(123456789, 6, big), 6, big, generator, false);
    cout
        << "Kth residue vector exhaustive root sets and primitive roots, signed/uint64 "
           "extremes, planted large roots and compressed 998244352 roots PASS\n";
}
