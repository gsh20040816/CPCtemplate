#pragma once
#include "biconnected.hpp"
#include "graph.hpp"
#include <array>

// BEGIN EdgeCompression
struct EdgeCompression
{
    int n;
    vector<int> size, inside;
    vector<array<int, 3>> edges;

    EdgeCompression(const Biconnected &graph) : n(graph.cnt), size(n + 1), inside(n + 1)
    {
        for (int u = 1; u <= graph.n; u++) size[graph.bel[u]]++;
        for (int id = 0; id < (int)graph.edges.size(); id++)
        {
            auto [u, v] = graph.edges[id];
            u = graph.bel[u];
            v = graph.bel[v];
            if (u == v)
                inside[u]++;
            else
                edges.push_back({u, v, id});
        }
    }
};

// END EdgeCompression

// BEGIN orient_edges
// Tree edges go down; other edges go to ancestors. Handles each logical edge once.
vector<pair<int, int>> orient_edges(const Lowlink &graph)
{
    vector<pair<int, int>> direction(graph.edges);
    vector<int> seen(graph.n + 1);
    auto dfs = [&](auto &&self, int u) -> void
    {
        seen[u] = 1;
        for (auto [v, id] : graph.g[u])
        {
            if (direction[id].first) continue;
            direction[id] = {u, v};
            if (!seen[v]) self(self, v);
        }
    };
    for (int u = 1; u <= graph.n; u++)
        if (!seen[u]) dfs(dfs, u);
    return direction;
}

// END orient_edges
