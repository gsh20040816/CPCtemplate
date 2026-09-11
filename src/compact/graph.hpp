#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct Dijkstra
{
    using ll = long long;
    static constexpr ll inf = LLONG_MAX;
    int n;
    vector<vector<pair<int, ll>>> g;
    vector<ll> dis;
    vector<int> pre;

    Dijkstra(int n) : n(n), g(n + 1)
    {
    }

    void add(int u, int v, ll w)
    {
        assert(w >= 0);
        g[u].push_back({v, w});
    }

    void run(int s)
    {
        dis.assign(n + 1, inf);
        pre.assign(n + 1, -1);
        dis[s] = 0;
        priority_queue<pair<ll, int>, vector<pair<ll, int>>, greater<pair<ll, int>>> q;
        q.push({0, s});
        while (!q.empty())
        {
            auto [d, u] = q.top();
            q.pop();
            if (d != dis[u])
                continue;
            for (auto [v, w] : g[u])
                if (w < inf - d && d + w < dis[v])
                {
                    dis[v] = d + w;
                    pre[v] = u;
                    q.push({dis[v], v});
                }
        }
    }

    vector<int> path(int t) const
    {
        if (dis[t] == inf)
            return {};
        vector<int> ans;
        for (; t != -1; t = pre[t])
            ans.push_back(t);
        reverse(ans.begin(), ans.end());
        return ans;
    }
};

struct SCC
{
    int n, cnt = 0;
    vector<vector<int>> g, rg;
    vector<int> bel;

    SCC(int n) : n(n), g(n + 1), rg(n + 1)
    {
    }

    void add(int u, int v)
    {
        g[u].push_back(v);
        rg[v].push_back(u);
    }

    // Iterative Kosaraju; component IDs are in topological order, 1..cnt.
    void run()
    {
        vector<int> vis(n + 1), order;
        cnt = 0;
        bel.assign(n + 1, 0);
        for (int s = 1; s <= n; s++)
            if (!vis[s])
            {
                vector<pair<int, int>> st{{s, 0}};
                vis[s] = 1;
                while (!st.empty())
                {
                    int u = st.back().first, &i = st.back().second;
                    if (i == (int)g[u].size())
                    {
                        order.push_back(u);
                        st.pop_back();
                    }
                    else
                    {
                        int v = g[u][i++];
                        if (!vis[v])
                        {
                            vis[v] = 1;
                            st.push_back({v, 0});
                        }
                    }
                }
            }
        reverse(order.begin(), order.end());
        for (int s : order)
            if (!bel[s])
            {
                ++cnt;
                vector<int> st{s};
                bel[s] = cnt;
                while (!st.empty())
                {
                    int u = st.back();
                    st.pop_back();
                    for (int v : rg[u])
                        if (!bel[v])
                        {
                            bel[v] = cnt;
                            st.push_back(v);
                        }
                }
            }
    }
};

struct TwoSAT
{
    int n;
    SCC g;
    vector<int> ans;

    TwoSAT(int n) : n(n), g(2 * n)
    {
    }

    int id(int x, bool value) const
    {
        return 2 * x - 1 + value;
    }

    void add(int x, bool a, int y, bool b)
    {
        g.add(id(x, !a), id(y, b));
        g.add(id(y, !b), id(x, a));
    }

    bool solve()
    {
        g.run();
        ans.assign(n + 1, 0);
        for (int x = 1; x <= n; x++)
        {
            if (g.bel[id(x, 0)] == g.bel[id(x, 1)])
                return false;
            ans[x] = g.bel[id(x, 1)] > g.bel[id(x, 0)];
        }
        return true;
    }
};

struct BipartiteMatching
{
    int n, m;
    vector<vector<int>> g;
    vector<int> l, r, dep;

    BipartiteMatching(int n, int m)
        : n(n), m(m), g(n + 1), l(n + 1), r(m + 1), dep(n + 1)
    {
    }

    void add(int u, int v)
    {
        g[u].push_back(v);
    }

    bool bfs()
    {
        queue<int> q;
        fill(dep.begin(), dep.end(), -1);
        for (int u = 1; u <= n; u++)
            if (!l[u])
            {
                dep[u] = 0;
                q.push(u);
            }
        bool ok = false;
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            for (int v : g[u])
                if (!r[v])
                    ok = true;
                else if (dep[r[v]] < 0)
                {
                    dep[r[v]] = dep[u] + 1;
                    q.push(r[v]);
                }
        }
        return ok;
    }

    bool dfs(int u)
    {
        for (int v : g[u])
            if (!r[v] || (dep[r[v]] == dep[u] + 1 && dfs(r[v])))
            {
                l[u] = v;
                r[v] = u;
                return true;
            }
        dep[u] = -1;
        return false;
    }

    int solve()
    {
        int ans = 0;
        for (int u = 1; u <= n; u++)
            ans += (l[u] != 0);
        while (bfs())
            for (int u = 1; u <= n; u++)
                if (!l[u])
                    ans += dfs(u);
        return ans;
    }
};

struct Lowlink
{
    int n, timer = 0;
    vector<vector<pair<int, int>>> g;
    vector<int> dfn, low, cut, bridge;
    int edges = 0;

    Lowlink(int n) : n(n), g(n + 1)
    {
    }

    int add(int u, int v)
    {
        g[u].push_back({v, edges});
        g[v].push_back({u, edges});
        return edges++;
    }

    void dfs(int u, int pe)
    {
        dfn[u] = low[u] = ++timer;
        int children = 0;
        for (auto [v, id] : g[u])
        {
            if (id == pe)
                continue;
            if (!dfn[v])
            {
                ++children;
                dfs(v, id);
                low[u] = min(low[u], low[v]);
                if (low[v] > dfn[u])
                    bridge[id] = 1;
                if (pe != -1 && low[v] >= dfn[u])
                    cut[u] = 1;
            }
            else
                low[u] = min(low[u], dfn[v]);
        }
        if (pe == -1 && children > 1)
            cut[u] = 1;
    }

    void run()
    {
        timer = 0;
        dfn.assign(n + 1, 0);
        low = dfn;
        cut = dfn;
        bridge.assign(edges, 0);
        for (int u = 1; u <= n; u++)
            if (!dfn[u])
                dfs(u, -1);
    }
};
