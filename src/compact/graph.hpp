#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

#include "data_structure.hpp"

struct Dijkstra
{
    using ll = long long;
    static constexpr ll inf = LLONG_MAX;
    int n;
    vector<vector<pair<int, ll>>> g;
    vector<ll> dis;
    vector<int> pre;

    Dijkstra(int n) : n(n), g(n + 1) {}

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
            if (d != dis[u]) continue;
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
        if (dis[t] == inf) return {};
        vector<int> ans;
        for (; t != -1; t = pre[t]) ans.push_back(t);
        reverse(ans.begin(), ans.end());
        return ans;
    }
};

struct SCC
{
    int n, cnt = 0;
    vector<vector<int>> g, rg;
    vector<int> bel;

    SCC(int n) : n(n), g(n + 1), rg(n + 1) {}

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
            if (!vis[v]) dfs1(v, vis, order);
        }
        order.push_back(u);
    }

    void dfs2(int u)
    {
        bel[u] = cnt;
        for (int v : rg[u])
        {
            if (!bel[v]) dfs2(v);
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
            if (!vis[s]) dfs1(s, vis, order);
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

    TwoSAT(int n) : n(n), g(2 * n) {}

    int id(int x, bool value) const { return 2 * x - 1 + value; }

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
            if (g.bel[id(x, 0)] == g.bel[id(x, 1)]) return false;
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
            if (dep[u] >= dep[0]) continue;
            for (int v : g[u])
            {
                int next = r[v];
                if (dep[next] != n + 1) continue;
                dep[next] = dep[u] + 1;
                if (next) q.push(next);
            }
        }
        return dep[0] != n + 1;
    }

    bool dfs(int u)
    {
        if (!u) return true;
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
        for (int u = 1; u <= n; u++) answer += (l[u] != 0);
        while (bfs())
        {
            for (int u = 1; u <= n; u++)
            {
                if (!l[u] && dfs(u)) answer++;
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
            if (dep[u] == n + 1) left.push_back(u);
        }
        for (int v = 1; v <= m; v++)
        {
            if (r[v] && dep[r[v]] != n + 1) right.push_back(v);
        }
        return {left, right};
    }
};

struct Kruskal
{
    struct Edge
    {
        int u, v;
        long long w;
    };
    int n;
    vector<Edge> e;
    vector<int> ids;
    long long weight = 0;

    Kruskal(int n) : n(n) {}

    int add(int u, int v, long long w)
    {
        e.push_back({u, v, w});
        return int(e.size()) - 1;
    }

    // Minimum spanning forest on 0..n-1; ties by edge id. Returns the component count.
    int run()
    {
        vector<int> order(e.size());
        iota(order.begin(), order.end(), 0);
        stable_sort(order.begin(), order.end(), [&](int a, int b) { return e[a].w < e[b].w; });
        dsu d(n);
        ids.clear();
        weight = 0;
        int cnt = n;
        for (int id : order)
            if (d.merge(e[id].u, e[id].v))
            {
                ids.push_back(id);
                weight += e[id].w;
                cnt--;
            }
        return cnt;
    }
};

struct Prim
{
    static constexpr long long inf = LLONG_MAX / 4;
    int n;
    vector<vector<long long>> cost;
    vector<int> pre;
    long long weight = 0;

    Prim(int n) : n(n), cost(n, vector<long long>(n, inf)) {}

    void add(int u, int v, long long w) { cost[u][v] = cost[v][u] = min(cost[u][v], w); }

    // O(n^2) minimum spanning forest on 0..n-1; returns the component count.
    int run()
    {
        vector<long long> d(n, inf);
        vector<bool> vis(n);
        pre.assign(n, -1);
        weight = 0;
        int cnt = 0;
        for (int step = 0; step < n; step++)
        {
            int u = -1;
            for (int v = 0; v < n; v++)
                if (!vis[v] && (u == -1 || d[v] < d[u])) u = v;
            if (d[u] == inf)
                cnt++;
            else
                weight += d[u];
            vis[u] = true;
            for (int v = 0; v < n; v++)
                if (!vis[v] && cost[u][v] < d[v]) d[v] = cost[u][v], pre[v] = u;
        }
        return cnt;
    }
};

