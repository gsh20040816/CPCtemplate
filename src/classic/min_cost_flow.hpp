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

struct Min_Cost_Flow
{
    using ll = long long;
    using i128 = __int128_t;

    struct Edge
    {
        int from, to;
        ll cap, cost, initial;
    };

    int n;
    vector<Edge> e;
    vector<vector<int>> g;

    Min_Cost_Flow(int n) : n(n), g(n + 1)
    {
    }

    int Insert(int u, int v, ll cap, ll cost)
    {
        assert(cap >= 0 && cost != LLONG_MIN);
        int id = (int)e.size();
        e.push_back({u, v, cap, cost, cap});
        e.push_back({v, u, 0, -cost, 0});
        g[u].push_back(id);
        g[v].push_back(id + 1);
        return id;
    }

    ll Used(int id) const
    {
        return e[id].initial - e[id].cap;
    }

    // Negative costs allowed; initial residual graph must have no negative cycle.
    pair<ll, i128> Flow(int s, int t, ll limit = LLONG_MAX)
    {
        assert(s != t && limit >= 0);
        const i128 inf = i128(1) << 120;
        vector<i128> h(n + 1, 0), d(n + 1);
        vector<int> pre(n + 1);
        // Super-source Bellman-Ford: feasible potentials for every vertex.
        for ( int it = 0; it < n; it++ )
        {
            bool changed = false;
            for ( auto &a : e )
                if ( a.cap && h[a.to] > h[a.from] + a.cost )
                {
                    h[a.to] = h[a.from] + a.cost;
                    changed = true;
                }
            if ( !changed )
                break;
            if ( it == n - 1 )
                throw invalid_argument("negative cycle");
        }
        ll f = 0;
        i128 cost = 0;
        while ( f < limit )
        {
            fill(d.begin(), d.end(), inf);
            d[s] = 0;
            priority_queue<pair<i128, int>,
                           vector<pair<i128, int>>,
                           greater<pair<i128, int>>>
                q;
            q.push({0, s});
            while ( !q.empty() )
            {
                auto [du, u] = q.top();
                q.pop();
                if ( du != d[u] )
                    continue;
                for ( int id : g[u] )
                {
                    auto &a = e[id];
                    i128 nd = du + a.cost + h[u] - h[a.to];
                    if ( a.cap && nd < d[a.to] )
                    {
                        d[a.to] = nd;
                        pre[a.to] = id;
                        q.push({nd, a.to});
                    }
                }
            }
            if ( d[t] == inf )
                break;
            for ( int u = 1; u <= n; u++ )
                if ( d[u] != inf )
                    h[u] += d[u];
            ll take = limit - f;
            for ( int u = t; u != s; u = e[pre[u]].from )
                take = min(take, e[pre[u]].cap);
            for ( int u = t; u != s; u = e[pre[u]].from )
            {
                int id = pre[u];
                e[id].cap -= take;
                e[id ^ 1].cap += take;
                cost += i128(take) * e[id].cost;
            }
            f += take;
        }
        return {f, cost};
    }
};
