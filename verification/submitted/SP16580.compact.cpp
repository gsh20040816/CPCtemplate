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

struct ColorMax
{
    const HLD &h;
    vector<int> col, tail;
    vector<long long> weight, seg;
    vector<array<multiset<long long>, 2>> light;
    array<set<int>, 2> pos;

    ColorMax(const HLD &tree, vector<int> color, vector<long long> w)
        : h(tree), col(move(color)), tail(h.n + 1), weight(move(w)),
          seg(2 * h.n, LLONG_MIN), light(h.n + 1)
    {
        assert(h.n >= 1 && h.n <= INT_MAX / 2 && h.timer == h.n);
        assert(col.size() == size_t(h.n + 1));
        assert(weight.size() == size_t(h.n + 1));
        vector<long long> f = weight;
        for (int i = h.n; i >= 1; i--)
        {
            int u = h.rk[i];
            assert(col[u] == 0 || col[u] == 1);
            pos[col[u]].insert(i);
            tail[h.top[u]] = max(tail[h.top[u]], i);
            int p = h.fa[u];
            if (p == u) continue;
            if (col[p] == col[u]) f[p] = max(f[p], f[u]);
            if (h.son[p] != u) light[p][col[u]].insert(f[u]);
        }
        for (int u = 1; u <= h.n; u++) seg[h.n + h.dfn[u] - 1] = base(u);
        for (int i = h.n - 1; i; i--) seg[i] = max(seg[2 * i], seg[2 * i + 1]);
    }

    long long base(int u) const
    {
        long long ans = weight[u];
        if (!light[u][col[u]].empty()) ans = max(ans, *light[u][col[u]].rbegin());
        return ans;
    }

    void put(int u)
    {
        int x = h.n + h.dfn[u] - 1;
        seg[x] = base(u);
        for (x /= 2; x; x /= 2) seg[x] = max(seg[2 * x], seg[2 * x + 1]);
    }

    long long down(int u) const
    {
        int r = tail[h.top[u]];
        auto it = pos[col[u] ^ 1].upper_bound(h.dfn[u]);
        if (it != pos[col[u] ^ 1].end()) r = min(r, *it - 1);
        long long ans = LLONG_MIN;
        int l = h.n + h.dfn[u] - 1;
        r += h.n;
        while (l < r)
        {
            if (l & 1) ans = max(ans, seg[l++]);
            if (r & 1) ans = max(ans, seg[--r]);
            l /= 2;
            r /= 2;
        }
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

    void change(int u, int color, long long w)
    {
        assert(color == 0 || color == 1);
        bool first = true;
        while (true)
        {
            int t = h.top[u];
            int old = col[t];
            long long before = down(t);
            if (first)
            {
                pos[col[u]].erase(h.dfn[u]);
                col[u] = color;
                pos[col[u]].insert(h.dfn[u]);
                weight[u] = w;
                first = false;
            }
            put(u);
            if (h.fa[t] == t) break;
            int p = h.fa[t];
            auto it = light[p][old].find(before);
            assert(it != light[p][old].end());
            light[p][old].erase(it);
            light[p][col[t]].insert(down(t));
            u = p;
        }
    }

    void flip(int u)
    {
        change(u, col[u] ^ 1, weight[u]);
    }

    void set_weight(int u, long long w)
    {
        change(u, col[u], w);
    }

    long long query(int u) const
    {
        return down(top(u));
    }
};

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    while (cin >> n)
    {
        HLD h(n);
        for (int i = 1; i < n; i++)
        {
            int u, v;
            cin >> u >> v;
            h.add(u, v);
        }
        vector<int> color(n + 1);
        vector<long long> w(n + 1);
        for (int u = 1; u <= n; u++) cin >> color[u];
        for (int u = 1; u <= n; u++) cin >> w[u];
        h.build();
        ColorMax tree(h, color, w);
        int q;
        cin >> q;
        while (q--)
        {
            int op, u;
            cin >> op >> u;
            if (op == 0) cout << tree.query(u) << '\n';
            else if (op == 1) tree.flip(u);
            else
            {
                long long value;
                cin >> value;
                tree.set_weight(u, value);
            }
        }
    }
}
