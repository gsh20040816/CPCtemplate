#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

struct DagLongest
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
    vector<int> pre, ord;

    DagLongest(int n) : n(n), g(n + 1)
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

    // s=0 allows any starting vertex, including a zero-edge path.
    // A cycle anywhere returns false and invalidates all results.
    bool run(int s)
    {
        assert(0 <= s && s <= n);
        valid = false;
        dis.assign(n + 1, -inf);
        pre.assign(n + 1, -1);
        ord.clear();
        vector<int> deg(n + 1);
        for (auto [u, v, w] : e) deg[v]++;
        for (int u = 1; u <= n; u++)
        {
            if (!deg[u]) ord.push_back(u);
            if (!s || u == s) dis[u] = 0;
        }
        for (int i = 0; i < (int)ord.size(); i++)
        {
            int u = ord[i];
            for (int id : g[u])
            {
                auto [from, v, w] = e[id];
                if (dis[u] != -inf && dis[v] < dis[u] + w)
                {
                    dis[v] = dis[u] + w;
                    pre[v] = id;
                }
                if (!--deg[v]) ord.push_back(v);
            }
        }
        valid = (int)ord.size() == n;
        return valid;
    }

    // Forward original-edge IDs; inspect dis to distinguish unreachable.
    vector<int> path(int t) const
    {
        assert(valid && 1 <= t && t <= n);
        vector<int> ids;
        if (dis[t] == -inf) return ids;
        while (pre[t] != -1)
        {
            ids.push_back(pre[t]);
            t = e[pre[t]].u;
        }
        reverse(ids.begin(), ids.end());
        return ids;
    }
};
