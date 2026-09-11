#pragma once
#include <algorithm>
#include <cassert>
#include <limits>
#include <utility>
#include <vector>
using namespace std;

template <int N> struct Centroid_Pairs
{
    using ll = long long;
    int n;
    vector<pair<int, ll>> g[N + 1];
    int siz[N + 1], removed[N + 1], parent[N + 1];
    vector<ll> all[N + 1];
    vector<vector<ll>> part[N + 1];

    void Init(int vertices)
    {
        assert(0 <= vertices && vertices <= N);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
    }

    void Insert(int u, int v, ll w)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n && u != v && w >= 0);
        g[u].push_back({v, w});
        g[v].push_back({u, w});
    }

    void Size_Dfs(int u, int p)
    {
        siz[u] = 1;
        for ( auto [v, w] : g[u] )
        {
            if ( v == p || removed[v] )
                continue;
            Size_Dfs(v, u);
            siz[u] += siz[v];
        }
    }

    int Centroid(int u, int p, int total)
    {
        for ( auto [v, w] : g[u] )
        {
            if ( v != p && !removed[v] && siz[v] > total / 2 )
                return Centroid(v, u, total);
        }
        return u;
    }

    void Collect(int u, int p, ll d, vector<ll> &out)
    {
        out.push_back(d);
        for ( auto [v, w] : g[u] )
        {
            if ( v == p || removed[v] )
                continue;
            assert(d <= numeric_limits<ll>::max() - w);
            Collect(v, u, d + w, out);
        }
    }

    void Decompose(int entry, int p)
    {
        Size_Dfs(entry, 0);
        int c = Centroid(entry, 0, siz[entry]);
        removed[c] = 1;
        parent[c] = p;
        all[c] = {0};
        for ( auto [v, w] : g[c] )
        {
            if ( removed[v] )
                continue;
            part[c].push_back({});
            auto &d = part[c].back();
            Collect(v, c, w, d);
            sort(d.begin(), d.end());
            all[c].insert(all[c].end(), d.begin(), d.end());
        }
        sort(all[c].begin(), all[c].end());
        for ( auto [v, w] : g[c] )
        {
            if ( !removed[v] )
                Decompose(v, c);
        }
    }

    // Input must be a forest. Rebuild after changing edges.
    void Build()
    {
        fill(removed, removed + n + 1, 0);
        for ( int u = 1; u <= n; u++ )
        {
            all[u].clear();
            part[u].clear();
        }
        for ( int u = 1; u <= n; u++ )
        {
            if ( !removed[u] )
                Decompose(u, 0);
        }
    }

    ll Pairs(const vector<ll> &d, ll k) const
    {
        int l = 0, r = (int)d.size() - 1;
        ll answer = 0;
        while ( l < r )
        {
            if ( d[l] <= k - d[r] )
            {
                answer += r - l;
                l++;
            }
            else
                r--;
        }
        return answer;
    }

    // Unordered Pairs of distinct connected vertices. Nonnegative edge weights.
    ll Count_Leq(ll k) const
    {
        if ( k < 0 )
            return 0;
        ll answer = 0;
        for ( int c = 1; c <= n; c++ )
        {
            answer += Pairs(all[c], k);
            for ( const auto &d : part[c] )
                answer -= Pairs(d, k);
        }
        return answer;
    }

    ll Count_Exact(ll k) const
    {
        if ( k < 0 )
            return 0;
        return Count_Leq(k) - (k ? Count_Leq(k - 1) : 0);
    }
};
