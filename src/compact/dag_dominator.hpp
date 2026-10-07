#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

struct DagDominator
{
    int n, lg = 1;
    vector<vector<int>> g, up;
    vector<int> idom, dep, order;

    DagDominator(int n) : n(n), g(n + 1)
    {
        assert(n > 0);
        while ((1LL << lg) <= n)
            lg++;
    }

    void add(int u, int v)
    {
        g[u].push_back(v);
    }

    int lca(int u, int v) const
    {
        if (!u || !v)
            return u + v;
        if (dep[u] < dep[v])
            swap(u, v);
        for (int k = lg - 1; k >= 0; k--)
            if (dep[up[k][u]] >= dep[v])
                u = up[k][u];
        if (u == v)
            return u;
        for (int k = lg - 1; k >= 0; k--)
            if (up[k][u] != up[k][v])
            {
                u = up[k][u];
                v = up[k][v];
            }
        return up[0][u];
    }

    bool build(int root)
    {
        assert(1 <= root && root <= n);
        idom.clear();
        dep.clear();
        up.clear();
        order.clear();
        vector<int> deg(n + 1);
        for (int u = 1; u <= n; u++)
            for (int v : g[u])
                deg[v]++;
        for (int u = 1; u <= n; u++)
            if (!deg[u])
                order.push_back(u);
        for (int i = 0; i < (int)order.size(); i++)
            for (int v : g[order[i]])
                if (--deg[v] == 0)
                    order.push_back(v);
        if ((int)order.size() != n)
        {
            order.clear();
            return false;
        }
        idom.assign(n + 1, 0);
        dep.assign(n + 1, 0);
        up.assign(lg, vector<int>(n + 1));
        idom[root] = root;
        for (int u : order)
        {
            if (!idom[u])
                continue;
            dep[u] = u == root ? 1 : dep[idom[u]] + 1;
            up[0][u] = idom[u];
            for (int k = 1; k < lg; k++)
                up[k][u] = up[k - 1][up[k - 1][u]];
            for (int v : g[u])
                idom[v] = lca(idom[v], u);
        }
        return true;
    }
};
