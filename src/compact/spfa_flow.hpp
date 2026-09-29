#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct SpfaFlow
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

    SpfaFlow(int n) : n(n), g(n + 1) {}

    int add(int u, int v, ll cap, ll cost)
    {
        assert(cap >= 0 && cost != LLONG_MIN);
        int id = (int)e.size();
        e.push_back({u, v, cap, cost, cap});
        e.push_back({v, u, 0, -cost, 0});
        g[u].push_back(id);
        g[v].push_back(id + 1);
        return id;
    }

    ll used(int id) const { return e[id].initial - e[id].cap; }

    // Internal: s=0 seeds every vertex to detect any residual negative cycle.
    void shortest(int s, vector<I> &d, vector<int> &pre)
    {
        const I inf = I(1) << 120;
        d.assign(n + 1, inf);
        pre.assign(n + 1, -1);
        vector<int> len(n + 1), in(n + 1);
        queue<int> q;
        for (int u = 1; u <= n; u++)
            if (!s || u == s)
            {
                d[u] = 0;
                in[u] = 1;
                q.push(u);
            }
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            in[u] = 0;
            for (int id : g[u])
            {
                auto &a = e[id];
                if (!a.cap || d[a.to] <= d[u] + a.cost) continue;
                d[a.to] = d[u] + a.cost;
                pre[a.to] = id;
                len[a.to] = len[u] + 1;
                if (len[a.to] >= n) throw invalid_argument("negative cycle");
                if (!in[a.to])
                {
                    in[a.to] = 1;
                    q.push(a.to);
                }
            }
        }
    }

    // Returns additional flow/cost; reuse only with the same source/sink.
    pair<ll, I> flow(int s, int t, ll limit = LLONG_MAX)
    {
        assert(s != t && limit >= 0);
        vector<I> d;
        vector<int> pre;
        shortest(0, d, pre);
        ll f = 0;
        I cost = 0;
        while (f < limit)
        {
            shortest(s, d, pre);
            if (pre[t] < 0) break;
            ll take = limit - f;
            for (int u = t; u != s; u = e[pre[u]].from) take = min(take, e[pre[u]].cap);
            for (int u = t; u != s; u = e[pre[u]].from)
            {
                int id = pre[u];
                e[id].cap -= take;
                e[id ^ 1].cap += take;
            }
            f += take;
            cost += I(take) * d[t];
        }
        return {f, cost};
    }
};
