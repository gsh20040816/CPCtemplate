#include "../src/compact/algebra.hpp"
#include <cassert>
#include <iostream>
#include <random>

int main()
{
    const int n = 200000;
    vector<long long> pmu(n + 1), pphi(n + 1);
    // Independent trial factorization, not the linear sieve used by DuJiao.
    for (int x = 1; x <= n; x++)
    {
        int value = x, mu = 1, phi = x;
        for (int p = 2; p <= value / p; p++)
            if (value % p == 0)
            {
                phi = phi / p * (p - 1);
                int exponent = 0;
                while (value % p == 0)
                {
                    value /= p;
                    exponent++;
                }
                mu = exponent > 1 ? 0 : -mu;
            }
        if (value > 1)
        {
            phi = phi / value * (value - 1);
            mu = -mu;
        }
        pmu[x] = pmu[x - 1] + mu;
        pphi[x] = pphi[x - 1] + phi;
    }
    for (int limit : {1, 7, 64, 1000})
    {
        DuJiao a(limit);
        vector<int> queries;
        for (int x = 0; x <= 1000; x++) queries.push_back(x);
        mt19937 rng(limit);
        for (int i = 0; i < 200; i++) queries.push_back(rng() % (n + 1));
        queries.push_back(n);
        shuffle(queries.begin(), queries.end(), rng);
        for (int x : queries)
        {
            assert(a.mertens(x) == pmu[x]);
            assert(a.totient_sum(x) == pphi[x]);
        }
        auto am = a.mmu;
        auto ap = a.mphi;
        for (int x : queries)
        {
            assert(a.mertens(x) == pmu[x]);
            assert(a.totient_sum(x) == pphi[x]);
        }
        assert(a.mmu == am && a.mphi == ap);
        assert(a.mmu.count(n) && a.mphi.count(n));
        a.mmu.clear();
        a.mphi.clear();
        assert(a.mertens(n) == pmu[n] && a.totient_sum(n) == pphi[n]);
    }
    // Cutoff independence at the documented upper bound: consistency, not a separate
    // oracle.
    {
        DuJiao a(1000000);
        DuJiao b(2000000);
        const long long top = 100000000000LL;
        assert(a.mertens(top) == b.mertens(top));
        assert(a.totient_sum(top) == b.totient_sum(top));
        assert(a.mmu.count(top) && a.mphi.count(top));
        auto m = a.mertens(top);
        auto phi = a.totient_sum(top);
        assert(-top <= m && m <= top);
        assert(phi >= 1 && phi <= __int128_t(top) * (top + 1) / 2);
    }
    cout << "DuJiao current vector trial-prefix oracle, zero/cutoff boundaries, "
            "shuffled/repeated queries, cache rebuild and 1e11 cutoff consistency "
            "PASS\n";
}
