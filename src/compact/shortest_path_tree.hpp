#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <functional>
#include <queue>
#include <utility>
#include <vector>
using namespace std;

struct ShortestPathTree
{
    using I = __int128_t;
    static constexpr I inf = I(1) << 126;
    struct Edge
    {
        int u, v;
        long long w;
    };
    int n, root = 0;
    bool valid = false;
    I weight = 0;
    vector<Edge> e;
    vector<vector<pair<int, int>>> g, tree;
    vector<I> dis;
    vector<int> bel, ids, pre;

    ShortestPathTree(int n) : n(n), g(n + 1)
    {
        assert(0 < n && n < INT_MAX);
    }

    int add(int u, int v, long long w)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n && w >= 0);
        assert(e.size() < INT_MAX);
        int id = e.size();
        e.push_back({u, v, w});
        g[u].push_back({v, id});
        g[v].push_back({u, id});
        valid = false;
        return id;
    }

    // Internal: span one reachable zero-weight component recursively.
    void zero(int u, int c)
    {
        bel[u] = c;
        for (auto [v, id] : g[u])
            if (!e[id].w && !bel[v])
            {
                ids.push_back(id);
                zero(v, c);
            }
    }

    // Internal: orient the selected undirected tree from the query root.
    void dfs(int u, int p)
    {
        for (auto [v, id] : tree[u])
            if (v != p)
            {
                pre[v] = id;
                dfs(v, u);
            }
    }

    // Minimum total edge weight among shortest-path trees of reachable vertices.
    // Returns the number of reachable vertices, including s.
    int run(int s)
    {
        assert(1 <= s && s <= n);
        valid = false;
        root = s;
        dis.assign(n + 1, inf);
        priority_queue<pair<I, int>, vector<pair<I, int>>, greater<pair<I, int>>> q;
        dis[s] = 0;
        q.push({0, s});
        while (!q.empty())
        {
            auto [d, u] = q.top();
            q.pop();
            if (d != dis[u]) continue;
            for (auto [v, id] : g[u])
                if (dis[v] > d + e[id].w)
                {
                    dis[v] = d + e[id].w;
                    q.push({dis[v], v});
                }
        }
        bel.assign(n + 1, 0);
        ids.clear();
        int cnt = 0, reached = 0;
        for (int u = 1; u <= n; u++)
            if (dis[u] != inf)
            {
                reached++;
                if (!bel[u]) zero(u, ++cnt);
            }
        vector<int> best(cnt + 1, -1);
        for (int u = 1; u <= n; u++)
            if (dis[u] != inf)
                for (auto [v, id] : g[u])
                    if (bel[u] != bel[v] && dis[v] == dis[u] + e[id].w)
                    {
                        int &b = best[bel[v]];
                        if (b == -1 || e[id].w < e[b].w) b = id;
                    }
        for (int c = 1; c <= cnt; c++)
            if (c != bel[s])
            {
                assert(best[c] != -1);
                ids.push_back(best[c]);
            }
        tree.assign(n + 1, {});
        weight = 0;
        for (int id : ids)
        {
            auto [u, v, w] = e[id];
            tree[u].push_back({v, id});
            tree[v].push_back({u, id});
            weight += w;
        }
        pre.assign(n + 1, -1);
        dfs(s, 0);
        valid = true;
        return reached;
    }

    // Forward undirected edge IDs; follow each edge from the current vertex.
    vector<int> path(int t) const
    {
        assert(valid && 1 <= t && t <= n);
        vector<int> p;
        if (dis[t] == inf) return p;
        while (t != root)
        {
            int id = pre[t];
            p.push_back(id);
            auto [u, v, w] = e[id];
            t = u == t ? v : u;
        }
        reverse(p.begin(), p.end());
        return p;
    }
};
