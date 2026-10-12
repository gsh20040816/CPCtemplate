#include <bits/stdc++.h>
#include <cassert>
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

    void dfs1(int u, int p)
    {
        fa[u] = p;
        siz[u] = 1;
        son[u] = 0;
        for (int v : g[u])
        {
            if (v == p) continue;
            dep[v] = dep[u] + 1;
            dfs1(v, u);
            siz[u] += siz[v];
            if (!son[u] || siz[v] > siz[son[u]]) son[u] = v;
        }
    }

    void dfs2(int u, int t)
    {
        top[u] = t;
        dfn[u] = ++timer;
        rk[timer] = u;
        if (son[u]) dfs2(son[u], t);
        for (int v : g[u])
        {
            if (v != fa[u] && v != son[u]) dfs2(v, v);
        }
    }

    // Connected tree only. Recursive DFS; subtree interval is [dfn, dfn+siz-1].
    void build(int root = 1)
    {
        assert(1 <= root && root <= n);
        timer = 0;
        dep[root] = 0;
        dfs1(root, root);
        dfs2(root, root);
        assert(timer == n);
    }

    int lca(int u, int v) const
    {
        while (top[u] != top[v])
        {
            if (dep[top[u]] < dep[top[v]]) swap(u, v);
            u = fa[top[u]];
        }
        return dep[u] < dep[v] ? u : v;
    }

    // Commutative operations only; edge=true excludes the LCA's position.
    template <class F> void path(int u, int v, F work, bool edge = false) const
    {
        while (top[u] != top[v])
        {
            if (dep[top[u]] < dep[top[v]]) swap(u, v);
            work(dfn[top[u]], dfn[u]);
            u = fa[top[u]];
        }
        if (dep[u] > dep[v]) swap(u, v);
        if (dfn[u] + edge <= dfn[v]) work(dfn[u] + edge, dfn[v]);
    }

    // Emit u-to-v order; reverse=true traverses the closed interval from r to l.
    template <class F> void path_ordered(int u, int v, F work, bool edge = false) const
    {
        vector<pair<int, int>> down;
        while (top[u] != top[v])
        {
            if (dep[top[u]] >= dep[top[v]])
            {
                work(dfn[top[u]], dfn[u], true);
                u = fa[top[u]];
            }
            else
            {
                down.emplace_back(dfn[top[v]], dfn[v]);
                v = fa[top[v]];
            }
        }
        if (dep[u] >= dep[v])
        {
            if (dfn[v] + edge <= dfn[u]) work(dfn[v] + edge, dfn[u], true);
        }
        else if (dfn[u] + edge <= dfn[v]) work(dfn[u] + edge, dfn[v], false);
        for (auto it = down.rbegin(); it != down.rend(); ++it)
            work(it->first, it->second, false);
    }
};

struct ColorComponents
{
    const HLD &h;
    vector<int> col;
    array<set<int>, 2> pos;
    array<vector<long long>, 2> bit;

    ColorComponents(const HLD &tree, vector<int> color = {})
        : h(tree), col(move(color))
    {
        assert(h.n >= 1 && h.n <= INT_MAX / 2 && h.timer == h.n);
        if (col.empty()) col.resize(h.n + 1);
        assert(col.size() == size_t(h.n + 1));
        vector<array<int, 2>> f(h.n + 1);
        for (int i = h.n; i >= 1; i--)
        {
            int u = h.rk[i];
            assert(col[u] == 0 || col[u] == 1);
            pos[col[u]].insert(i);
            f[u][0]++;
            f[u][1]++;
            if (h.fa[u] != u) f[h.fa[u]][col[u]] += f[u][col[u]];
        }
        for (int c = 0; c < 2; c++)
        {
            bit[c].resize(h.n + 1);
            for (int i = 1; i <= h.n; i++)
                bit[c][i] = f[h.rk[i]][c] - f[h.rk[i - 1]][c];
            for (int i = 1; i <= h.n; i++)
            {
                int j = i + (i & -i);
                if (j <= h.n) bit[c][j] += bit[c][i];
            }
        }
    }

    void add(int c, int x, long long v)
    {
        for (; x <= h.n; x += x & -x) bit[c][x] += v;
    }

    long long value(int u, int c) const
    {
        long long ans = 0;
        for (int x = h.dfn[u]; x; x -= x & -x) ans += bit[c][x];
        return ans;
    }

    int top(int u) const
    {
        int c = col[u];
        while (true)
        {
            int v = h.top[u];
            auto it = pos[c ^ 1].upper_bound(h.dfn[u]);
            if (it != pos[c ^ 1].begin())
            {
                --it;
                if (*it >= h.dfn[v]) return h.rk[*it + 1];
            }
            if (h.fa[v] == v || col[h.fa[v]] != c) return v;
            u = h.fa[v];
        }
    }

    void change(int u, int c, long long delta)
    {
        int p = h.fa[u];
        if (p == u) return;
        int v = p;
        if (col[p] == c)
        {
            v = top(p);
            v = h.fa[v];
        }
        h.path(p, v, [&](int l, int r)
        {
            add(c, l, delta);
            add(c, r + 1, -delta);
        });
    }

    void flip(int u)
    {
        int c = col[u];
        change(u, c, -value(u, c));
        change(u, c ^ 1, value(u, c ^ 1));
        pos[c].erase(h.dfn[u]);
        col[u] ^= 1;
        pos[c ^ 1].insert(h.dfn[u]);
    }

    int query(int u) const
    {
        return value(top(u), col[u]);
    }
};

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    HLD h(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        h.add(u, v);
    }
    h.build();
    ColorComponents tree(h);
    int q;
    cin >> q;
    while (q--)
    {
        int op, u;
        cin >> op >> u;
        if (op == 0) cout << tree.query(u) << '\n';
        else tree.flip(u);
    }
}
