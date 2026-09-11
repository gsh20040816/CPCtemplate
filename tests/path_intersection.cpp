#include "../src/compact/path_intersection.hpp"
#include "../src/classic/path_intersection.hpp"
#include "../src/compact/euler_lca.hpp"
#include "../src/classic/tree.hpp"
#include <iostream>
#include <random>
#include <cstdint>

void check(int n, const vector<pair<int, int>> &edges, bool exhaustive)
{
    EulerLCA tree(n);
    static Heavy_Light_Decomposition<32> classic;
    classic.Init(n);
    vector<vector<int>> g(n + 1);
    for (auto [u, v] : edges)
    {
        tree.add(u, v);
        classic.Insert(u, v);
        g[u].push_back(v);
        g[v].push_back(u);
    }
    vector<vector<uint64_t>> paths(n + 1, vector<uint64_t>(n + 1));
    for (int start = 1; start <= n; start++)
    {
        vector<int> parent(n + 1, -1), queue{start};
        parent[start] = 0;
        for (int i = 0; i < (int)queue.size(); i++)
            for (int v : g[queue[i]])
                if (parent[v] == -1)
                {
                    parent[v] = queue[i];
                    queue.push_back(v);
                }
        for (int v = 1; v <= n; v++)
            for (int u = v; u; u = parent[u])
                paths[start][v] |= uint64_t(1) << (u - 1);
    }
    mt19937 rng(n * 601 + edges.size());
    for (int root = 1; root <= n; root++)
    {
        tree.build(root);
        classic.Build(root);
        auto lca = [&](int u, int v)
        {
            return tree.lca(u, v);
        };
        auto classic_lca = [&](int u, int v)
        {
            return classic.Lca(u, v);
        };
        auto query = [&](int a, int b, int c, int d)
        {
            uint64_t mask = paths[a][b] & paths[c][d];
            int count = __builtin_popcountll(mask);
            auto x = path_intersection(a, b, c, d, tree.depth, lca);
            auto y = Path_Intersection(a, b, c, d, classic.dep, classic_lca);
            assert(x.vertices == count && y.vertices == count);
            if (!count)
                assert(x.u == 0 && x.v == 0 && y.u == 0 && y.v == 0);
            else
            {
                assert(1 <= x.u && x.u <= n && 1 <= x.v && x.v <= n);
                assert(1 <= y.u && y.u <= n && 1 <= y.v && y.v <= n);
                assert(paths[x.u][x.v] == mask && paths[y.u][y.v] == mask);
            }
        };
        if (exhaustive)
            for (int a = 1; a <= n; a++)
                for (int b = 1; b <= n; b++)
                    for (int c = 1; c <= n; c++)
                        for (int d = 1; d <= n; d++)
                            query(a, b, c, d);
        else
            for (int i = 0; i < 300; i++)
                query(rng() % n + 1, rng() % n + 1, rng() % n + 1, rng() % n + 1);
    }
}

int main()
{
    for (int n = 1; n <= 5; n++)
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
            check(n, edges, true);
        }
    }
    mt19937 rng(3398);
    for (int t = 0; t < 150; t++)
    {
        int n = rng() % 30 + 1;
        vector<int> labels(n + 1);
        iota(labels.begin(), labels.end(), 0);
        shuffle(labels.begin() + 1, labels.end(), rng);
        vector<pair<int, int>> edges;
        for (int u = 2; u <= n; u++)
            edges.push_back({labels[u], labels[rng() % (u - 1) + 1]});
        check(n, edges, false);
    }
    cout << "Path intersection dual exhaustive labelled trees/roots/four endpoints, set oracle and Euler/HLD callbacks PASS\n";
}
