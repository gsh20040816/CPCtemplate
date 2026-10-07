#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct ZkwFlow
{
    using ll = long long;
    using I = __int128_t;

    struct Edge
    {
        int from, to;
        ll cap, cost, initial;
    };

    int n;
    vector<Edge> e;
    vector<vector<int>> g;
    vector<I> h;
    vector<int> vis;

    ZkwFlow(int n) : n(n), g(n + 1), h(n + 1), vis(n + 1)
    {
    }

    int add(int u, int v, ll cap, ll cost)
    {
        assert(cap >= 0 && cost != LLONG_MIN);
        int id = (int)e.size();
        e.push_back({u, v, cap, cost, cap});
        e.push_back({v, u, 0, -cost, 0});
        g[u].push_back(id);
        g[v].push_back(id ^ 1);
        return id;
    }

    ll used(int id) const
    {
        return e[id].initial - e[id].cap;
    }

    // Internal: a feasible potential on every residual component.
    void init()
    {
        fill(h.begin(), h.end(), 0);
        for (int it = 0; it < n; it++)
        {
            bool changed = false;
            for (auto a : e)
                if (a.cap && h[a.to] > h[a.from] + a.cost)
                {
                    h[a.to] = h[a.from] + a.cost;
                    changed = true;
                }
            if (!changed) return;
            if (it == n - 1) throw invalid_argument("negative cycle");
        }
    }

    ll dfs(int u, int t, ll f)
    {
        if (u == t) return f;
        vis[u] = 1;
        for (int id : g[u])
        {
            int v = e[id].to;
            if (!e[id].cap || vis[v]) continue;
            if (I(e[id].cost) + h[u] != h[v]) continue;
            ll take = dfs(v, t, min(f, e[id].cap));
            if (!take) continue;
            e[id].cap -= take;
            e[id ^ 1].cap += take;
            return take;
        }
        return 0;
    }

    bool relabel()
    {
        const I inf = I(1) << 120;
        I d = inf;
        for (auto a : e)
            if (a.cap && vis[a.from] && !vis[a.to])
                d = min(d, I(a.cost) + h[a.from] - h[a.to]);
        if (d == inf) return false;
        for (int u = 1; u <= n; u++)
            if (vis[u]) h[u] -= d;
        return true;
    }

    // Returns additional flow/cost; reuse only with the same source/sink.
    pair<ll, I> flow(int s, int t, ll limit = LLONG_MAX)
    {
        assert(s != t && limit >= 0);
        init();
        ll f = 0;
        I cost = 0;
        while (f < limit)
        {
            fill(vis.begin(), vis.end(), 0);
            ll take = dfs(s, t, limit - f);
            if (take)
            {
                f += take;
                cost += I(take) * (h[t] - h[s]);
            }
            else if (!relabel()) break;
        }
        return {f, cost};
    }
};
