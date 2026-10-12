#pragma once
#include "manhattan_mst.hpp"

// BEGIN manhattan_order
vector<int> manhattan_order(const vector<ManhattanMST::Point> &p)
{
    assert(p.size() <= INT_MAX);
    int n = int(p.size());
    if (n == 0)
        return {};
    auto t = ManhattanMST::solve(p);
    vector<vector<int>> g(n);
    for (auto [u, v] : t.edges)
    {
        g[u].push_back(v);
        g[v].push_back(u);
    }
    vector<int> ord;
    ord.reserve(n);
    auto dfs = [&](auto &&self, int u, int fa) -> void
    {
        ord.push_back(u);
        for (int v : g[u])
        {
            if (v != fa)
                self(self, v, u);
        }
    };
    dfs(dfs, 0, -1);
    return ord;
}
// END manhattan_order
