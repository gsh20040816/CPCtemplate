#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <queue>
#include <vector>
using namespace std;

struct BellmanFord
{
    using I = __int128_t;
    static constexpr I inf = I(1) << 126;
    struct Edge
    {
        int u, v;
        long long w;
    };
    int n;
    bool ready = false;
    vector<Edge> e;
    vector<vector<int>> g;
    vector<I> dis;
    vector<int> pre, neg, cycle;

    BellmanFord(int n) : n(n)
    {
        assert(0 < n && n < INT_MAX);
        g.resize(n + 1);
    }

    int add(int u, int v, long long w)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        assert(e.size() < INT_MAX);
        int id = e.size();
        e.push_back({u, v, w});
        g[u].push_back(v);
        ready = false;
        return id;
    }

    // s=0 initializes every vertex to zero, for detecting any negative cycle.
    bool run(int s)
    {
        assert(0 <= s && s <= n);
        dis.assign(n + 1, s ? inf : 0);
        pre.assign(n + 1, -1);
        neg.assign(n + 1, 0);
        cycle.clear();
        dis[s] = 0;
        queue<int> q;
        int last = -1;
        for (int step = 0; step < n; step++)
        {
            last = -1;
            for (int id = 0; id < (int)e.size(); id++)
            {
                auto [u, v, w] = e[id];
                if (dis[u] == inf || dis[v] <= dis[u] + w) continue;
                dis[v] = dis[u] + w;
                pre[v] = id;
                last = v;
                if (step == n - 1 && !neg[v])
                {
                    neg[v] = 1;
                    q.push(v);
                }
            }
            if (last == -1) break;
        }
        if (last != -1)
        {
            int x = last;
            for (int i = 0; i < n; i++) x = e[pre[x]].u;
            int start = x;
            do
            {
                cycle.push_back(pre[x]);
                x = e[pre[x]].u;
            } while (x != start);
            reverse(cycle.begin(), cycle.end());
        }
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            for (int v : g[u])
                if (!neg[v])
                {
                    neg[v] = 1;
                    q.push(v);
                }
        }
        ready = true;
        return cycle.empty();
    }

    // Finite path in forward original-edge IDs; empty also for unreachable/-inf.
    vector<int> path(int t) const
    {
        assert(ready && 1 <= t && t <= n);
        vector<int> ids;
        if (dis[t] == inf || neg[t]) return ids;
        while (pre[t] != -1)
        {
            ids.push_back(pre[t]);
            t = e[pre[t]].u;
        }
        reverse(ids.begin(), ids.end());
        return ids;
    }
};
