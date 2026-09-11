#include "../src/compact/dsu_on_tree.hpp"
#include "../src/classic/dsu_on_tree.hpp"
#include <iostream>
#include <limits>
#include <map>
#include <random>
#include <pthread.h>

void test_all()
{
    std::mt19937 rng(531177);
    static Subtree_Colors<64> b;
    for (int trial = 0; trial < 1000; trial++)
    {
        int n = 1 + rng() % 64;
        SubtreeColors a(n);
        b.Init(n);
        std::vector<std::vector<int>> g(n + 1);
        for (int v = 2; v <= n; v++)
        {
            int u = 1 + rng() % (v - 1);
            a.add(u, v);
            b.Insert(u, v);
            g[u].push_back(v);
            g[v].push_back(u);
        }
        for (int repeat = 0; repeat < 2; repeat++)
        {
            int root = 1 + rng() % n;
            std::vector<int> c(n + 1), p(n + 1), q{root};
            for (int u = 1; u <= n; u++)
                c[u] = (int)(rng() % 9) - 4;
            if (repeat)
                c[root] = std::numeric_limits<int>::min();
            for (int i = 0; i < n; i++)
                for (int v : g[q[i]])
                    if (v != p[q[i]])
                    {
                        p[v] = q[i];
                        q.push_back(v);
                    }
            std::vector<std::map<int, int>> count(n + 1);
            for (int v = 1; v <= n; v++)
                for (int u = v; u; u = p[u])
                    count[u][c[v]]++;
            a.run(c, root);
            b.Run(c, root);
            for (int u = 1; u <= n; u++)
            {
                int best = 0;
                long long sum = 0;
                for (auto [color, freq] : count[u])
                    best = std::max(best, freq);
                for (auto [color, freq] : count[u])
                    if (freq == best)
                        sum += color;
                assert(a.max_freq[u] == best && b.max_freq[u] == best);
                assert(a.answer[u] == sum && b.answer[u] == sum);
            }
            assert(a.best == 0 && b.best == 0 && a.sum == 0 && b.sum == 0);
            for (int x : a.freq)
                assert(x == 0);
            for (int x : b.freq)
                assert(x == 0);
        }
    }
    const int n = 100000;
    SubtreeColors a(n);
    static Subtree_Colors<n> large;
    large.Init(n);
    for (int v = 2; v <= n; v++)
    {
        a.add(v - 1, v);
        large.Insert(v - 1, v);
    }
    std::vector<int> c(n + 1, -7);
    a.run(c);
    large.Run(c);
    for (int u = 1; u <= n; u++)
    {
        assert(a.answer[u] == -7 && large.answer[u] == -7);
        assert(a.max_freq[u] == n - u + 1 && large.max_freq[u] == n - u + 1);
    }
    SubtreeColors star(n);
    large.Init(n);
    for (int v = 2; v <= n; v++)
    {
        star.add(1, v);
        large.Insert(1, v);
    }
    for (int u = 1; u <= n; u++)
        c[u] = u;
    star.run(c);
    large.Run(c);
    assert(star.answer[1] == 1LL * n * (n + 1) / 2);
    assert(large.answer[1] == star.answer[1]);
    for (int u = 2; u <= n; u++)
        assert(star.answer[u] == u && large.answer[u] == u);
    SubtreeColors empty(0);
    empty.run({0});
    large.Init(0);
    large.Run({0});
    std::cout << "DSU-on-tree ancestor histogram, reroot/reset, recursive chain and star PASS\n";
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
