#pragma once
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

struct Floyd
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
    vector<vector<I>> dis;
    vector<vector<int>> nxt;

    Floyd(int n) : n(n)
    {
        assert(0 < n && n < INT_MAX);
    }

    int add(int u, int v, long long w)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        assert(e.size() < INT_MAX);
        int id = e.size();
        e.push_back({u, v, w});
        valid = false;
        return id;
    }

    // Any negative cycle invalidates all results, including finite pairs.
    bool run()
    {
        valid = false;
        dis.assign(n + 1, vector<I>(n + 1, inf));
        nxt.assign(n + 1, vector<int>(n + 1, -1));
        for (int u = 1; u <= n; u++) dis[u][u] = 0;
        for (int id = 0; id < (int)e.size(); id++)
        {
            auto [u, v, w] = e[id];
            if (w < dis[u][v])
            {
                dis[u][v] = w;
                nxt[u][v] = id;
            }
        }
        for (int k = 1; k <= n; k++)
        {
            // Stop before using a negative diagonal as a pivot.
            if (dis[k][k] < 0) return false;
            for (int u = 1; u <= n; u++)
            {
                if (dis[u][k] == inf) continue;
                for (int v = 1; v <= n; v++)
                    if (dis[k][v] != inf && dis[u][v] > dis[u][k] + dis[k][v])
                    {
                        dis[u][v] = dis[u][k] + dis[k][v];
                        nxt[u][v] = nxt[u][k];
                    }
            }
        }
        valid = true;
        return true;
    }

    // Forward original-edge IDs; empty for unreachable or s=t.
    vector<int> path(int s, int t) const
    {
        assert(valid && 1 <= s && s <= n && 1 <= t && t <= n);
        vector<int> ids;
        if (dis[s][t] == inf) return ids;
        while (s != t)
        {
            int id = nxt[s][t];
            ids.push_back(id);
            s = e[id].v;
        }
        return ids;
    }
};
