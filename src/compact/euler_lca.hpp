#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

struct EulerLCA
{
    using ll = long long;
    int n;
    bool ready = false;
    vector<vector<int>> g, st;
    vector<vector<ll>> cost;
    vector<ll> root_dist;
    vector<int> first, depth, euler, lg;

    EulerLCA(int n)
        : n(n), g(n + 1), cost(n + 1), root_dist(n + 1), first(n + 1), depth(n + 1)
    {
    }

    void add(int u, int v, ll w = 1)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        assert(w >= 0);
        g[u].push_back(v);
        g[v].push_back(u);
        cost[u].push_back(w);
        cost[v].push_back(w);
        ready = false;
    }

    int shallower(int u, int v) const { return depth[u] <= depth[v] ? u : v; }

    void dfs(int u, int parent)
    {
        first[u] = euler.size();
        euler.push_back(u);
        for (int i = 0; i < int(g[u].size()); i++)
        {
            int v = g[u][i];
            if (v != parent)
            {
                depth[v] = depth[u] + 1;
                root_dist[v] = root_dist[u] + cost[u][i];
                dfs(v, u);
                euler.push_back(u);
            }
        }
    }

    // Input must be a nonempty tree. Rebuilding may change the root.
    void build(int root = 1)
    {
        assert(1 <= root && root <= n);
        euler.clear();
        depth[root] = 0;
        root_dist[root] = 0;
        dfs(root, 0);
        int m = euler.size();
        lg.assign(m + 1, 0);
        for (int i = 2; i <= m; i++) lg[i] = lg[i / 2] + 1;
        st.assign(lg[m] + 1, {});
        st[0] = euler;
        for (int k = 1; k <= lg[m]; k++)
        {
            st[k].resize(m - (1 << k) + 1);
            for (int i = 0; i + (1 << k) <= m; i++)
                st[k][i] = shallower(st[k - 1][i], st[k - 1][i + (1 << (k - 1))]);
        }
        ready = true;
    }

    int lca(int u, int v) const
    {
        assert(ready && 1 <= u && u <= n && 1 <= v && v <= n);
        int l = first[u], r = first[v];
        if (l > r) swap(l, r);
        int k = lg[r - l + 1];
        return shallower(st[k][l], st[k][r - (1 << k) + 1]);
    }

    int distance(int u, int v) const
    {
        int z = lca(u, v);
        return depth[u] + depth[v] - 2 * depth[z];
    }

    ll weighted_distance(int u, int v) const
    {
        int z = lca(u, v);
        return (root_dist[u] - root_dist[z]) + (root_dist[v] - root_dist[z]);
    }
};
