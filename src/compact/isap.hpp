#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct Isap
{
    using ll = long long;

    struct Edge
    {
        int from, to;
        ll cap, initial;
    };

    int n;
    vector<Edge> e;
    vector<vector<int>> g;
    vector<int> dep, cur, gap;

    Isap(int n) : n(n), g(n + 1), dep(n + 1), cur(n + 1), gap(n + 1)
    {
    }

    int add(int u, int v, ll cap)
    {
        assert(cap >= 0);
        int id = (int)e.size();
        e.push_back({u, v, cap, cap});
        e.push_back({v, u, 0, 0});
        g[u].push_back(id);
        g[v].push_back(id ^ 1);
        return id;
    }

    ll used(int id) const
    {
        return e[id].initial - e[id].cap;
    }

    void bfs(int t)
    {
        fill(dep.begin(), dep.end(), n);
        fill(gap.begin(), gap.end(), 0);
        queue<int> q;
        dep[t] = 0;
        q.push(t);
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            for (int id : g[u])
            {
                int v = e[id].to;
                if (!e[id ^ 1].cap || dep[v] != n) continue;
                dep[v] = dep[u] + 1;
                q.push(v);
            }
        }
        for (int u = 1; u <= n; u++) gap[dep[u]]++;
    }

    ll dfs(int u, int s, int t, ll f)
    {
        if (u == t) return f;
        for (int &i = cur[u]; i < (int)g[u].size(); i++)
        {
            int id = g[u][i], v = e[id].to;
            if (!e[id].cap || dep[u] != dep[v] + 1) continue;
            ll take = dfs(v, s, t, min(f, e[id].cap));
            if (take)
            {
                e[id].cap -= take;
                e[id ^ 1].cap += take;
                return take;
            }
            if (dep[s] == n) return 0;
        }
        int old = dep[u], best = n;
        for (int id : g[u])
            if (e[id].cap) best = min(best, dep[e[id].to] + 1);
        dep[u] = best;
        cur[u] = 0;
        gap[best]++;
        if (--gap[old] == 0) dep[s] = n;
        return 0;
    }

    // Returns additional flow; reuse only with the same source/sink.
    ll flow(int s, int t, ll limit = LLONG_MAX)
    {
        assert(s != t && limit >= 0);
        bfs(t);
        fill(cur.begin(), cur.end(), 0);
        ll ans = 0;
        while (ans < limit && dep[s] < n)
            ans += dfs(s, s, t, limit - ans);
        return ans;
    }

    vector<int> cut(int s) const
    {
        vector<int> vis(n + 1), ans;
        queue<int> q;
        vis[s] = 1;
        q.push(s);
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            ans.push_back(u);
            for (int id : g[u])
            {
                int v = e[id].to;
                if (!e[id].cap || vis[v]) continue;
                vis[v] = 1;
                q.push(v);
            }
        }
        return ans;
    }
};
