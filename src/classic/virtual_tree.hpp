#pragma once
#include <algorithm>
#include <cassert>
#include <limits>
#include <utility>
#include <vector>
using namespace std;

template <int N, int LOG = 20> struct Virtual_Tree
{
    using ll = long long;

    struct Edge
    {
        int from, to;
        ll distance, minimum;
    };

    struct Result
    {
        vector<int> vertices;
        vector<Edge> edges;
    };

    int n, log = 1, timer = 0;
    vector<pair<int, ll>> g[N + 1];
    int up[LOG][N + 1], depth[N + 1], tin[N + 1], tout[N + 1];
    ll mn[LOG][N + 1], dist[N + 1];

    void Init(int vertices)
    {
        assert(0 < vertices && vertices <= N);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
    }

    void Insert(int u, int v, ll w = 1)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n && u != v && w >= 0);
        g[u].push_back({v, w});
        g[v].push_back({u, w});
    }

    void Dfs(int u, int p)
    {
        tin[u] = ++timer;
        up[0][u] = p;
        for ( int j = 1; j < log; j++ )
        {
            up[j][u] = up[j - 1][up[j - 1][u]];
            mn[j][u] = min(mn[j - 1][u], mn[j - 1][up[j - 1][u]]);
        }
        for ( auto [v, w] : g[u] )
        {
            if ( v == p )
                continue;
            assert(dist[u] <= numeric_limits<ll>::max() - w);
            depth[v] = depth[u] + 1;
            dist[v] = dist[u] + w;
            mn[0][v] = w;
            Dfs(v, u);
        }
        tout[u] = timer;
    }

    void Prepare(int root = 1)
    {
        assert(1 <= root && root <= n);
        log = 1;
        while ( (1LL << log) <= n )
            log++;
        assert(log <= LOG);
        for ( int j = 0; j < log; j++ )
        {
            fill(up[j], up[j] + n + 1, 0);
            fill(mn[j], mn[j] + n + 1, numeric_limits<ll>::max());
        }
        fill(depth, depth + n + 1, 0);
        fill(tin, tin + n + 1, 0);
        fill(tout, tout + n + 1, 0);
        fill(dist, dist + n + 1, 0);
        timer = 0;
        Dfs(root, root);
    }

    bool Ancestor(int u, int v) const
    {
        return tin[u] <= tin[v] && tout[v] <= tout[u];
    }

    int Lca(int u, int v) const
    {
        if ( Ancestor(u, v) )
            return u;
        if ( Ancestor(v, u) )
            return v;
        for ( int j = log - 1; j >= 0; j-- )
        {
            if ( !Ancestor(up[j][u], v) )
                u = up[j][u];
        }
        return up[0][u];
    }

    Edge Path(int u, int v) const
    {
        assert(u != v && Ancestor(u, v));
        ll minimum = numeric_limits<ll>::max();
        int x = v, steps = depth[v] - depth[u];
        for ( int j = 0; j < log; j++ )
        {
            if ( steps >> j & 1 )
            {
                minimum = min(minimum, mn[j][x]);
                x = up[j][x];
            }
        }
        return {u, v, dist[v] - dist[u], minimum};
    }

    // Uses original vertex IDs. Empty input gives an empty result.
    Result Build(vector<int> keys) const
    {
        if ( keys.empty() )
            return {};
        for ( int u : keys )
            assert(1 <= u && u <= n);
        auto cmp = [&](int u, int v)
        {
            return tin[u] < tin[v];
        };
        sort(keys.begin(), keys.end(), cmp);
        keys.erase(unique(keys.begin(), keys.end()), keys.end());
        int k = keys.size();
        for ( int i = 1; i < k; i++ )
            keys.push_back(Lca(keys[i - 1], keys[i]));
        sort(keys.begin(), keys.end(), cmp);
        keys.erase(unique(keys.begin(), keys.end()), keys.end());
        Result result{keys, {}};
        vector<int> st;
        for ( int u : keys )
        {
            while ( !st.empty() && !Ancestor(st.back(), u) )
                st.pop_back();
            if ( !st.empty() )
                result.edges.push_back(Path(st.back(), u));
            st.push_back(u);
        }
        return result;
    }
};
