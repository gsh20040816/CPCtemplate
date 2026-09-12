#pragma once
#include "biconnected.hpp"

// BEGIN removal_components
// Call after run(). Each vertex is deleted independently from the original graph.
inline pair<int, vector<int>> removal_components(const Biconnected &graph)
{
    int before = graph.cnt - count(graph.bridge.begin(), graph.bridge.end(), 1);
    vector<int> after(graph.n + 1, before - 1);
    after[0] = 0;
    for (const auto &block : graph.blocks)
        if (block.size() > 1)
            for (int u : block) after[u]++;
    return {before, after};
}

// END removal_components
