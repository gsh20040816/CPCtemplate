#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

struct TreePathKth
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, sum = 0;
    };

    int n, lg;
    vector<vector<int>> g, up;
    vector<int> root, dep;
    vector<ll> value, vals;
    vector<Node> t;

    TreePathKth(const vector<ll> &a)
        : n(a.size()), g(n + 1), root(n + 1), dep(n + 1), value(a)
    {
        assert(n > 0);
        lg = 1;
        while ((1LL << lg) <= n) lg++;
        up.assign(lg, vector<int>(n + 1));
    }

    void add(int u, int v)
    {
        g[u].push_back(v);
        g[v].push_back(u);
    }

    int insert(int old, int l, int r, int x)
    {
        int p = t.size();
        Node copy = t[old];
        t.push_back(copy);
        t[p].sum++;
        if (l == r) return p;
        int m = (l + r) / 2;
        if (x <= m)
        {
            int child = insert(t[old].l, l, m, x);
            t[p].l = child;
        }
        else
        {
            int child = insert(t[old].r, m + 1, r, x);
            t[p].r = child;
        }
        return p;
    }

    void dfs(int u, int p)
    {
        up[0][u] = p;
        for (int j = 1; j < lg; j++) up[j][u] = up[j - 1][up[j - 1][u]];
        int x = lower_bound(vals.begin(), vals.end(), value[u - 1]) - vals.begin();
        root[u] = insert(root[p], 0, (int)vals.size() - 1, x);
        for (int v : g[u])
        {
            if (v == p) continue;
            dep[v] = dep[u] + 1;
            dfs(v, u);
        }
    }

    void build(int r = 1)
    {
        assert(1 <= r && r <= n);
        vals = value;
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        t.assign(1, Node{});
        dep[r] = 0;
        dfs(r, 0);
    }

    int lca(int u, int v) const
    {
        if (dep[u] < dep[v]) swap(u, v);
        int diff = dep[u] - dep[v];
        for (int j = 0; j < lg; j++)
            if (diff >> j & 1) u = up[j][u];
        if (u == v) return u;
        for (int j = lg - 1; j >= 0; j--)
            if (up[j][u] != up[j][v])
            {
                u = up[j][u];
                v = up[j][v];
            }
        return up[0][u];
    }

    ll kth(int u, int v, int k) const
    {
        int z = lca(u, v);
        assert(1 <= k && k <= dep[u] + dep[v] - 2 * dep[z] + 1);
        int a = root[u], b = root[v], c = root[z], d = root[up[0][z]];
        int l = 0, r = (int)vals.size() - 1;
        while (l < r)
        {
            int count = t[t[a].l].sum + t[t[b].l].sum - t[t[c].l].sum - t[t[d].l].sum;
            int m = (l + r) / 2;
            if (k <= count)
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
