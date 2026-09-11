#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

template <int N, int NODES, int LOG = 20> struct Tree_Path_Kth
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, sum = 0;
    };

    static_assert(1 <= LOG && LOG <= 31);
    int n, tot;
    vector<int> g[N + 1];
    int up[LOG][N + 1], root[N + 1], dep[N + 1];
    ll value[N + 1];
    vector<ll> vals;
    Node t[NODES + 1];

    void Init(const vector<ll> &a)
    {
        n = a.size();
        assert(0 < n && n <= N && (1LL << LOG) > n);
        for ( int u = 1; u <= n; u++ )
        {
            value[u] = a[u - 1];
            g[u].clear();
        }
        root[0] = 0;
        for ( int j = 0; j < LOG; j++ )
            up[j][0] = 0;
    }

    void Insert(int u, int v)
    {
        g[u].push_back(v);
        g[v].push_back(u);
    }

    int Update(int old, int l, int r, int x)
    {
        assert(tot < NODES);
        int p = ++tot;
        t[p] = t[old];
        t[p].sum++;
        if ( l == r )
            return p;
        int m = (l + r) / 2;
        if ( x <= m )
        {
            int child = Update(t[old].l, l, m, x);
            t[p].l = child;
        }
        else
        {
            int child = Update(t[old].r, m + 1, r, x);
            t[p].r = child;
        }
        return p;
    }

    void Dfs(int u, int p)
    {
        up[0][u] = p;
        for ( int j = 1; j < LOG; j++ )
            up[j][u] = up[j - 1][up[j - 1][u]];
        int x = lower_bound(vals.begin(), vals.end(), value[u]) - vals.begin();
        root[u] = Update(root[p], 0, (int)vals.size() - 1, x);
        for ( int v : g[u] )
        {
            if ( v == p )
                continue;
            dep[v] = dep[u] + 1;
            Dfs(v, u);
        }
    }

    void Build(int r = 1)
    {
        assert(1 <= r && r <= n);
        vals.assign(value + 1, value + n + 1);
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        tot = 0;
        t[0] = Node{};
        dep[r] = 0;
        Dfs(r, 0);
    }

    int Lca(int u, int v) const
    {
        if ( dep[u] < dep[v] )
            swap(u, v);
        int diff = dep[u] - dep[v];
        for ( int j = 0; j < LOG; j++ )
            if ( diff >> j & 1 )
                u = up[j][u];
        if ( u == v )
            return u;
        for ( int j = LOG - 1; j >= 0; j-- )
            if ( up[j][u] != up[j][v] )
            {
                u = up[j][u];
                v = up[j][v];
            }
        return up[0][u];
    }

    ll Kth(int u, int v, int k) const
    {
        int z = Lca(u, v);
        assert(1 <= k && k <= dep[u] + dep[v] - 2 * dep[z] + 1);
        int a = root[u], b = root[v], c = root[z], d = root[up[0][z]];
        int l = 0, r = (int)vals.size() - 1;
        while ( l < r )
        {
            int count = t[t[a].l].sum + t[t[b].l].sum - t[t[c].l].sum - t[t[d].l].sum;
            int m = (l + r) / 2;
            if ( k <= count )
            {
                a = t[a].l;
                b = t[b].l;
                c = t[c].l;
                d = t[d].l;
                r = m;
            }
            else
            {
                k -= count;
                a = t[a].r;
                b = t[b].r;
                c = t[c].r;
                d = t[d].r;
                l = m + 1;
            }
        }
        return vals[l];
    }
};
