#pragma once
#include "data_structure.hpp"

struct Kruskal
{
    using I = __int128_t;
    struct Edge
    {
        int u, v;
        long long w;
    };

    int n;
    vector<Edge> e;
    vector<int> ids;
    I weight = 0;

    Kruskal(int n) : n(n)
    {
        assert(n >= 0);
    }

    int add(int u, int v, long long w)
    {
        assert(0 <= u && u < n && 0 <= v && v < n);
        assert(e.size() < INT_MAX);
        e.push_back({u, v, w});
        return int(e.size()) - 1;
    }

    // Rebuild a minimum spanning forest; return its component count.
    int run()
    {
        vector<int> order(e.size());
        iota(order.begin(), order.end(), 0);
        sort(order.begin(), order.end(), [&](int a, int b)
        {
            return tie(e[a].w, a) < tie(e[b].w, b);
        });
        dsu d(n);
        ids.clear();
        weight = 0;
        int cnt = n;
        for (int id : order)
        {
            auto [u, v, w] = e[id];
            u = d.find(u);
            v = d.find(v);
            if (u == v) continue;
            if (d.sz[u] < d.sz[v]) swap(u, v);
            d.merge(u, v);
            ids.push_back(id);
            weight += I(w);
            cnt--;
        }
        return cnt;
    }
};
