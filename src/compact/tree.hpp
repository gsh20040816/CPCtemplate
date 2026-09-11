#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct HLD
{
    int n, timer = 0;
    vector<vector<int>> g;
    vector<int> fa, dep, siz, son, top, dfn, rk;

    HLD(int n)
        : n(n),
          g(n + 1),
          fa(n + 1),
          dep(n + 1),
          siz(n + 1),
          son(n + 1),
          top(n + 1),
          dfn(n + 1),
          rk(n + 1)
    {
    }

    void add(int u, int v)
    {
        g[u].push_back(v);
        g[v].push_back(u);
    }

    // Connected tree only; iterative build avoids chain-shaped DFS stack overflow.
    void build(int root = 1)
    {
        fill(fa.begin(), fa.end(), 0);
        fill(son.begin(), son.end(), 0);
        vector<int> order{root};
        fa[root] = root;
        dep[root] = 0;
        for (int i = 0; i < (int)order.size(); i++)
        {
            int u = order[i];
            for (int v : g[u])
                if (v != fa[u])
                {
                    fa[v] = u;
                    dep[v] = dep[u] + 1;
                    order.push_back(v);
                }
        }
        assert((int)order.size() == n);
        for (int i = n - 1; i >= 0; i--)
        {
            int u = order[i];
            siz[u] = 1;
            for (int v : g[u])
                if (fa[v] == u && v != u)
                {
                    siz[u] += siz[v];
                    if (!son[u] || siz[v] > siz[son[u]])
                        son[u] = v;
                }
        }
        timer = 0;
        vector<pair<int, int>> st{{root, root}};
        while (!st.empty())
        {
            auto [u, t] = st.back();
            st.pop_back();
            for (; u; u = son[u])
            {
                top[u] = t;
                dfn[u] = ++timer;
                rk[timer] = u;
                for (int v : g[u])
                    if (fa[v] == u && v != u && v != son[u])
                        st.push_back({v, v});
            }
        }
    }

    int lca(int u, int v) const
    {
        while (top[u] != top[v])
        {
            if (dep[top[u]] < dep[top[v]])
                swap(u, v);
            u = fa[top[u]];
        }
        return dep[u] < dep[v] ? u : v;
    }

    // Commutative operations only; edge=true excludes the LCA's position.
    template <class F> void path(int u, int v, F work, bool edge = false) const
    {
        while (top[u] != top[v])
        {
            if (dep[top[u]] < dep[top[v]])
                swap(u, v);
            work(dfn[top[u]], dfn[u]);
            u = fa[top[u]];
        }
        if (dep[u] > dep[v])
            swap(u, v);
        if (dfn[u] + edge <= dfn[v])
            work(dfn[u] + edge, dfn[v]);
    }
};
