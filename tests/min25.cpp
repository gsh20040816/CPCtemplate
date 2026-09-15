#include "../src/compact/min25.hpp"

template <int P> void check(int n)
{
    using Z = ModInt<P>;
    Min25<P> sieve(n);
    vector<int> primes;
    for (int p = 2; p <= n; p++)
    {
        bool prime = true;
        for (int d = 2; d <= p / d; d++)
            if (p % d == 0) prime = false;
        if (prime) primes.push_back(p);
    }
    for (int k = 0; k < (int)sieve.w.size(); k++)
    {
        array<Z, 3> want{};
        for (int p : primes)
            if (p <= sieve.w[k])
            {
                want[0] = want[0] + 1;
                want[1] = want[1] + p;
                want[2] = want[2] + Z(p) * p;
            }
        for (int d = 0; d < 3; d++) assert(sieve.g[k][d].v == want[d].v);
    }
    array<array<Z, 3>, 7> c{{{1, 0, 0},
                             {0, 1, 0},
                             {-1, 1, 0},
                             {-1, 0, 0},
                             {2, 0, 0},
                             {0, -1, 1},
                             {3, 7, 0}}};
    for (int kind = 0; kind < 7; kind++)
    {
        auto power = [&](long long p, int e, long long pe) -> Z
        {
            if (kind == 0) return 1;
            if (kind == 1) return pe;
            if (kind == 2) return pe - pe / p;
            if (kind == 3) return e == 1 ? -1 : 0;
            if (kind == 4) return e + 1;
            if (kind == 5) return Z(pe) * (Z(pe) - 1);
            return Z(3) * e + Z(7) * p;
        };
        Z want = 1;
        for (int x = 2; x <= n; x++)
        {
            int v = x;
            Z f = 1;
            for (int p = 2; p <= v; p++)
                if (v % p == 0)
                {
                    int e = 0, pe = 1;
                    while (v % p == 0)
                    {
                        v /= p;
                        pe *= p;
                        e++;
                    }
                    f = f * power(p, e, pe);
                }
            want = want + f;
        }
        assert(sieve.sum(c[kind], power).v == want.v);
    }
}

int main()
{
    for (int n = 1; n <= 300; n++)
    {
        check<5>(n);
        check<1000000007>(n);
    }
    mt19937 rng(5325);
    for (int t = 0; t < 80; t++) check<469762049>(1 + rng() % 5000);
    using Z = ModInt<1000000007>;
    long long n = 1000000000;
    Min25<1000000007> large(n);
    assert(large.sum({1, 0, 0}, [](long long, int, long long) { return Z(1); }).v == n);
    Z expected = Z(n) * Z(n + 1) / Z(2);
    assert(large.sum({0, 1, 0}, [](long long, int, long long pe) { return Z(pe); }).v ==
           expected.v);
    cout << "Min25: all quotient prime moments; 7 independent factorization families "
            "over mod5/469762049/1e9+7, all n<=300 and 80 random n<=5000; repeated "
            "sums and n=1e9 identities PASS\n";
}
