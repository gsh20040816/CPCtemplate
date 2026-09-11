#include "../src/compact/euler_lca.hpp"
#include "../src/classic/euler_lca.hpp"
#include <iostream>
#include <random>
#include <pthread.h>

void check(int n, const vector<pair<int, int>> &edges)
{
    EulerLCA a(n);
    static Euler_LCA<30, 6> b;
    b.Init(n);
    vector<vector<int>> g(n + 1);
    for (auto [u, v] : edges)
    {
        a.add(u, v);
        b.Insert(u, v);
        assert(!a.ready && !b.ready);
        g[u].push_back(v);
        g[v].push_back(u);
    }
    for (int root = 1; root <= n; root++)
    {
        vector<int> parent(n + 1, -1), depth(n + 1), queue{root};
        parent[root] = 0;
        for (int i = 0; i < (int)queue.size(); i++)
            for (int v : g[queue[i]])
                if (parent[v] == -1)
                {
                    parent[v] = queue[i];
                    depth[v] = depth[queue[i]] + 1;
                    queue.push_back(v);
                }
        for (int repeat = 0; repeat < 2; repeat++)
        {
            a.build(root);
            b.Build(root);
            assert(a.euler.size() == (size_t)(2 * n - 1));
            assert(a.euler == b.euler);
            for (int u = 1; u <= n; u++)
            {
                assert(a.first[u] == b.first[u]);
                assert(a.euler[a.first[u]] == u);
                assert(a.first[u] == find(a.euler.begin(), a.euler.end(), u) - a.euler.begin());
                for (int v = 1; v <= n; v++)
                {
                    int x = u, y = v;
                    while (x != y)
                        if (depth[x] >= depth[y])
                            x = parent[x];
                        else
                            y = parent[y];
                    assert(a.lca(u, v) == x && b.Lca(u, v) == x);
                    int distance = depth[u] + depth[v] - 2 * depth[x];
                    assert(a.distance(u, v) == distance && b.Distance(u, v) == distance);
                }
            }
        }
    }
    b.Init(1);
    b.Build();
    assert(b.Lca(1, 1) == 1 && b.Distance(1, 1) == 0);
}

void *large(void *)
{
    constexpr int n = 500000;
    EulerLCA a(n);
    static Euler_LCA<n> b;
    b.Init(n);
    for (int u = 2; u <= n; u++)
    {
        a.add(u - 1, u);
        b.Insert(u - 1, u);
    }
    for (int root : {1, n, n / 2})
    {
        a.build(root);
        b.Build(root);
        for (int u = 1; u <= n; u++)
        {
            int v = n + 1 - u;
            int expected = clamp(root, min(u, v), max(u, v));
            assert(a.lca(u, v) == expected && b.Lca(u, v) == expected);
            assert(a.distance(u, v) == abs(u - v));
            assert(b.Distance(u, v) == abs(u - v));
        }
    }
    return nullptr;
}

int main()
{
    // Every labelled tree through n=6, via Prufer sequences.
    for (int n = 1; n <= 6; n++)
    {
        int count = 1;
        for (int i = 0; i < n - 2; i++)
            count *= n;
        for (int code = 0; code < count; code++)
        {
            vector<int> sequence, degree(n + 1, 1);
            int value = code;
            for (int i = 0; i < n - 2; i++)
            {
                int u = value % n + 1;
                value /= n;
                sequence.push_back(u);
                degree[u]++;
            }
            vector<pair<int, int>> edges;
            for (int u : sequence)
            {
                int v = 1;
                while (degree[v] != 1)
                    v++;
                edges.push_back({u, v});
                degree[u]--;
                degree[v]--;
            }
            if (n >= 2)
            {
                int u = 1, v = n;
                while (degree[u] != 1)
                    u++;
                while (degree[v] != 1)
                    v--;
                edges.push_back({u, v});
            }
            check(n, edges);
        }
    }
    mt19937 rng(3379);
    for (int t = 0; t < 300; t++)
    {
        int n = rng() % 30 + 1;
        vector<pair<int, int>> edges;
        for (int u = 2; u <= n; u++)
            edges.push_back({u, (int)(rng() % (u - 1)) + 1});
        shuffle(edges.begin(), edges.end(), rng);
        check(n, edges);
    }
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 512ULL << 20) == 0);
    pthread_t worker;
    assert(pthread_create(&worker, &attr, large, nullptr) == 0);
    assert(pthread_join(worker, nullptr) == 0);
    pthread_attr_destroy(&attr);
    cout << "Euler LCA dual exhaustive labelled trees, all roots/pairs, distances, rebuild and 500000 recursive chain PASS\n";
}
