#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct Johnson
{
    using I = __int128_t;
    static constexpr I inf = I(1) << 120;
    int n;
    vector<tuple<int, int, long long>> edges;
    vector<vector<pair<int, long long>>> g;
    vector<I> h;
    bool ready = false;

    Johnson(int n) : n(n), g(n + 1), h(n + 1) { assert(n > 0); }

    void add(int u, int v, long long w)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        edges.push_back({u, v, w});
        g[u].push_back({v, w});
        ready = false;
    }

    bool build()
    {
        ready = false;
        fill(h.begin(), h.end(), 0);
        for (int step = 0; step < n; step++)
        {
            bool changed = false;
            for (auto [u, v, w] : edges)
                if (h[v] > h[u] + w)
                {
                    h[v] = h[u] + w;
                    changed = true;
                }
            if (!changed)
            {
                ready = true;
                return true;
            }
        }
        return false;
    }

    vector<I> distances(int s) const
    {
        assert(ready && 1 <= s && s <= n);
        vector<I> d(n + 1, inf);
        priority_queue<pair<I, int>, vector<pair<I, int>>, greater<pair<I, int>>> q;
        d[s] = 0;
        q.push({0, s});
        while (!q.empty())
        {
            auto [value, u] = q.top();
            q.pop();
            if (value != d[u]) continue;
            for (auto [v, w] : g[u])
            {
                I next = value + w + h[u] - h[v];
                if (next < d[v])
                {
                    d[v] = next;
                    q.push({next, v});
                }
            }
        }
        for (int v = 1; v <= n; v++)
            if (d[v] != inf) d[v] += h[v] - h[s];
        return d;
    }
};
