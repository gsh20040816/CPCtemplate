#pragma once
#include "tree.hpp"

// BEGIN DynamicDP
// Dynamic DP: max-weight independent set of a tree under point weight changes (P4719).
// Vertices 1..n, built HLD (any root). f0/f1 = best in subtree with u excluded/included.
struct DynamicDP
{
    using ll = long long;
    static constexpr ll NEG = LLONG_MIN / 4;
    struct M
    {
        ll a[2][2];
    };

    // (max,+) product; matrices along a heavy chain multiply from top to bottom.
    static M mul(const M &x, const M &y)
    {
        M r;
        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++) r.a[i][j] = max(x.a[i][0] + y.a[0][j], x.a[i][1] + y.a[1][j]);
        return r;
    }

    const HLD &h;
    int n;
    vector<ll> w, g0, g1; // g0 = sum max(f0,f1), g1 = w + sum f0, over light children only
    vector<int> ed;       // ed[top] = dfn of the chain's last vertex
    vector<M> t;

    M leaf(int u) const { return {{{g0[u], g0[u]}, {g1[u], NEG}}}; }

    void build(int p, int l, int r)
    {
        if (l == r)
        {
            t[p] = leaf(h.rk[l]);
            return;
        }
        int m = (l + r) / 2;
        build(2 * p, l, m), build(2 * p + 1, m + 1, r);
        t[p] = mul(t[2 * p], t[2 * p + 1]);
    }

    void update(int p, int l, int r, int x)
    {
        if (l == r)
        {
            t[p] = leaf(h.rk[l]);
            return;
        }
        int m = (l + r) / 2;
        x <= m ? update(2 * p, l, m, x) : update(2 * p + 1, m + 1, r, x);
        t[p] = mul(t[2 * p], t[2 * p + 1]);
    }

    M query(int p, int l, int r, int ql, int qr) const
    {
        if (ql <= l && r <= qr) return t[p];
        int m = (l + r) / 2;
        if (qr <= m) return query(2 * p, l, m, ql, qr);
        if (ql > m) return query(2 * p + 1, m + 1, r, ql, qr);
        return mul(query(2 * p, l, m, ql, qr), query(2 * p + 1, m + 1, r, ql, qr));
    }

    // (f0, f1) of a chain top: chain product applied to the empty vector (0, -inf).
    pair<ll, ll> chain(int top) const
    {
        M p = query(1, 1, n, h.dfn[top], ed[top]);
        return {p.a[0][0], p.a[1][0]};
    }

    DynamicDP(const HLD &h, const vector<ll> &weight) : h(h), n(h.n), w(weight), g0(n + 1), g1(n + 1), ed(n + 1), t(4 * n + 4)
    {
        vector<ll> f0(n + 1), f1(n + 1);
        for (int i = n; i >= 1; i--)
        {
            int u = h.rk[i];
            f1[u] += w[u], g1[u] += w[u];
            for (int v : h.g[u])
                if (v != h.fa[u])
                {
                    f0[u] += max(f0[v], f1[v]), f1[u] += f0[v];
                    if (v != h.son[u]) g0[u] += max(f0[v], f1[v]), g1[u] += f0[v];
                }
        }
        for (int i = 1; i <= n; i++) ed[h.top[h.rk[i]]] = i;
        build(1, 1, n);
    }

    // Set w[u] = val in O(log^2 n).
    void set(int u, ll val)
    {
        g1[u] += val - w[u], w[u] = val;
        while (true)
        {
            int top = h.top[u];
            auto old = chain(top);
            update(1, 1, n, h.dfn[u]);
            auto now = chain(top);
            if (h.fa[top] == top) break; // root chain
            int p = h.fa[top];
            g0[p] += max(now.first, now.second) - max(old.first, old.second);
            g1[p] += now.first - old.first;
            u = p;
        }
    }

    // Maximum weight of an independent set in the whole tree.
    ll answer() const
    {
        auto [a, b] = chain(h.rk[1]);
        return max(a, b);
    }
};
// END DynamicDP
