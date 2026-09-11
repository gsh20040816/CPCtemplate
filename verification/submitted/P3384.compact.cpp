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

    void dfs1(int u, int p)
    {
        fa[u] = p;
        siz[u] = 1;
        son[u] = 0;
        for (int v : g[u])
        {
            if (v == p)
                continue;
            dep[v] = dep[u] + 1;
            dfs1(v, u);
            siz[u] += siz[v];
            if (!son[u] || siz[v] > siz[son[u]])
                son[u] = v;
        }
    }

    void dfs2(int u, int t)
    {
        top[u] = t;
        dfn[u] = ++timer;
        rk[timer] = u;
        if (son[u])
            dfs2(son[u], t);
        for (int v : g[u])
        {
            if (v != fa[u] && v != son[u])
                dfs2(v, v);
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

#include <cassert>
#include <vector>
using namespace std;

struct AffineSegTree
{
    using ll = long long;

    struct Node
    {
        ll sum = 0, mul = 1, add = 0;
    };

    int n, mod;
    vector<Node> t;

    AffineSegTree(const vector<ll> &a, int mod) : n(a.size()), mod(mod), t(4 * n + 4)
    {
        assert(n > 0 && mod > 0);
        build(1, 1, n, a);
    }

    ll norm(ll x) const
    {
        x %= mod;
        if (x < 0)
            x += mod;
        return x;
    }

    void pull(int p)
    {
        t[p].sum = (t[p * 2].sum + t[p * 2 + 1].sum) % mod;
    }

    void build(int p, int l, int r, const vector<ll> &a)
    {
        t[p] = Node{};
        if (l == r)
        {
            t[p].sum = norm(a[l - 1]);
            return;
        }
        int m = (l + r) / 2;
        build(p * 2, l, m, a);
        build(p * 2 + 1, m + 1, r, a);
        pull(p);
    }

    // New transform follows the old pending transform: x -> x*a+b.
    void apply(int p, int len, ll a, ll b)
    {
        t[p].sum = (t[p].sum * a % mod + len * b % mod) % mod;
        t[p].mul = t[p].mul * a % mod;
        t[p].add = (t[p].add * a % mod + b) % mod;
    }

    void push(int p, int l, int r)
    {
        if (t[p].mul == 1 && t[p].add == 0)
            return;
        int m = (l + r) / 2;
        apply(p * 2, m - l + 1, t[p].mul, t[p].add);
        apply(p * 2 + 1, r - m, t[p].mul, t[p].add);
        t[p].mul = 1;
        t[p].add = 0;
    }

    void update(int l, int r, ll a, ll b)
    {
        assert(1 <= l && l <= r && r <= n);
        update(1, 1, n, l, r, norm(a), norm(b));
    }

    void update(int p, int l, int r, int ql, int qr, ll a, ll b)
    {
        if (ql <= l && r <= qr)
        {
            apply(p, r - l + 1, a, b);
            return;
        }
        push(p, l, r);
        int m = (l + r) / 2;
        if (ql <= m)
            update(p * 2, l, m, ql, qr, a, b);
        if (qr > m)
            update(p * 2 + 1, m + 1, r, ql, qr, a, b);
        pull(p);
    }

    ll query(int l, int r)
    {
        assert(1 <= l && l <= r && r <= n);
        return query(1, 1, n, l, r);
    }

    ll query(int p, int l, int r, int ql, int qr)
    {
        if (ql <= l && r <= qr)
            return t[p].sum;
        push(p, l, r);
        int m = (l + r) / 2;
        ll answer = 0;
        if (ql <= m)
            answer += query(p * 2, l, m, ql, qr);
        if (qr > m)
            answer += query(p * 2 + 1, m + 1, r, ql, qr);
        return answer % mod;
    }
};

#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m, root, mod;
    std::cin >> n >> m >> root >> mod;
    std::vector<long long> values(n + 1);
    for (int u = 1; u <= n; u++)
        std::cin >> values[u];
    HLD h(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        std::cin >> u >> v;
        h.add(u, v);
    }
    h.build(root);
    std::vector<long long> ordered(n);
    for (int u = 1; u <= n; u++)
        ordered[h.dfn[u] - 1] = values[u];
    AffineSegTree seg(ordered, mod);
    while (m--)
    {
        int op, u;
        std::cin >> op >> u;
        if (op == 1)
        {
            int v;
            long long x;
            std::cin >> v >> x;
            h.path(u,
                   v,
                   [&](int l, int r)
                   {
                       seg.update(l, r, 1, x);
                   });
        }
        else if (op == 2)
        {
            int v;
            std::cin >> v;
            long long answer = 0;
            h.path(u,
                   v,
                   [&](int l, int r)
                   {
                       answer = (answer + seg.query(l, r)) % mod;
                   });
            std::cout << answer << '\n';
        }
        else if (op == 3)
        {
            long long x;
            std::cin >> x;
            seg.update(h.dfn[u], h.dfn[u] + h.siz[u] - 1, 1, x);
        }
        else
            std::cout << seg.query(h.dfn[u], h.dfn[u] + h.siz[u] - 1) << '\n';
    }
}
