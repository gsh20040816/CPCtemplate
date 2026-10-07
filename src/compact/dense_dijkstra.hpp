#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

struct DenseDijkstra
{
    using I = __int128_t;
    static constexpr I inf = I(1) << 126;
    int n, root = 0;
    bool valid = false;
    vector<vector<long long>> cost;
    vector<I> dis;
    vector<int> pre;

    DenseDijkstra(int n) : n(n), cost(n + 1, vector<long long>(n + 1, -1))
    {
        assert(0 < n && n < INT_MAX);
    }

    void add(int u, int v, long long w)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n && w >= 0);
        auto &x = cost[u][v];
        if (x == -1 || w < x) x = w;
        valid = false;
    }

    void run(int s)
    {
        assert(1 <= s && s <= n);
        root = s;
        dis.assign(n + 1, inf);
        pre.assign(n + 1, -1);
        vector<bool> vis(n + 1);
        dis[s] = 0;
        for (int step = 0; step < n; step++)
        {
            int u = 0;
            for (int v = 1; v <= n; v++)
            {
                if (!vis[v] && (!u || dis[v] < dis[u])) u = v;
            }
            if (!u || dis[u] == inf) break;
            vis[u] = true;
            for (int v = 1; v <= n; v++)
                if (!vis[v] && cost[u][v] >= 0 && dis[v] > dis[u] + cost[u][v])
                {
                    dis[v] = dis[u] + cost[u][v];
                    pre[v] = u;
                }
        }
        valid = true;
    }

    // Forward vertex IDs; empty iff unreachable, {root} for the root.
    vector<int> path(int t) const
    {
        assert(valid && 1 <= t && t <= n);
        if (dis[t] == inf) return {};
        vector<int> p;
        for (; t != -1; t = pre[t]) p.push_back(t);
        reverse(p.begin(), p.end());
        return p;
    }
};
