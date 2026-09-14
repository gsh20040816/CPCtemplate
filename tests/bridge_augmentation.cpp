#include "../src/compact/bridge_augmentation.hpp"
#include "../src/classic/bridge_augmentation.hpp"
#include <iostream>
#include <numeric>
#include <random>
#include <pthread.h>

bool connected(int n, const vector<pair<int, int>> &edges, int skip = -1)
{
    vector<int> parent(n + 1);
    iota(parent.begin(), parent.end(), 0);
    auto find = [&](auto &&self, int u) -> int
    {
        return parent[u] == u ? u : parent[u] = self(self, parent[u]);
    };
    for (int i = 0; i < (int)edges.size(); i++)
        if (i != skip)
            parent[find(find, edges[i].first)] = find(find, edges[i].second);
    for (int u = 1; u <= n; u++)
        if (find(find, u) != find(find, 1))
            return false;
    return true;
}

void check(int n, const vector<pair<int, int>> &edges)
{
    if (!connected(n, edges))
        return;
    BiconnectedCore graph(n);
    static Biconnected_Graph<20> classic;
    classic.Init(n);
    for (auto [u, v] : edges)
    {
        graph.add(u, v);
        classic.Insert(u, v);
    }
    graph.run();
    classic.Run();
    auto added = bridge_augmentation(graph);
    assert(added == Bridge_Augmentation(classic));
    // Independent bridge deletion and DSU compression for the lower bound.
    vector<int> parent(n + 1);
    iota(parent.begin(), parent.end(), 0);
    auto find = [&](auto &&self, int u) -> int
    {
        return parent[u] == u ? u : parent[u] = self(self, parent[u]);
    };
    vector<pair<int, int>> bridges;
    for (int i = 0; i < (int)edges.size(); i++)
    {
        auto [u, v] = edges[i];
        if (connected(n, edges, i))
            parent[find(find, u)] = find(find, v);
        else
            bridges.push_back({u, v});
    }
    vector<int> degree(n + 1);
    for (auto [u, v] : bridges)
    {
        degree[find(find, u)]++;
        degree[find(find, v)]++;
    }
    int leaves = count(degree.begin(), degree.end(), 1);
    assert((int)added.size() == (leaves + 1) / 2);
    auto result = edges;
    for (auto [u, v] : added)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n && u != v);
        result.push_back({u, v});
    }
    for (int i = 0; i < (int)result.size(); i++)
        assert(connected(n, result, i));
}

void *large(void *)
{
    constexpr int n = 200000;
    BiconnectedCore graph(n);
    static Biconnected_Graph<n> classic;
    classic.Init(n);
    for (int u = 2; u <= n; u++)
    {
        graph.add(u - 1, u);
        classic.Insert(u - 1, u);
    }
    graph.run();
    classic.Run();
    auto added = bridge_augmentation(graph);
    assert(added == Bridge_Augmentation(classic));
    assert(added.size() == 1);
    assert(added[0] == make_pair(1, n) || added[0] == make_pair(n, 1));
    return nullptr;
}

int main()
{
    for (int n = 1; n <= 5; n++)
    {
        vector<pair<int, int>> possible;
        for (int u = 1; u <= n; u++)
            for (int v = u + 1; v <= n; v++)
                possible.push_back({u, v});
        for (int mask = 0; mask < (1 << possible.size()); mask++)
        {
            vector<pair<int, int>> edges;
            for (int i = 0; i < (int)possible.size(); i++)
                if (mask >> i & 1)
                    edges.push_back(possible[i]);
            check(n, edges);
        }
    }
    mt19937 rng(2860);
    for (int t = 0; t < 10000; t++)
    {
        int n = rng() % 19 + 1;
        vector<pair<int, int>> edges;
        for (int u = 2; u <= n; u++)
            edges.push_back({u, (int)(rng() % (u - 1)) + 1});
        int extra = t % 3 == 0 ? rng() % 25 : 0;
        for (int i = 0; i < extra; i++)
            edges.push_back({(int)(rng() % n) + 1, (int)(rng() % n) + 1});
        shuffle(edges.begin(), edges.end(), rng);
        check(n, edges);
    }
    for (int n = 2; n <= 20; n++)
    {
        vector<pair<int, int>> star;
        for (int u = 2; u <= n; u++)
            star.push_back({1, u});
        check(n, star);
    }
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 256ULL << 20) == 0);
    pthread_t worker;
    assert(pthread_create(&worker, &attr, large, nullptr) == 0);
    assert(pthread_join(worker, nullptr) == 0);
    pthread_attr_destroy(&attr);
    cout << "bridge augmentation: exhaustive graphs, random multigraphs, certificates, 200000 recursive chain passed\n";
}