struct Floyd
{
    static constexpr long long inf = LLONG_MAX / 4;
    struct Edge
    {
        int u, v;
        long long w;
    };
    int n;
    vector<Edge> e;
    vector<vector<long long>> dis;
    vector<vector<int>> nxt;

    Floyd(int n) : n(n) {}

    int add(int u, int v, long long w)
    {
        e.push_back({u, v, w});
        return int(e.size()) - 1;
    }

    // 1-based. False on a negative cycle; then every result is invalid.
    bool run()
    {
        dis.assign(n + 1, vector<long long>(n + 1, inf));
        nxt.assign(n + 1, vector<int>(n + 1, -1));
        for (int u = 1; u <= n; u++) dis[u][u] = 0;
        for (int id = 0; id < (int)e.size(); id++)
        {
            auto [u, v, w] = e[id];
            if (w < dis[u][v]) dis[u][v] = w, nxt[u][v] = id;
        }
        for (int k = 1; k <= n; k++)
        {
            if (dis[k][k] < 0) return false;
            for (int u = 1; u <= n; u++)
                if (dis[u][k] != inf)
                    for (int v = 1; v <= n; v++)
                        if (dis[k][v] != inf && dis[u][k] + dis[k][v] < dis[u][v])
                            dis[u][v] = dis[u][k] + dis[k][v], nxt[u][v] = nxt[u][k];
        }
        return true;
    }

    // Edge ids from s to t; empty if unreachable or s=t.
    vector<int> path(int s, int t) const
    {
        vector<int> ids;
        if (dis[s][t] == inf) return ids;
        for (; s != t; s = e[ids.back()].v) ids.push_back(nxt[s][t]);
        return ids;
    }
};

struct Spfa
{
    static constexpr long long inf = LLONG_MAX / 4;
    struct Edge
    {
        int u, v;
        long long w;
    };
    int n;
    vector<Edge> e;
    vector<vector<int>> g;
    vector<long long> dis;
    vector<int> pre;

    Spfa(int n) : n(n), g(n + 1) {}

    int add(int u, int v, long long w)
    {
        e.push_back({u, v, w});
        g[u].push_back(int(e.size()) - 1);
        return int(e.size()) - 1;
    }

    // 1-based; s=0 starts from every vertex (difference constraints). False on a negative cycle.
    bool run(int s)
    {
        dis.assign(n + 1, inf);
        pre.assign(n + 1, -1);
        vector<int> in(n + 1), len(n + 1);
        queue<int> q;
        for (int u = 1; u <= n; u++)
            if (!s || u == s) dis[u] = 0, in[u] = 1, q.push(u);
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            in[u] = 0;
            for (int id : g[u])
            {
                int v = e[id].v;
                if (dis[u] + e[id].w >= dis[v]) continue;
                dis[v] = dis[u] + e[id].w, pre[v] = id, len[v] = len[u] + 1;
                if (len[v] >= n) return false;
                if (!in[v]) in[v] = 1, q.push(v);
            }
        }
        return true;
    }

    // Edge ids of the shortest path to t; empty if unreachable or t is a start.
    vector<int> path(int t) const
    {
        vector<int> ids;
        if (dis[t] == inf) return ids;
        for (; pre[t] != -1; t = e[pre[t]].u) ids.push_back(pre[t]);
        reverse(ids.begin(), ids.end());
        return ids;
    }
};

struct BellmanFord
{
    static constexpr long long inf = LLONG_MAX / 4;
    struct Edge
    {
        int u, v;
        long long w;
    };
    int n;
    vector<Edge> e;
    vector<long long> dis;
    vector<int> pre, neg, cycle; // neg[v]: distance is -inf; cycle: edge ids of one negative cycle

