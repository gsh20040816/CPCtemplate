#pragma once
#include "data_structure.hpp"

template <int N> struct Xor_Walk
{
    using U = unsigned long long;
    int n = 0;
    bool built = false;
    vector<pair<int, U>> g[N + 1];
    int vis[N + 1];
    U dist[N + 1];
    Xor_Basis cycles;

    void Init(int size)
    {
        assert(0 <= size && size <= N);
        for ( int u = 1; u <= n; u++ )
            g[u] = vector<pair<int, U>>();
        n = size;
        cycles.Init();
        built = false;
    }

    void Insert(int u, int v, U w)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        g[u].push_back({v, w});
        g[v].push_back({u, w});
        built = false;
    }

    void Dfs(int u)
    {
        vis[u] = 1;
        for ( auto [v, w] : g[u] )
        {
            if ( !vis[v] )
            {
                dist[v] = dist[u] ^ w;
                Dfs(v);
            }
            else
                cycles.Insert(dist[u] ^ dist[v] ^ w);
        }
    }

    void Build(int root = 1)
    {
        assert(1 <= root && root <= n);
        fill(vis, vis + n + 1, 0);
        fill(dist, dist + n + 1, 0);
        cycles.Init();
        Dfs(root);
        built = true;
    }

    optional<U> Query(int u, int v) const
    {
        assert(built && 1 <= u && u <= n && 1 <= v && v <= n);
        if ( !vis[u] || !vis[v] )
            return nullopt;
        return cycles.Query(dist[u] ^ dist[v]);
    }
};
