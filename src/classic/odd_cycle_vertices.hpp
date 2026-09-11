#pragma once
#include "biconnected.hpp"

// BEGIN Odd_Cycle_Vertices
// After Run(). Simple odd cycles have length >= 3; self-loops are ignored.
template <int N> vector<int> Odd_Cycle_Vertices(const Biconnected_Graph<N> &graph)
{
    int n = graph.n;
    auto forest = graph.Block_Forest();
    vector<int> parent(forest.size()), depth(forest.size());
    auto root_tree = [&](auto &&self, int u, int p) -> void
    {
        parent[u] = p;
        for ( int v : forest[u] )
            if ( v != p )
            {
                depth[v] = depth[u] + 1;
                self(self, v, u);
            }
    };
    for ( int u = 1; u <= n; u++ )
        if ( !depth[u] )
        {
            depth[u] = 1;
            root_tree(root_tree, u, 0);
        }
    vector<vector<pair<int, int>>> edges(graph.blocks.size());
    for ( auto [u, v] : graph.edges )
        if ( u != v )
        {
            int block = parent[depth[u] >= depth[v] ? u : v] - n - 1;
            assert(0 <= block && block < (int)edges.size());
            edges[block].push_back({u, v});
        }
    vector<vector<int>> g(n + 1);
    vector<int> color(n + 1), answer(n + 1);
    for ( int block = 0; block < (int)edges.size(); block++ )
    {
        for ( int u : graph.blocks[block] )
        {
            g[u].clear();
            color[u] = 0;
        }
        for ( auto [u, v] : edges[block] )
        {
            g[u].push_back(v);
            g[v].push_back(u);
        }
        bool bipartite = true;
        auto paint = [&](auto &&self, int u) -> void
        {
            for ( int v : g[u] )
                if ( !color[v] )
                {
                    color[v] = -color[u];
                    self(self, v);
                }
                else if ( color[v] == color[u] )
                    bipartite = false;
        };
        int root = graph.blocks[block][0];
        color[root] = 1;
        paint(paint, root);
        if ( !bipartite )
            for ( int u : graph.blocks[block] )
                answer[u] = 1;
    }
    return answer;
}

// END Odd_Cycle_Vertices
