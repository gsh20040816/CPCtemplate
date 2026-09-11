#include "../src/compact/tree.hpp"
#include "../src/classic/tree.hpp"
#include "../src/compact/affine_segment_tree.hpp"
#include "../src/classic/affine_segment_tree.hpp"
#include "../src/compact/graph.hpp"
#include "../src/classic/graph.hpp"
#include <iostream>
#include <random>
#include <pthread.h>

void test_all()
{
    std::mt19937 rng(467791);
    static Heavy_Light_Decomposition<64> b;
    static Affine_Segment_Tree<64> sb;
    for (int trial = 0; trial < 200; trial++)
    {
        int n = 1 + rng() % 64;
        HLD a(n);
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
            std::vector<int> p(n + 1), depth(n + 1), q{root};
            for (int i = 0; i < n; i++)
                for (int v : g[q[i]])
                    if (v != p[q[i]])
                    {
                        p[v] = q[i];
                        depth[v] = depth[q[i]] + 1;
                        q.push_back(v);
                    }
            auto lca = [&](int u, int v)
            {
                while (depth[u] > depth[v])
                    u = p[u];
                while (depth[v] > depth[u])
                    v = p[v];
                while (u != v)
                {
                    u = p[u];
                    v = p[v];
                }
                return u;
            };
            auto path = [&](int u, int v, bool edge)
            {
                int w = lca(u, v);
                std::vector<int> nodes;
                for (; u != w; u = p[u])
                    nodes.push_back(u);
                for (; v != w; v = p[v])
                    nodes.push_back(v);
                if (!edge)
                    nodes.push_back(w);
                std::sort(nodes.begin(), nodes.end());
                return nodes;
            };
            std::vector<std::vector<int>> sub(n + 1);
            for (int v = 1; v <= n; v++)
                for (int u = v; u; u = p[u])
                    sub[u].push_back(v);
            a.build(root);
            b.Build(root);
            for (int u = 1; u <= n; u++)
            {
                std::vector<int> sa_nodes, sb_nodes;
                for (int i = a.dfn[u]; i < a.dfn[u] + a.siz[u]; i++)
                    sa_nodes.push_back(a.rk[i]);
                for (int i = b.dfn[u]; i < b.dfn[u] + b.siz[u]; i++)
                    sb_nodes.push_back(b.rk[i]);
                std::sort(sa_nodes.begin(), sa_nodes.end());
                std::sort(sb_nodes.begin(), sb_nodes.end());
                assert(sa_nodes == sub[u] && sb_nodes == sub[u]);
                for (int v = 1; v <= n; v++)
                {
                    assert(a.lca(u, v) == lca(u, v) && b.Lca(u, v) == lca(u, v));
                    for (bool edge : {false, true})
                    {
                        std::vector<int> x, y;
                        a.path(
                            u,
                            v,
                            [&](int l, int r)
                            {
                                for (int i = l; i <= r; i++)
                                    x.push_back(a.rk[i]);
                            },
                            edge);
                        b.Path(
                            u,
                            v,
                            [&](int l, int r)
                            {
                                for (int i = l; i <= r; i++)
                                    y.push_back(b.rk[i]);
                            },
                            edge);
                        std::sort(x.begin(), x.end());
                        std::sort(y.begin(), y.end());
                        assert(x == path(u, v, edge) && y == path(u, v, edge));
                    }
                }
            }
            AffineSegTree sa(std::vector<long long>(n), 97);
            sb.Init(std::vector<long long>(n), 97);
            std::vector<long long> values(n + 1);
            for (int step = 0; step < 100; step++)
            {
                int u = 1 + rng() % n, v = 1 + rng() % n;
                int op = rng() % 4;
                auto nodes = op < 2 ? path(u, v, false) : sub[u];
                if (op % 2 == 0)
                {
                    int x = rng() % 97;
                    for (int node : nodes)
                        values[node] = (values[node] + x) % 97;
                    if (op == 0)
                    {
                        a.path(u,
                               v,
                               [&](int l, int r)
                               {
                                   sa.update(l, r, 1, x);
                               });
                        b.Path(u,
                               v,
                               [&](int l, int r)
                               {
                                   sb.Update(l, r, 1, x);
                               });
                    }
                    else
                    {
                        sa.update(a.dfn[u], a.dfn[u] + a.siz[u] - 1, 1, x);
                        sb.Update(b.dfn[u], b.dfn[u] + b.siz[u] - 1, 1, x);
                    }
                }
                else
                {
                    long long expected = 0, x = 0, y = 0;
                    for (int node : nodes)
                        expected = (expected + values[node]) % 97;
                    if (op == 1)
                    {
                        a.path(u,
                               v,
                               [&](int l, int r)
                               {
                                   x = (x + sa.query(l, r)) % 97;
                               });
                        b.Path(u,
                               v,
                               [&](int l, int r)
                               {
                                   y = (y + sb.Query(l, r)) % 97;
                               });
                    }
                    else
                    {
                        x = sa.query(a.dfn[u], a.dfn[u] + a.siz[u] - 1);
                        y = sb.Query(b.dfn[u], b.dfn[u] + b.siz[u] - 1);
                    }
                    assert(x == expected && y == expected);
                }
            }
        }
    }
    const int n = 200000;
    HLD a(n);
    static Heavy_Light_Decomposition<n> large;
    large.Init(n);
    for (int v = 2; v <= n; v++)
    {
        a.add(v - 1, v);
        large.Insert(v - 1, v);
    }
    for (int root : {1, n})
    {
        a.build(root);
        large.Build(root);
        assert(a.siz[root] == n && large.siz[root] == n);
        assert(a.lca(1, n) == root && large.Lca(1, n) == root);
    }
    SCC c(n);
    Strong_Component d(n);
    for (int u = 1; u < n; u++)
    {
        c.add(u, u + 1);
        d.Insert(u, u + 1);
    }
    c.run();
    d.Run();
    assert(c.cnt == n && d.cnt == n);
    c.add(n, 1);
    d.Insert(n, 1);
    c.run();
    d.Run();
    assert(c.cnt == 1 && d.cnt == 1);
    std::cout << "Recursive HLD paths, edge paths, subtree intervals, segment "
                 "integration and reroot PASS\n";
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
