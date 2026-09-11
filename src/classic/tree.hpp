#pragma once
#include <cassert>
#include <algorithm>
#include <vector>
using namespace std;

template <int N> struct Heavy_Light_Decomposition
{
    int n, timer = 0;
    vector<int> g[N + 1];
    int fa[N + 1], dep[N + 1], siz[N + 1], son[N + 1];
    int top[N + 1], dfn[N + 1], rk[N + 1];

    void Init(int vertices)
    {
        assert(0 < vertices && vertices <= N);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
    }

    void Insert(int u, int v)
    {
        g[u].push_back(v);
        g[v].push_back(u);
    }

    void Dfs1(int u, int p)
    {
        fa[u] = p;
        siz[u] = 1;
        son[u] = 0;
        for ( int v : g[u] )
        {
            if ( v == p )
                continue;
            dep[v] = dep[u] + 1;
            Dfs1(v, u);
            siz[u] += siz[v];
            if ( !son[u] || siz[v] > siz[son[u]] )
                son[u] = v;
        }
    }

    void Dfs2(int u, int t)
    {
        top[u] = t;
        dfn[u] = ++timer;
        rk[timer] = u;
        if ( son[u] )
            Dfs2(son[u], t);
        for ( int v : g[u] )
        {
            if ( v != fa[u] && v != son[u] )
                Dfs2(v, v);
        }
    }

    // Connected tree only. Recursive DFS; subtree interval is [dfn, dfn+siz-1].
    void Build(int root = 1)
    {
        assert(1 <= root && root <= n);
        timer = 0;
        dep[root] = 0;
        Dfs1(root, root);
        Dfs2(root, root);
        assert(timer == n);
    }

    int Lca(int u, int v) const
    {
        while ( top[u] != top[v] )
        {
            if ( dep[top[u]] < dep[top[v]] )
                swap(u, v);
            u = fa[top[u]];
        }
        return dep[u] < dep[v] ? u : v;
    }

    // Commutative operations only; edge=true excludes the LCA's position.
    template <class F> void Path(int u, int v, F work, bool edge = false) const
    {
        while ( top[u] != top[v] )
        {
            if ( dep[top[u]] < dep[top[v]] )
                swap(u, v);
            work(dfn[top[u]], dfn[u]);
            u = fa[top[u]];
        }
        if ( dep[u] > dep[v] )
            swap(u, v);
        if ( dfn[u] + edge <= dfn[v] )
            work(dfn[u] + edge, dfn[v]);
    }
};
