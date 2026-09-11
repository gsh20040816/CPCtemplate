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

    void dfs1(int u, vector<int> &vis, vector<int> &order)
    {
        vis[u] = 1;
        for (int v : g[u])
        {
            if (!vis[v])
                dfs1(v, vis, order);
        }
        order.push_back(u);
    }

    void dfs2(int u)
    {
        bel[u] = cnt;
        for (int v : rg[u])
        {
            if (!bel[v])
                dfs2(v);
        }
    }

    // Recursive Kosaraju; component IDs are in topological order, 1..cnt.
    void run()
    {
        vector<int> vis(n + 1), order;
        cnt = 0;
        bel.assign(n + 1, 0);
        for (int s = 1; s <= n; s++)
        {
            if (!vis[s])
                dfs1(s, vis, order);
        }
        reverse(order.begin(), order.end());
        for (int s : order)
        {
            if (!bel[s])
            {
                ++cnt;
                dfs2(s);
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
    vector<int> l, r, dep, cur;

    BipartiteMatching(int n, int m)
        : n(n), m(m), g(n + 1), l(n + 1), r(m + 1), dep(n + 1), cur(n + 1)
    {
    }

    void add(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= m);
        g[u].push_back(v);
    }

    bool bfs()
    {
        queue<int> q;
        fill(dep.begin(), dep.end(), n + 1);
        fill(cur.begin(), cur.end(), 0);
        for (int u = 1; u <= n; u++)
        {
            if (!l[u])
            {
                dep[u] = 0;
                q.push(u);
            }
        }
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            if (dep[u] >= dep[0])
                continue;
            for (int v : g[u])
            {
                int next = r[v];
                if (dep[next] != n + 1)
                    continue;
                dep[next] = dep[u] + 1;
                if (next)
                    q.push(next);
            }
        }
        return dep[0] != n + 1;
    }

    bool dfs(int u)
    {
        if (!u)
            return true;
        for (int &i = cur[u]; i < (int)g[u].size(); i++)
        {
            int v = g[u][i];
            if (dep[r[v]] == dep[u] + 1 && dfs(r[v]))
            {
                l[u] = v;
                r[v] = u;
                return true;
            }
        }
        dep[u] = n + 1;
        return false;
    }

    // Retains an existing matching; edges may be added between calls.
    int solve()
    {
        int answer = 0;
        for (int u = 1; u <= n; u++)
            answer += (l[u] != 0);
        while (bfs())
        {
            for (int u = 1; u <= n; u++)
            {
                if (!l[u] && dfs(u))
                    answer++;
            }
        }
        return answer;
    }

    // Call after solve(), before adding more edges. Returns left/right vertex IDs.
    pair<vector<int>, vector<int>> cover() const
    {
        vector<int> left, right;
        for (int u = 1; u <= n; u++)
        {
            if (dep[u] == n + 1)
                left.push_back(u);
        }
        for (int v = 1; v <= m; v++)
        {
            if (r[v] && dep[r[v]] != n + 1)
                right.push_back(v);
        }
        return {left, right};
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
