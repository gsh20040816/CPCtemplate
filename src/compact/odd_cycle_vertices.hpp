#pragma once
#include "biconnected.hpp"

// BEGIN odd_cycle_vertices
// After run(). Simple odd cycles have length >= 3; self-loops are ignored.
inline vector<int> odd_cycle_vertices(const Biconnected &graph)
{
    int n = graph.n;
    auto forest = graph.block_forest();
    vector<int> parent(forest.size()), depth(forest.size());
    auto root_tree = [&](auto &&self, int u, int p) -> void
    {
        parent[u] = p;
        for (int v : forest[u])
            if (v != p)
            {
                depth[v] = depth[u] + 1;
                self(self, v, u);
            }
    };
    for (int u = 1; u <= n; u++)
        if (!depth[u])
        {
            depth[u] = 1;
            root_tree(root_tree, u, 0);
        }
    vector<vector<pair<int, int>>> edges(graph.blocks.size());
    for (auto [u, v] : graph.edges)
        if (u != v)
        {
            int block = parent[depth[u] >= depth[v] ? u : v] - n - 1;
            assert(0 <= block && block < (int)edges.size());
            edges[block].push_back({u, v});
        }
    vector<vector<int>> g(n + 1);
    vector<int> color(n + 1), answer(n + 1);
    for (int block = 0; block < (int)edges.size(); block++)
    {
        for (int u : graph.blocks[block])
        {
            g[u].clear();
            color[u] = 0;
        }
        for (auto [u, v] : edges[block])
        {
            g[u].push_back(v);
            g[v].push_back(u);
        }
        bool bipartite = true;
        auto paint = [&](auto &&self, int u) -> void
        {
            for (int v : g[u])
                if (!color[v])
                {
                    color[v] = -color[u];
                    self(self, v);
                }
                else if (color[v] == color[u])
                    bipartite = false;
        };
        int root = graph.blocks[block][0];
        color[root] = 1;
        paint(paint, root);
        if (!bipartite)
            for (int u : graph.blocks[block])
                answer[u] = 1;
    }
    return answer;
}

// END odd_cycle_vertices
