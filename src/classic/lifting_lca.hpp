#pragma once
#include <algorithm>
#include <cassert>
#include <limits>
#include <optional>
#include <utility>
#include <vector>
using namespace std;

template <int N, int LOG = 20> struct Lifting_LCA
{
    using ll = long long;
    static constexpr ll LOW = numeric_limits<ll>::lowest();
    static_assert(1 <= LOG && LOG <= 31);
    int n;
    bool ready = false;
    vector<pair<int, ll>> g[N + 1];
    int up[LOG][N + 1], depth[N + 1];
    ll mx[LOG][N + 1];

    void Init(int vertices)
    {
        assert(0 < vertices && vertices <= N && (1LL << LOG) > vertices);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
        for ( int k = 0; k < LOG; k++ )
        {
            up[k][0] = 0;
            mx[k][0] = LOW;
        }
        ready = false;
    }

    void Insert(int u, int v, ll w = 1)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        g[u].push_back({v, w});
        g[v].push_back({u, w});
        ready = false;
    }

    void Dfs(int u, int parent, ll weight)
    {
        up[0][u] = parent;
        mx[0][u] = weight;
        for ( int k = 1; k < LOG; k++ )
        {
            int p = up[k - 1][u];
            up[k][u] = up[k - 1][p];
            mx[k][u] = max(mx[k - 1][u], mx[k - 1][p]);
        }
        for ( auto [v, w] : g[u] )
            if ( v != parent )
            {
                depth[v] = depth[u] + 1;
                Dfs(v, u, w);
            }
    }

    // Nonempty tree only. Node 0 means no ancestor.
    void Build(int root = 1)
    {
        assert(1 <= root && root <= n);
        depth[root] = 0;
        Dfs(root, 0, LOW);
        ready = true;
    }

    int Jump(int u, long long steps) const
    {
        assert(ready && 1 <= u && u <= n && steps >= 0);
        if ( steps > depth[u] )
            return 0;
        for ( int k = 0; k < LOG; k++ )
            if ( steps >> k & 1 )
                u = up[k][u];
        return u;
    }

    int Lca(int u, int v) const
    {
        assert(ready && 1 <= u && u <= n && 1 <= v && v <= n);
        if ( depth[u] < depth[v] )
            swap(u, v);
        u = Jump(u, depth[u] - depth[v]);
        if ( u == v )
            return u;
        for ( int k = LOG - 1; k >= 0; k-- )
            if ( up[k][u] != up[k][v] )
            {
                u = up[k][u];
                v = up[k][v];
            }
        return up[0][u];
    }

    int Distance(int u, int v) const
    {
        return depth[u] + depth[v] - 2 * depth[Lca(u, v)];
    }

    optional<ll> Max_Edge(int u, int v) const
    {
        assert(ready && 1 <= u && u <= n && 1 <= v && v <= n);
        if ( u == v )
            return nullopt;
        if ( depth[u] < depth[v] )
            swap(u, v);
        ll answer = LOW;
        int delta = depth[u] - depth[v];
        for ( int k = 0; k < LOG; k++ )
            if ( delta >> k & 1 )
            {
                answer = max(answer, mx[k][u]);
                u = up[k][u];
            }
        if ( u == v )
            return answer;
        for ( int k = LOG - 1; k >= 0; k-- )
            if ( up[k][u] != up[k][v] )
            {
                answer = max(answer, max(mx[k][u], mx[k][v]));
                u = up[k][u];
                v = up[k][v];
            }
        return max(answer, max(mx[0][u], mx[0][v]));
    }
};
