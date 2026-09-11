#pragma once
#include <algorithm>
#include <array>
#include <cassert>
#include <climits>
#include <cmath>
#include <functional>
#include <map>
#include <numeric>
#include <optional>
#include <queue>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;

struct Kuhn_Munkres
{
    using I = __int128_t;
    // Minimum cost injection from n rows to m columns, n<=m. Zero-based matrix.
    static pair<I, vector<int>> Solve(const vector<vector<long long>> &cost)
    {
        int n = cost.size();
        if ( !n )
            return {0, {}};
        int m = cost[0].size();
        assert(n <= m);
        vector<I> u(n + 1), v(m + 1);
        vector<int> p(m + 1), way(m + 1);
        const I inf = I(1) << 120;
        for ( int i = 1; i <= n; i++ )
        {
            assert((int)cost[i - 1].size() == m);
            p[0] = i;
            int j0 = 0;
            vector<I> dis(m + 1, inf);
            vector<bool> Used(m + 1);
            do
            {
                Used[j0] = true;
                int i0 = p[j0], j1 = 0;
                I delta = inf;
                for ( int j = 1; j <= m; j++ )
                    if ( !Used[j] )
                    {
                        I cur = I(cost[i0 - 1][j - 1]) - u[i0] - v[j];
                        if ( cur < dis[j] )
                        {
                            dis[j] = cur;
                            way[j] = j0;
                        }
                        if ( dis[j] < delta )
                        {
                            delta = dis[j];
                            j1 = j;
                        }
                    }
                for ( int j = 0; j <= m; j++ )
                    if ( Used[j] )
                    {
                        u[p[j]] += delta;
                        v[j] -= delta;
                    }
                    else
                        dis[j] -= delta;
                j0 = j1;
            } while ( p[j0] );
            do
            {
                int j1 = way[j0];
                p[j0] = p[j1];
                j0 = j1;
            } while ( j0 );
        }
        vector<int> ans(n);
        for ( int j = 1; j <= m; j++ )
            if ( p[j] )
                ans[p[j] - 1] = j - 1;
        return {-v[0], ans};
    }
};

struct Directed_MST
{
    using I = __int128_t;
    struct Edge
    {
        int u, v;
        I w;
    };
    // Directed minimum rooted OUT-arborescence cost, 0-based, or nullopt.
    static optional<I> Solve(int n, int root, vector<Edge> e)
    {
        const I inf = I(1) << 120;
        I ans = 0;
        while ( true )
        {
            vector<I> in(n, inf);
            vector<int> pre(n, -1), id(n, -1), vis(n, -1);
            for ( auto a : e )
                if ( a.u != a.v && a.w < in[a.v] )
                {
                    in[a.v] = a.w;
                    pre[a.v] = a.u;
                }
            in[root] = 0;
            for ( I x : in )
            {
                if ( x == inf )
                    return nullopt;
                ans += x;
            }
            int cnt = 0;
            for ( int i = 0; i < n; i++ )
            {
                int u = i;
                while ( vis[u] != i && id[u] == -1 && u != root )
                {
                    vis[u] = i;
                    u = pre[u];
                }
                if ( u != root && id[u] == -1 )
                {
                    id[u] = cnt;
                    for ( int v = pre[u]; v != u; v = pre[v] )
                        id[v] = cnt;
                    ++cnt;
                }
            }
            if ( !cnt )
                return ans;
            for ( int i = 0; i < n; i++ )
                if ( id[i] == -1 )
                    id[i] = cnt++;
            for ( auto &a : e )
            {
                int v = a.v;
                a.u = id[a.u];
                a.v = id[a.v];
                if ( a.u != a.v )
                    a.w -= in[v];
            }
            root = id[root];
            n = cnt;
        }
    }
};

struct Global_Min_Cut
{
    using I = __int128_t;
    // Symmetric nonnegative adjacency matrix; returns weight and one cut side.
    static pair<I, vector<int>> Solve(vector<vector<I>> w)
    {
        int n = w.size();
        assert(n >= 2);
        vector<int> active(n);
        iota(active.begin(), active.end(), 0);
        vector<vector<int>> group(n);
        for ( int i = 0; i < n; i++ )
            group[i] = {i};
        I best = I(1) << 120;
        vector<int> side;
        while ( active.size() > 1 )
        {
            vector<I> dis(n);
            vector<bool> Used(n);
            int prev = -1;
            for ( int step = 0; step < (int)active.size(); step++ )
            {
                int sel = -1;
                for ( int v : active )
                    if ( !Used[v] && (sel == -1 || dis[v] > dis[sel]) )
                        sel = v;
                if ( step + 1 == (int)active.size() )
                {
                    if ( dis[sel] < best )
                    {
                        best = dis[sel];
                        side = group[sel];
                    }
                    for ( int v : active )
                        if ( v != prev && v != sel )
                            w[prev][v] = w[v][prev] = w[prev][v] + w[sel][v];
                    group[prev].insert(group[prev].end(), group[sel].begin(),
                                       group[sel].end());
                    active.erase(find(active.begin(), active.end(), sel));
                    break;
                }
                Used[sel] = true;
                prev = sel;
                for ( int v : active )
                    if ( !Used[v] )
                        dis[v] += w[sel][v];
            }
        }
        return {best, side};
    }
};
