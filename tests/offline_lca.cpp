#include "../src/compact/offline_lca.hpp"
#include "../src/classic/offline_lca.hpp"
#include <iostream>
#include <random>
#include <pthread.h>

void check(int n, const vector<pair<int, int>> &edges)
{
    OfflineLCA a(n);
    static Offline_LCA<30> b;
    b.Init(n);
    vector<vector<int>> g(n + 1);
    for (auto [u, v] : edges)
    {
        a.add(u, v);
        b.Insert(u, v);
        g[u].push_back(v);
        g[v].push_back(u);
    }
    for (int u = n; u >= 1; u--)
        for (int v = 1; v <= n; v++)
            assert(a.add_query(u, v) == b.Add_Query(u, v));
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
        a.run(root);
        b.Run(root);
        assert(a.answer == b.answer);
        int id = 0;
        for (int u = n; u >= 1; u--)
            for (int v = 1; v <= n; v++)
            {
                int x = u, y = v;
                while (x != y)
                    if (depth[x] >= depth[y])
                        x = parent[x];
                    else
                        y = parent[y];
                assert(a.answer[id++] == x);
            }
        auto expected = a.answer;
        a.run(root);
        b.Run(root);
        assert(a.answer == expected && b.answer == expected);
    }
    int id = a.add_query(n, n);
    assert(b.Add_Query(n, n) == id);
    a.run();
    b.Run();
    assert(a.answer == b.answer && a.answer[id] == n);
    b.Init(n);
    for (auto [u, v] : edges)
        b.Insert(u, v);
    b.Run();
    assert(b.answer.empty());
}

void *large(void *)
{
    constexpr int n = 500000;
    OfflineLCA a(n);
    static Offline_LCA<n> b;
    b.Init(n);
    for (int u = 2; u <= n; u++)
    {
        a.add(u - 1, u);
        b.Insert(u - 1, u);
    }
    for (int u = 1; u <= n; u++)
    {
        a.add_query(u, n + 1 - u);
        b.Add_Query(u, n + 1 - u);
    }
    for (int root : {1, n, n / 2})
    {
        a.run(root);
        b.Run(root);
        assert(a.answer == b.answer);
        for (int u = 1; u <= n; u++)
        {
            int v = n + 1 - u;
            assert(a.answer[u - 1] == clamp(root, min(u, v), max(u, v)));
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
    cout << "Offline LCA dual exhaustive labelled trees, all roots/pairs, reset and 500000 recursive chain PASS\n";
}
