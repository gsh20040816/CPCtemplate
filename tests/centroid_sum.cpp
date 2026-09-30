#include "../src/compact/centroid_sum.hpp"
#include <iostream>
#include <limits>
#include <pthread.h>
#include <queue>
#include <random>

using ll = long long;
std::mt19937 rng(63292026);

void check(int n, int shape)
{
    CentroidSum<ll> tree(n);
    std::vector<std::vector<int>> g(n);
    for (int v = 1; v < n; v++)
    {
        int p = shape == 0 ? v - 1 : shape == 1 ? 0 : shape == 2 ? (v - 1) / 2 : rng() % v;
        tree.add(p, v);
        g[p].push_back(v);
        g[v].push_back(p);
    }
    std::vector<std::vector<int>> dist(n, std::vector<int>(n, -1));
    for (int s = 0; s < n; s++)
    {
        std::queue<int> q;
        q.push(s);
        dist[s][s] = 0;
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            for (int v : g[u])
                if (dist[s][v] == -1)
                {
                    dist[s][v] = dist[s][u] + 1;
                    q.push(v);
                }
        }
    }
    for (int repeat = 0; repeat < 3; repeat++)
    {
        std::vector<ll> value(n);
        for (ll &x : value) x = ((ll)(rng() % 2001) - 1000) * 1000000000LL;
        tree.build(value);
        for (int step = 0; step < 200; step++)
        {
            int u = rng() % n;
            ll x = step % 4 ? (ll)(rng() % 2001) - 1000 : value[u];
            tree.set(u, x);
            value[u] = x;
            for (ll k : {-1LL, 0LL, (ll)(rng() % n), (ll)n, std::numeric_limits<ll>::max()})
            {
                ll expected = 0;
                for (int v = 0; v < n; v++)
                    if (dist[u][v] <= k) expected += value[v];
                assert(tree.query(u, k) == expected);
            }
            assert(tree.query(u, std::numeric_limits<ll>::min()) == 0);
        }
        for (int u = 0; u < n; u++)
            for (int k = 0; k <= n; k++)
            {
                ll expected = 0;
                for (int v = 0; v < n; v++)
                    if (dist[u][v] <= k) expected += value[v];
                assert(tree.query(u, k) == expected);
            }
    }
}

void stress(int shape)
{
    const int n = 100000;
    CentroidSum<ll> tree(n);
    for (int v = 1; v < n; v++)
    {
        int p = shape == 0 ? v - 1 : shape == 1 ? 0 : shape == 2 ? (v - 1) / 2 : rng() % v;
        tree.add(p, v);
    }
    std::vector<ll> values(n, 10000);
    tree.build(values);
    ll total = 10000LL * n;
    for (int step = 0; step < n; step++)
    {
        int u = rng() % n;
        ll x = (ll)(rng() % 20001) - 10000;
        total += x - values[u];
        values[u] = x;
        tree.set(u, x);
        assert(tree.query(u, 0) == x);
        assert(tree.query(u, n) == total);
        if (shape == 0)
        {
            int k = step % 10;
            ll expected = 0;
            for (int v = std::max(0, u - k); v <= std::min(n - 1, u + k); v++)
                expected += values[v];
            assert(tree.query(u, k) == expected);
        }
        if (shape == 1) assert(tree.query(u, 1) == (u ? values[u] + values[0] : total));
    }
    tree.build(std::vector<ll>(n, -7));
    assert(tree.query(n - 1, n) == -7LL * n);
    assert(tree.query(0, 0) == -7);
}

void *test_entry(void *)
{
    for (int shape = 0; shape < 4; shape++)
    {
        check(1, shape);
        for (int trial = 0; trial < 80; trial++) check(2 + rng() % 45, shape);
        stress(shape);
    }
    std::cout << "CentroidSum BFS/weight-scan oracle, rebuilds, signed values and four n=100000 topologies PASS\n";
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
