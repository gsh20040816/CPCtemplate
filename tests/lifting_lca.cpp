#include "../src/compact/lifting_lca.hpp"
#include "../src/classic/lifting_lca.hpp"
#include "../src/compact/tree.hpp"
#include "../src/classic/tree.hpp"
#include <iostream>
#include <climits>
#include <random>
#include <pthread.h>

void check(int n, const vector<pair<int, int>> &edges)
{
    LiftingLCA a(n);
    static Lifting_LCA<30, 6> b;
    b.Init(n);
    HLD c(n);
    static Heavy_Light_Decomposition<30> d;
    d.Init(n);
    vector<vector<int>> g(n + 1);
    vector<vector<long long>> weight(n + 1, vector<long long>(n + 1));
    int index = 0;
    for (auto [u, v] : edges)
    {
        long long choices[] = {LLONG_MIN, LLONG_MAX, -17, -1, 0, 23};
        long long w = choices[index++ % 6];
        weight[u][v] = weight[v][u] = w;
        a.add(u, v, w);
        b.Insert(u, v, w);
        c.add(u, v);
        d.Insert(u, v);
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
            c.build(root);
            d.Build(root);
            for (int u = 1; u <= n; u++)
            {
                int ancestor = u;
                for (int steps = 0; steps <= n + 1; steps++)
                {
                    assert(a.jump(u, steps) == ancestor);
                    assert(b.Jump(u, steps) == ancestor);
                    ancestor = parent[ancestor];
                    if (ancestor < 0)
                        ancestor = 0;
                }
                assert(a.jump(u, LLONG_MAX) == 0 && b.Jump(u, LLONG_MAX) == 0);
                for (int v = 1; v <= n; v++)
                {
                    int x = u, y = v;
                    optional<long long> maximum;
                    while (x != y)
                    {
                        int &z = depth[x] >= depth[y] ? x : y;
                        long long w = weight[z][parent[z]];
                        maximum = maximum ? max(*maximum, w) : w;
                        z = parent[z];
                    }
                    assert(a.max_edge(u, v) == maximum && b.Max_Edge(u, v) == maximum);
                    assert(a.lca(u, v) == x && b.Lca(u, v) == x);
                    int distance = depth[u] + depth[v] - 2 * depth[x];
                    assert(c.lca(u, v) == x && d.Lca(u, v) == x);
                    assert(c.dep[u] + c.dep[v] - 2 * c.dep[x] == distance);
                    assert(d.dep[u] + d.dep[v] - 2 * d.dep[x] == distance);
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
    LiftingLCA a(n);
    static Lifting_LCA<n> b;
    b.Init(n);
    for (int u = 2; u <= n; u++)
    {
        a.add(u - 1, u, -u);
        b.Insert(u - 1, u, -u);
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
            assert(a.max_edge(u, v) == optional<long long>(-min(u, v) - 1));
            assert(b.Max_Edge(u, v) == a.max_edge(u, v));
            assert(a.jump(u, abs(u - root)) == root);
            assert(b.Jump(u, abs(u - root) + 1LL) == 0);
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
    cout << "Lifting LCA dual exhaustive trees, ancestors, signed maximum edges, reroot and 500000 recursive chain PASS\n";
}
