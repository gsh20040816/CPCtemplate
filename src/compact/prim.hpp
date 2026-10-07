#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

struct Prim
{
    using I = __int128_t;
    static constexpr I inf = I(1) << 126;
    int n;
    vector<vector<I>> cost;
    vector<int> pre;
    I weight = 0;

    Prim(int n) : n(n), cost(n, vector<I>(n, inf))
    {
        assert(n >= 0);
    }

    void add(int u, int v, long long w)
    {
        assert(0 <= u && u < n && 0 <= v && v < n);
        cost[u][v] = cost[v][u] = min(cost[u][v], I(w));
    }

    // Rebuild a minimum spanning forest; return its component count.
    int run()
    {
        vector<I> d(n, inf);
        vector<bool> vis(n);
        pre.assign(n, -1);
        weight = 0;
        int cnt = 0;
        for (int step = 0; step < n; step++)
        {
            int u = -1;
            for (int v = 0; v < n; v++)
            {
                if (!vis[v] && (u == -1 || d[v] < d[u])) u = v;
            }
            if (d[u] == inf)
            {
                cnt++;
            }
            else
            {
                weight += d[u];
            }
            vis[u] = true;
            for (int v = 0; v < n; v++)
                if (!vis[v] && cost[u][v] < d[v])
                {
                    d[v] = cost[u][v];
                    pre[v] = u;
                }
        }
        return cnt;
    }
};
