#pragma once
#include "biconnected.hpp"

// BEGIN Bridge_Augmentation
// Connected, nonempty graph after Run(); new parallel edges are allowed.
template <int N>
inline vector<pair<int, int>> Bridge_Augmentation(const Biconnected_Graph<N> &graph)
{
    assert(graph.n > 0 && graph.cnt > 0);
    int bridges = count(graph.bridge.begin(), graph.bridge.end(), 1);
    assert(graph.cnt - bridges == 1);
    if ( graph.cnt == 1 )
        return {};
    auto tree = graph.Bridge_Forest();
    vector<int> representative(graph.cnt + 1);
    for ( int u = 1; u <= graph.n; u++ )
        representative[graph.bel[u]] = u;
    vector<int> leaves;
    auto dfs = [&](auto &&self, int u, int parent) -> void
    {
        if ( tree[u].size() == 1 )
            leaves.push_back(u);
        for ( auto [v, id] : tree[u] )
            if ( v != parent )
                self(self, v, u);
    };
    dfs(dfs, 1, 0);
    if ( leaves.size() % 2 )
        leaves.push_back(leaves[0]);
    int half = leaves.size() / 2;
    vector<pair<int, int>> added;
    for ( int i = 0; i < half; i++ )
        added.push_back({representative[leaves[i]], representative[leaves[i + half]]});
    return added;
}

// END Bridge_Augmentation
