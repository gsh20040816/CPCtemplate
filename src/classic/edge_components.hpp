#pragma once
#include "biconnected.hpp"
#include "graph.hpp"
#include <array>

// BEGIN Edge_Compression
struct Edge_Compression
{
    int n;
    vector<int> size, inside;
    vector<array<int, 3>> edges;

    template <int N>
    Edge_Compression(const Biconnected_Graph<N> &graph)
        : n(graph.cnt), size(n + 1), inside(n + 1)
    {
        for ( int u = 1; u <= graph.n; u++ )
            size[graph.bel[u]]++;
        for ( int id = 0; id < (int)graph.edges.size(); id++ )
        {
            auto [u, v] = graph.edges[id];
            u = graph.bel[u];
            v = graph.bel[v];
            if ( u == v )
                inside[u]++;
            else
                edges.push_back({u, v, id});
        }
    }
};

// END Edge_Compression

// BEGIN Orient_Edges
// Tree edges go down; other edges go to ancestors. Handles each logical edge once.
inline vector<pair<int, int>> Orient_Edges(const Low_Link &graph)
{
    vector<pair<int, int>> direction(graph.edges);
    vector<int> seen(graph.n + 1);
    auto dfs = [&](auto &&self, int u) -> void
    {
        seen[u] = 1;
        for ( auto [v, id] : graph.g[u] )
        {
            if ( direction[id].first )
                continue;
            direction[id] = {u, v};
            if ( !seen[v] )
                self(self, v);
        }
    };
    for ( int u = 1; u <= graph.n; u++ )
        if ( !seen[u] )
            dfs(dfs, u);
    return direction;
}

// END Orient_Edges
