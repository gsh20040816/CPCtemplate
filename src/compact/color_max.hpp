#pragma once
#include "tree.hpp"

// BEGIN ColorMax
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
// END ColorMax
