#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <queue>
#include <vector>
using namespace std;

struct Spfa
{
    using I = __int128_t;
    static constexpr I inf = I(1) << 126;
    struct Edge
    {
        int u, v;
        long long w;
    };
    int n;
    bool valid = false;
    vector<Edge> e;
    vector<vector<int>> g;
    vector<I> dis;
    vector<int> pre;

    Spfa(int n) : n(n), g(n + 1)
    {
        assert(0 < n && n < INT_MAX);
    }

    int add(int u, int v, long long w)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        assert(e.size() < INT_MAX);
        int id = e.size();
        e.push_back({u, v, w});
        g[u].push_back(id);
        valid = false;
        return id;
    }

    // s=0 checks the whole graph. A false result invalidates all distances.
    bool run(int s)
    {
        assert(0 <= s && s <= n);
        valid = false;
        dis.assign(n + 1, inf);
        pre.assign(n + 1, -1);
        vector<int> in(n + 1), len(n + 1);
        queue<int> q;
        for (int u = 1; u <= n; u++)
            if (!s || u == s)
            {
                dis[u] = 0;
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
                auto [from, v, w] = e[id];
                if (dis[v] <= dis[u] + w) continue;
                dis[v] = dis[u] + w;
                pre[v] = id;
                len[v] = len[u] + 1;
                if (len[v] >= n) return false;
                if (!in[v])
                {
                    in[v] = 1;
                    q.push(v);
                }
            }
        }
        valid = true;
        return true;
    }

    // Forward original-edge IDs; empty for unreachable or a zero-edge path.
    vector<int> path(int t) const
    {
        assert(valid && 1 <= t && t <= n);
        vector<int> ids;
        if (dis[t] == inf) return ids;
        while (pre[t] != -1)
        {
            ids.push_back(pre[t]);
            t = e[pre[t]].u;
        }
        reverse(ids.begin(), ids.end());
        return ids;
    }
};
