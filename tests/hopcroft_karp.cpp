#include "../src/compact/graph.hpp"
#include "../src/classic/graph.hpp"
#include <iostream>
#include <random>
#include <pthread.h>

int brute(int n, int m, const std::vector<std::pair<int, int>> &edges)
{
    std::vector<std::vector<int>> g(n + 1);
    for (auto [u, v] : edges)
        g[u].push_back(v - 1);
    std::vector<int> dp(1 << m, -1);
    dp[0] = 0;
    for (int u = 1; u <= n; u++)
    {
        auto next = dp;
        for (int mask = 0; mask < (1 << m); mask++)
            if (dp[mask] >= 0)
                for (int v : g[u])
                    if (!(mask >> v & 1))
                        next[mask | (1 << v)] =
                            std::max(next[mask | (1 << v)], dp[mask] + 1);
        dp.swap(next);
    }
    return *std::max_element(dp.begin(), dp.end());
}

void check(int n, int m, const std::vector<std::pair<int, int>> &edges)
{
    BipartiteMatching a(n, m);
    static Bipartite_Matching<8, 8> b;
    b.Init(n, m);
    std::vector<std::pair<int, int>> current;
    auto verify = [&](const auto &left, const auto &right, auto cover, int expected)
    {
        int count = 0;
        std::vector<int> cl(n + 1), cr(m + 1);
        for (int u : cover.first)
        {
            assert(1 <= u && u <= n && !cl[u]);
            cl[u] = 1;
        }
        for (int v : cover.second)
        {
            assert(1 <= v && v <= m && !cr[v]);
            cr[v] = 1;
        }
        assert((int)(cover.first.size() + cover.second.size()) == expected);
        for (auto [u, v] : current)
            assert(cl[u] || cr[v]);
        for (int u = 1; u <= n; u++)
        {
            if (!left[u])
                continue;
            int v = left[u];
            assert(1 <= v && v <= m && right[v] == u);
            assert(std::find(current.begin(), current.end(), std::pair{u, v}) !=
                   current.end());
            count++;
        }
        for (int v = 1; v <= m; v++)
            if (right[v])
                assert(left[right[v]] == v);
        assert(count == expected);
    };
    for (int stage = 0; stage < 2; stage++)
    {
        int target = stage ? edges.size() : edges.size() / 2;
        while ((int)current.size() < target)
        {
            auto [u, v] = edges[current.size()];
            current.push_back({u, v});
            a.add(u, v);
            b.Insert(u, v);
        }
        int expected = brute(n, m, current);
        assert(a.solve() == expected && b.Solve() == expected);
        verify(a.l, a.r, a.cover(), expected);
        verify(b.l, b.r, b.Cover(), expected);
        assert(a.solve() == expected && b.Solve() == expected);
    }
}

void test_all()
{
    for (int n = 0; n <= 4; n++)
        for (int m = 0; m <= 4; m++)
            for (unsigned mask = 0; mask < (1U << (n * m)); mask++)
            {
                std::vector<std::pair<int, int>> edges;
                for (int u = 1; u <= n; u++)
                    for (int v = 1; v <= m; v++)
                        if (mask >> ((u - 1) * m + v - 1) & 1)
                            edges.push_back({u, v});
                check(n, m, edges);
            }
    std::mt19937 rng(619773);
    for (int trial = 0; trial < 1000; trial++)
    {
        int n = 1 + rng() % 8, m = 1 + rng() % 8;
        std::vector<std::pair<int, int>> edges;
        for (int i = rng() % 70; i; i--)
            edges.push_back({1 + rng() % n, 1 + rng() % m});
        check(n, m, edges);
    }
    const int n = 100000;
    BipartiteMatching a(n, n);
    static Bipartite_Matching<n, n> b;
    b.Init(n, n);
    for (int u = 1; u < n; u++)
    {
        a.add(u, u + 1);
        b.Insert(u, u + 1);
    }
    assert(a.solve() == n - 1 && b.Solve() == n - 1);
    for (int u = 1; u <= n; u++)
    {
        a.add(u, u);
        b.Insert(u, u);
    }
    assert(a.bfs() && b.Bfs());
    assert(a.dep[0] == n && b.dep[0] == n);
    assert(a.solve() == n && b.Solve() == n);
    for (int u = 1; u <= n; u++)
        assert(a.l[u] == u && b.l[u] == u);
    assert(a.cover().first.size() == n && b.Cover().first.size() == n);
    std::cout << "Hopcroft-Karp exhaustive matching/cover, incremental edges and long "
                 "layered path PASS\n";
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
