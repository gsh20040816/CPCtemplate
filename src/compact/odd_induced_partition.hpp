#pragma once
#include "data_structure.hpp"
#include <optional>

// BEGIN odd_induced_partition
optional<vector<int>> odd_induced_partition(int n, const vector<pair<int, int>> &edges)
{
    vector<vector<int>> g(n), up(n);
    for (auto [u, v] : edges)
    {
        assert(0 <= u && u < n && 0 <= v && v < n && u != v);
        g[u].push_back(v);
        g[v].push_back(u);
    }
    vector<int> depth(n, -1), order;
    auto dfs = [&](auto &&self, int u, int h) -> int
    {
        depth[u] = h;
        int size = 1;
        for (int v : g[u])
            if (depth[v] == -1) size += self(self, v, h + 1);
        order.push_back(u);
        return size;
    };
    for (int u = 0; u < n; u++)
        if (depth[u] == -1 && dfs(dfs, u, 0) % 2) return nullopt;
    for (auto [u, v] : edges)
    {
        if (depth[u] > depth[v]) swap(u, v);
        up[v].push_back(u);
    }
    for (auto &a : up)
        sort(a.begin(), a.end(), [&](int u, int v) { return depth[u] < depth[v]; });
    dsu d(n);
    vector<int> level = depth, color(n);
    int count = 0;
    for (int u : order)
    {
        vector<int> children;
        for (int v : g[u])
            if (level[v] == level[u] + 1 && !color[d.find(v)]) children.push_back(v);
        if (children.empty()) continue;
        int skip = -1, best = -1;
        if (children.size() % 2 == 0)
            for (int v : children)
            {
                auto it = lower_bound(up[v].begin(),
                                      up[v].end(),
                                      depth[u],
                                      [&](int w, int h) { return depth[w] < h; });
                if (it != up[v].begin() && depth[*prev(it)] > best)
                {
                    skip = v;
                    best = depth[*prev(it)];
                }
            }
        if (skip != -1) level[skip] = best + 1;
        if (children.size() % 2 || skip != -1) color[d.find(u)] = ++count;
        for (int v : children)
            if (v != skip) d.merge(u, v);
    }
    for (int u = 0; u < n; u++) color[u] = color[d.find(u)];
    return color;
}

// END odd_induced_partition
