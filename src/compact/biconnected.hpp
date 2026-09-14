#pragma once
#include <algorithm>
#include <cassert>
#include <utility>
#include <vector>
using namespace std;

struct Biconnected
{
    int n, timer = 0, cnt = 0;
    vector<vector<pair<int, int>>> g;
    vector<pair<int, int>> edges;
    vector<vector<int>> blocks;
    vector<int> dfn, low, cut, bridge, bel, st;

    Biconnected(int n) : n(n), g(n + 1) {}

    int add(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        int id = edges.size();
        edges.push_back({u, v});
        if (u != v)
        {
            g[u].push_back({v, id});
            g[v].push_back({u, id});
        }
        return id;
    }

    void dfs(int u, int parent_edge)
    {
        dfn[u] = low[u] = ++timer;
        st.push_back(u);
        int children = 0;
        for (auto [v, id] : g[u])
        {
            if (id == parent_edge) continue;
            if (!dfn[v])
            {
                children++;
                dfs(v, id);
                low[u] = min(low[u], low[v]);
                if (low[v] > dfn[u]) bridge[id] = 1;
                if (low[v] >= dfn[u])
                {
                    if (parent_edge != -1 || children > 1) cut[u] = 1;
                    blocks.push_back({u});
                    while (true)
                    {
                        int x = st.back();
                        st.pop_back();
                        blocks.back().push_back(x);
                        if (x == v) break;
                    }
                }
            }
            else
                low[u] = min(low[u], dfn[v]);
        }
        if (parent_edge == -1 && children == 0) blocks.push_back({u});
    }

    void paint(int u)
    {
        bel[u] = cnt;
        for (auto [v, id] : g[u])
        {
            if (!bridge[id] && !bel[v]) paint(v);
        }
    }

    void run()
    {
        timer = cnt = 0;
        dfn.assign(n + 1, 0);
        low = dfn;
        cut = dfn;
        bel = dfn;
        bridge.assign(edges.size(), 0);
        blocks.clear();
        st.clear();
        for (int u = 1; u <= n; u++)
        {
            if (!dfn[u])
            {
                dfs(u, -1);
                st.pop_back();
            }
        }
        for (int u = 1; u <= n; u++)
        {
            if (bel[u]) continue;
            ++cnt;
            paint(u);
        }
    }

    // Original vertices 1..n; block i has node n+i+1. Includes isolated vertices.
    vector<vector<int>> block_forest() const
    {
        vector<vector<int>> tree(n + blocks.size() + 1);
        for (int i = 0; i < (int)blocks.size(); i++)
        {
            int b = n + i + 1;
            for (int u : blocks[i])
            {
                tree[u].push_back(b);
                tree[b].push_back(u);
            }
        }
        return tree;
    }

    // Edge-connected component IDs 1..cnt; forest edges carry original edge IDs.
    vector<vector<pair<int, int>>> bridge_forest() const
    {
        vector<vector<pair<int, int>>> tree(cnt + 1);
        for (int id = 0; id < (int)edges.size(); id++)
        {
            if (!bridge[id]) continue;
            auto [u, v] = edges[id];
            u = bel[u];
            v = bel[v];
            tree[u].push_back({v, id});
            tree[v].push_back({u, id});
        }
        return tree;
    }
};
