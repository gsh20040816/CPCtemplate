#pragma once
#include "bridge_component_forest.hpp"

// BEGIN bridge_augmentation
// Connected, nonempty graph after run(); new parallel edges are allowed.
vector<pair<int, int>> bridge_augmentation(const BiconnectedCore &graph)
{
    assert(graph.n > 0 && graph.cnt > 0);
    int bridges = count(graph.bridge.begin(), graph.bridge.end(), 1);
    assert(graph.cnt - bridges == 1);
    if (graph.cnt == 1) return {};
    auto tree = bridge_component_forest(graph);
    vector<int> representative(graph.cnt + 1);
    for (int u = 1; u <= graph.n; u++) representative[graph.bel[u]] = u;
    vector<int> leaves;
    auto dfs = [&](auto &&self, int u, int parent) -> void
    {
        if (tree[u].size() == 1) leaves.push_back(u);
        for (auto [v, id] : tree[u])
            if (v != parent) self(self, v, u);
    };
    dfs(dfs, 1, 0);
    if (leaves.size() % 2) leaves.push_back(leaves[0]);
    int half = leaves.size() / 2;
    vector<pair<int, int>> added;
    for (int i = 0; i < half; i++)
        added.push_back({representative[leaves[i]], representative[leaves[i + half]]});
    return added;
}

// END bridge_augmentation
