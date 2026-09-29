#pragma once
#include "number_theory.hpp"

template <int mod> struct TreePathProducts
{
    using Z = ModInt<mod>;

    struct Node
    {
        int ch[2]{}, fa = 0;
        Z weight = 0, product = 1, left = 0, right = 0, virt = 0;
        bool rev = false;
    };

    vector<Node> a;

    // g is a nonempty tree, with 0-based vertices and one weight per vertex.
    TreePathProducts(const vector<vector<int>> &g, const vector<Z> &weight)
        : a(g.size() + 1)
    {
        assert(!g.empty() && g.size() == weight.size());
        auto dfs = [&](auto &&self, int u, int parent) -> void
        {
            int x = u + 1;
            a[x].fa = parent + 1;
            a[x].weight = weight[u];
            for (int v : g[u])
                if (v != parent)
                {
                    self(self, v, u);
                    a[x].virt += a[v + 1].left;
                }
            pull(x);
        };
        dfs(dfs, 0, -1);
    }

    bool is_root(int x) const
    {
        int f = a[x].fa;
        return a[f].ch[0] != x && a[f].ch[1] != x;
    }

    void pull(int x)
    {
        auto &t = a[x];
        const auto &l = a[t.ch[0]], &r = a[t.ch[1]];
        t.product = l.product * t.weight * r.product;
        t.left = l.left + l.product * t.weight * (Z(1) + t.virt + r.left);
        t.right = r.right + r.product * t.weight * (Z(1) + t.virt + l.right);
    }

    void reverse(int x)
    {
        if (!x) return;
        swap(a[x].ch[0], a[x].ch[1]);
        swap(a[x].left, a[x].right);
        a[x].rev = !a[x].rev;
    }

    void push(int x)
    {
        if (!a[x].rev) return;
        reverse(a[x].ch[0]);
        reverse(a[x].ch[1]);
        a[x].rev = false;
    }

    void push_path(int x)
    {
        if (!is_root(x)) push_path(a[x].fa);
        push(x);
    }

    void rotate(int x)
    {
        int y = a[x].fa, z = a[y].fa;
        int k = a[y].ch[1] == x, w = a[x].ch[k ^ 1];
        if (!is_root(y)) a[z].ch[a[z].ch[1] == y] = x;
        a[x].fa = z;
        a[y].ch[k] = w;
        if (w) a[w].fa = y;
        a[x].ch[k ^ 1] = y;
        a[y].fa = x;
        pull(y);
        pull(x);
    }

    void splay(int x)
    {
        push_path(x);
        while (!is_root(x))
        {
            int y = a[x].fa, z = a[y].fa;
            if (!is_root(y))
            {
                bool same = (a[y].ch[1] == x) == (a[z].ch[1] == y);
                rotate(same ? y : x);
            }
            rotate(x);
        }
    }

    void make_root(int x)
    {
        int last = 0;
        for (int y = x; y; y = a[y].fa)
        {
            splay(y);
            a[y].virt += a[a[y].ch[1]].left - a[last].left;
            a[y].ch[1] = last;
            if (last) a[last].fa = y;
            pull(y);
            last = y;
        }
        splay(x);
        reverse(x);
    }

    void set(int u, Z weight)
    {
        int x = u + 1;
        make_root(x);
        a[x].weight = weight;
        pull(x);
    }

    Z query(int u)
    {
        int x = u + 1;
        make_root(x);
        return a[x].left;
    }
};
