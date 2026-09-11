#include "../src/compact/virtual_tree.hpp"
#include "../src/classic/virtual_tree.hpp"
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <tuple>
#include <pthread.h>

void test_all()
{
    using ll = long long;
    std::mt19937 rng(247339);
    static Virtual_Tree<64> b;
    for (int trial = 0; trial < 300; trial++)
    {
        int n = 1 + rng() % 64;
        VirtualTree a(n);
        b.Init(n);
        std::vector<std::vector<std::pair<int, ll>>> g(n + 1);
        for (int v = 2; v <= n; v++)
        {
            int u = 1 + rng() % (v - 1);
            ll w = rng() % 100;
            a.add(u, v, w);
            b.Insert(u, v, w);
            g[u].push_back({v, w});
            g[v].push_back({u, w});
        }
        for (int repeat = 0; repeat < 2; repeat++)
        {
            int root = 1 + rng() % n;
            std::vector<int> parent(n + 1), depth(n + 1), q{root};
            std::vector<ll> weight(n + 1);
            for (int i = 0; i < n; i++)
                for (auto [v, w] : g[q[i]])
                    if (v != parent[q[i]])
                    {
                        parent[v] = q[i];
                        depth[v] = depth[q[i]] + 1;
                        weight[v] = w;
                        q.push_back(v);
                    }
            auto lca = [&](int u, int v)
            {
                while (depth[u] > depth[v])
                    u = parent[u];
                while (depth[v] > depth[u])
                    v = parent[v];
                while (u != v)
                {
                    u = parent[u];
                    v = parent[v];
                }
                return u;
            };
            a.prepare(root);
            b.Prepare(root);
            for (int query = 0; query < 40; query++)
            {
                std::vector<int> keys;
                int k = rng() % (n + 5);
                for (int i = 0; i < k; i++)
                    keys.push_back(1 + rng() % n);
                std::set<int> expected(keys.begin(), keys.end());
                for (int u : keys)
                    for (int v : keys)
                    {
                        int p = lca(u, v);
                        assert(a.lca(u, v) == p && b.Lca(u, v) == p);
                        expected.insert(p);
                    }
                std::set<std::tuple<int, int, ll, ll>> expected_edges;
                for (int v : expected)
                {
                    int u = parent[v];
                    while (u && !expected.count(u))
                        u = parent[u];
                    if (!u)
                        continue;
                    ll sum = 0, minimum = std::numeric_limits<ll>::max();
                    for (int x = v; x != u; x = parent[x])
                    {
                        sum += weight[x];
                        minimum = std::min(minimum, weight[x]);
                    }
                    expected_edges.insert({u, v, sum, minimum});
                }
                auto verify = [&](const auto &result)
                {
                    assert(std::set<int>(result.vertices.begin(), result.vertices.end()) == expected);
                    assert(result.vertices.size() == expected.size());
                    std::set<std::tuple<int, int, ll, ll>> actual;
                    std::map<int, int> position;
                    for (int i = 0; i < (int)result.vertices.size(); i++)
                        position[result.vertices[i]] = i;
                    for (auto e : result.edges)
                    {
                        assert(position[e.from] < position[e.to]);
                        assert(actual.insert({e.from, e.to, e.distance, e.minimum}).second);
                    }
                    assert(actual == expected_edges);
                    assert(result.edges.size() + !result.vertices.empty() == result.vertices.size());
                };
                verify(a.build(keys));
                verify(b.Build(keys));
            }
        }
    }
    const int n = 100000;
    VirtualTree a(n);
    static Virtual_Tree<n> large;
    large.Init(n);
    for (int v = 2; v <= n; v++)
    {
        a.add(v - 1, v);
        large.Insert(v - 1, v);
    }
    a.prepare();
    large.Prepare();
    auto x = a.build({1, n / 2, n});
    auto y = large.Build({1, n / 2, n});
    assert(x.edges.size() == 2 && y.edges.size() == 2);
    assert(x.edges[0].distance == n / 2 - 1 && x.edges[1].distance == n - n / 2);
    assert(y.edges[0].distance == x.edges[0].distance && y.edges[1].distance == x.edges[1].distance);
    VirtualTree boundary(2);
    boundary.add(1, 2, std::numeric_limits<ll>::max());
    boundary.prepare();
    auto edge = boundary.build({1, 2}).edges[0];
    assert(edge.distance == std::numeric_limits<ll>::max());
    assert(edge.minimum == std::numeric_limits<ll>::max());
    std::cout << "Virtual tree all-pairs LCA closure, compressed paths, reroot and recursive chain PASS\n";
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
