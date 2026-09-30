#include "../src/compact/composite_roots.hpp"
using L = long long;

L power(L a, unsigned long long k, L m)
{
    L x = a, y = 1 % m;
    while (k)
    {
        if (k & 1) y = (__int128)y * x % m;
        x = (__int128)x * x % m;
        k >>= 1;
    }
    return y;
}

vector<L> trial(L n)
{
    vector<L> f;
    for (L d = 2; d <= n / d; d++)
        while (n % d == 0)
        {
            f.push_back(d);
            n /= d;
        }
    if (n > 1) f.push_back(n);
    return f;
}

void certify(L mod)
{
    PollardRho rho(1);
    auto a = root_factors(mod, rho);
    vector<L> flat;
    L product = 1;
    for (auto [p, e, g] : a)
    {
        L m = 1;
        for (int i = 0; i < e; i++)
        {
            m *= p;
            flat.push_back(p);
        }
        product *= m;
        if (p == 2)
            assert(g == 0);
        else
        {
            assert(gcd(g, m) == 1);
            L phi = m / p * (p - 1);
            assert(power(g, phi, m) == 1);
            for (L d : trial(phi)) assert(power(g, phi / d, m) != 1);
            if (m < 300)
                for (L h = 1; h < g; h++)
                {
                    set<L> values;
                    L x = 1;
                    for (L i = 0; i < phi; i++)
                    {
                        values.insert(x);
                        x = x * h % m;
                    }
                    assert((L)values.size() != phi);
                }
        }
    }
    assert(product == mod && flat == trial(mod));
}

int main()
{
    for (int m = 1; m <= 500; m++) certify(m);
    for (L m : {999999999989LL,
                1000000000000LL,
                999983LL * 999979LL,
                (1LL << 39),
                3486784401LL})
        certify(m);
    PollardRho rho(3);
    for (int m = 1; m <= 80; m++)
        for (unsigned long long k = 1; k <= 8; k++)
            for (L a = 0; a < m; a++)
            {
                vector<L> want, got;
                for (L x = 0; x < m; x++)
                    if (power(x, k, m) == a) want.push_back(x);
                auto x = CompositeRoots::solve(a, k, m, rho);
                if (!x)
                    assert(want.empty());
                else
                {
                    for (L i = 0; i < x->total; i++)
                    {
                        L v = x->get(i);
                        assert(0 <= v && v < m);
                        got.push_back(v);
                    }
                    sort(got.begin(), got.end());
                    assert(got == want);
                }
            }
    cout << "Root preparation vector trial factorization, primitive-order "
            "certificates, trillion bounds and end-to-end composite root sets PASS\n";
}
