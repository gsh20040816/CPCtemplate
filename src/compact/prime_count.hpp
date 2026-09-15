#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN prime_count
long long prime_count(long long n)
{
    assert(0 <= n && n <= 1000000000000LL);
    if (n < 2) return 0;
    int s = sqrtl(n);
    while (1LL * (s + 1) * (s + 1) <= n) s++;
    while (1LL * s * s > n) s--;
    vector<long long> w, g;
    vector<int> small(s + 1), large(s + 1);
    for (long long l = 1, r; l <= n; l = r + 1)
    {
        long long x = n / l;
        r = n / x;
        int id = w.size();
        if (x <= s)
            small[x] = id;
        else
            large[n / x] = id;
        w.push_back(x);
        g.push_back(x - 1);
    }
    auto id = [&](long long x)
    {
        return x <= s ? small[x] : large[n / x];
    };
    for (int p = 2; p <= s; p++)
    {
        long long before = g[id(p - 1)];
        if (g[id(p)] == before) continue;
        for (int j = 0; j < (int)w.size() && 1LL * p * p <= w[j]; j++)
            g[j] -= g[id(w[j] / p)] - before;
    }
    return g[0];
}

// END prime_count
