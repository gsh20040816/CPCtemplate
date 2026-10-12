#pragma once
#include "tree.hpp"

// BEGIN ColorComponents
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
// END ColorComponents
