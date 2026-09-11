#include "../src/compact/centroid.hpp"
#include "../src/classic/centroid.hpp"
#include <iostream>
#include <random>
#include <tuple>
#include <pthread.h>

using ll = long long;
using Edge = std::tuple<int, int, ll>;
void check(int n, const std::vector<Edge> &edges)
{
    CentroidPairs a(n);
    static Centroid_Pairs<64> b;
    b.Init(n);
    using I = __int128_t;
    const I inf = I(1) << 100;
    std::vector<std::vector<I>> d(n + 1, std::vector<I>(n + 1, inf));
    for (int u = 1; u <= n; u++)
        d[u][u] = 0;
    for (auto [u, v, w] : edges)
    {
        a.add(u, v, w);
        b.Insert(u, v, w);
        d[u][v] = d[v][u] = w;
    }
    for (int k = 1; k <= n; k++)
        for (int u = 1; u <= n; u++)
            for (int v = 1; v <= n; v++)
                d[u][v] = std::min(d[u][v], d[u][k] + d[k][v]);
    std::vector<ll> queries{-1, 0, 1, 10, 20, 100, 1000, std::numeric_limits<ll>::max()};
    for (int u = 1; u <= n; u++)
        for (int v = u + 1; v <= n; v++)
            if (d[u][v] != inf)
                queries.push_back((ll)d[u][v]);
    for (int repeat = 0; repeat < 2; repeat++)
    {
        a.build();
        b.Build();
        for (ll k : queries)
        {
            ll leq = 0, exact = 0;
            for (int u = 1; u <= n; u++)
                for (int v = u + 1; v <= n; v++)
                {
                    leq += d[u][v] <= k;
                    exact += d[u][v] == k;
                }
            assert(a.count_leq(k) == leq && b.Count_Leq(k) == leq);
            assert(a.count_exact(k) == exact && b.Count_Exact(k) == exact);
        }
    }
}

void test_all()
{
    check(0, {});
    check(1, {});
    check(5, {{1, 2, std::numeric_limits<ll>::max()}, {2, 3, 0}, {1, 4, 0}, {1, 5, 0}});
    std::mt19937 rng(487782);
    for (int trial = 0; trial < 500; trial++)
    {
        int n = 1 + rng() % 35;
        std::vector<Edge> edges;
        for (int v = 2; v <= n; v++)
            if (rng() % 5)
                edges.push_back({1 + rng() % (v - 1), v, rng() % 11});
        check(n, edges);
    }
    const int n = 100000;
    CentroidPairs a(n);
    static Centroid_Pairs<n> b;
    b.Init(n);
    for (int v = 2; v <= n; v++)
    {
        a.add(v - 1, v, 1);
        b.Insert(v - 1, v, 1);
    }
    a.build();
    b.Build();
    for (ll k : {0LL, 1LL, 123LL, (ll)n, std::numeric_limits<ll>::max()})
    {
        ll t = std::min(k, (ll)n - 1);
        ll expected = t * n - t * (t + 1) / 2;
        assert(a.count_leq(k) == expected && b.Count_Leq(k) == expected);
    }
    CentroidPairs star(n);
    b.Init(n);
    for (int v = 2; v <= n; v++)
    {
        star.add(1, v, 0);
        b.Insert(1, v, 0);
    }
    star.build();
    b.Build();
    assert(star.count_exact(0) == 1LL * n * (n - 1) / 2);
    assert(b.Count_Exact(0) == star.count_exact(0));
    std::cout << "Centroid distance/Floyd oracle, zero weights, overflow boundary and recursive chain PASS\n";
}

void *test_entry(void *)
{
    test_all();
    return nullptr;
}

int main()
{
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 256ULL << 20) == 0);
    pthread_t thread;
    assert(pthread_create(&thread, &attr, test_entry, nullptr) == 0);
    assert(pthread_attr_destroy(&attr) == 0);
    assert(pthread_join(thread, nullptr) == 0);
}