    BellmanFord(int n) : n(n) {}

    int add(int u, int v, long long w)
    {
        e.push_back({u, v, w});
        return int(e.size()) - 1;
    }

    // 1-based; s=0 starts every vertex at 0 to find any negative cycle. True iff none found.
    bool run(int s)
    {
        dis.assign(n + 1, s ? inf : 0);
        pre.assign(n + 1, -1);
        neg.assign(n + 1, 0);
        cycle.clear();
        dis[s] = 0;
        int last = -1;
        for (int step = 0; step < n; step++)
        {
            last = -1;
            for (int id = 0; id < (int)e.size(); id++)
            {
                auto [u, v, w] = e[id];
                if (dis[u] == inf || dis[u] + w >= dis[v]) continue;
                dis[v] = dis[u] + w, pre[v] = id, last = v;
                if (step == n - 1) neg[v] = 1;
            }
            if (last == -1) break;
        }
        if (last != -1)
        {
            int x = last;
            for (int i = 0; i < n; i++) x = e[pre[x]].u;
            for (int y = x; cycle.empty() || y != x; y = e[pre[y]].u) cycle.push_back(pre[y]);
            reverse(cycle.begin(), cycle.end());
        }
        for (bool changed = true; changed;) // everything reachable from round n is -inf
        {
            changed = false;
            for (auto [u, v, w] : e)
                if (neg[u] && !neg[v]) neg[v] = 1, changed = true;
        }
        return cycle.empty();
    }

    // Finite shortest path as edge ids; empty for unreachable, -inf or t=s.
    vector<int> path(int t) const
    {
        vector<int> ids;
        if (dis[t] == inf || neg[t]) return ids;
        for (; pre[t] != -1; t = e[pre[t]].u) ids.push_back(pre[t]);
        reverse(ids.begin(), ids.end());
        return ids;
    }
};

// BEGIN matching_edges
pair<int, vector<array<bool, 2>>>
matching_edges(int n, int m, const vector<pair<int, int>> &edges)
{
    BipartiteMatching b(n, m);
    for (auto [u, v] : edges)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= m);
        b.add(u, v);
    }
    int size = b.solve(), s = n + m + 1, t = s + 1;
    SCC d(t);
    for (int u = 1; u <= n; u++)
        if (b.l[u])
            d.add(u, s);
        else
            d.add(s, u);
    for (int v = 1; v <= m; v++)
        if (b.r[v])
            d.add(t, n + v);
        else
            d.add(n + v, t);
    vector<bool> chosen(n + 1), used(edges.size());
    for (int i = 0; i < (int)edges.size(); i++)
    {
        auto [u, v] = edges[i];
        used[i] = b.l[u] == v && !chosen[u];
        if (used[i])
        {
            chosen[u] = true;
            d.add(n + v, u);
        }
        else
            d.add(u, n + v);
    }
    d.run();
    vector<array<bool, 2>> ans(edges.size());
    for (int i = 0; i < (int)edges.size(); i++)
    {
        auto [u, v] = edges[i];
        bool same = d.bel[u] == d.bel[n + v];
        ans[i] = {used[i] || same, used[i] && !same};
    }
    return {size, ans};
}

// END matching_edges

// BEGIN independent_set
// Maximum independent set; left/right IDs are separate and 1-based.
pair<vector<int>, vector<int>> independent_set(BipartiteMatching &g)
{
    g.solve();
    auto [a, b] = g.cover();
    vector<bool> x(g.n + 1, true), y(g.m + 1, true);
    for (int u : a) x[u] = false;
    for (int v : b) y[v] = false;
    vector<int> left, right;
    for (int u = 1; u <= g.n; u++)
    {
        if (x[u]) left.push_back(u);
    }
    for (int v = 1; v <= g.m; v++)
    {
        if (y[v]) right.push_back(v);
    }
    return {left, right};
}
// END independent_set
