#pragma once
#include "data_structure.hpp"

struct XorWalk
{
    using U = unsigned long long;
    int n;
    bool built = false;
    vector<vector<pair<int, U>>> g;
    vector<int> vis;
    vector<U> dist;
    XorBasis cycles;

    XorWalk(int size)
    {
        assert(size >= 0);
        n = size;
        g.resize(size_t(n) + 1);
        vis.resize(size_t(n) + 1);
        dist.resize(size_t(n) + 1);
    }

    void add(int u, int v, U w)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        g[u].push_back({v, w});
        g[v].push_back({u, w});
        built = false;
    }

    void dfs(int u)
    {
        vis[u] = 1;
        for (auto [v, w] : g[u])
        {
            if (!vis[v])
            {
                dist[v] = dist[u] ^ w;
                dfs(v);
            }
            else
                cycles.insert(dist[u] ^ dist[v] ^ w);
        }
    }

    void build(int root = 1)
    {
        assert(1 <= root && root <= n);
        fill(vis.begin(), vis.end(), 0);
        fill(dist.begin(), dist.end(), 0);
        cycles = XorBasis();
        dfs(root);
        built = true;
    }

    optional<U> query(int u, int v) const
    {
        assert(built && 1 <= u && u <= n && 1 <= v && v <= n);
        if (!vis[u] || !vis[v]) return nullopt;
        return cycles.query(dist[u] ^ dist[v]);
    }
};
