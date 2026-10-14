#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

#include "tree.hpp"

struct Mo
{
    struct Query
    {
        int l, r, id;
    };
    int n;
    vector<Query> q;

    Mo(int n) : n(n)
    {
        assert(n >= 0);
    }
    int add(int l, int r)
    {
        assert(0 <= l && l <= r && r <= n);
        int id = q.size();
        q.push_back({l, r, id});
        return id;
    }
    template <class Add, class Del, class Ans>
    void run(Add add, Del del, Ans ans, int block = 0) const
    {
        if (q.empty()) return;
        if (block == 0) block = max(1, int(n / sqrt(double(q.size()))));
        assert(block > 0);
        auto ord = q;
        sort(ord.begin(), ord.end(), [&](const Query &a, const Query &b)
        {
            int x = a.l / block;
            int y = b.l / block;
            if (x != y) return x < y;
            return x & 1 ? a.r > b.r : a.r < b.r;
        });
        int l = 0;
        int r = 0;
        for (auto a : ord)
        {
            while (l > a.l) add(--l);
            while (r < a.r) add(r++);
            while (l < a.l) del(l++);
            while (r > a.r) del(--r);
            ans(a.id);
        }
        while (l < r) del(l++);
    }
};

struct ModifiedMo
{
    struct Query
    {
        int l, r, t, id;
    };

    int n, m;
    vector<Query> q;

    ModifiedMo(int n, int m) : n(n), m(m) { assert(n > 0 && m >= 0); }

    int add(int l, int r, int t)
    {
        assert(0 <= l && l <= r && r <= n);
        assert(0 <= t && t <= m);
        int id = q.size();
        q.push_back({l, r, t, id});
        return id;
    }

    template <class Add, class Del, class Chg, class Ans>
    void run(Add add, Del del, Chg chg, Ans ans, int block = 0) const
    {
        if (q.empty()) return;
        if (block == 0) block = max(1, int(pow(n, 2.0 / 3)));
        assert(block > 0);
        auto ord = q;
        auto cmp = [&](const Query &a, const Query &b)
        {
            int x = a.l / block, y = b.l / block;
            if (x != y) return x < y;
            int p = a.r / block, q = b.r / block;
            if (p != q) return (x & 1) ? p > q : p < q;
            return ((x ^ p) & 1) ? a.t > b.t : a.t < b.t;
        };
        sort(ord.begin(), ord.end(), cmp);
        int l = 0, r = 0, t = 0;
        for (auto q : ord)
        {
            while (t < q.t)
            {
                chg(t, true, l, r);
                t++;
            }
            while (t > q.t)
            {
                t--;
                chg(t, false, l, r);
            }
            while (l > q.l) add(--l);
            while (r < q.r) add(r++);
            while (l < q.l) del(l++);
            while (r > q.r) del(--r);
            ans(q.id);
        }
    }
};

struct RollbackMo
{
    struct Query
    {
        int l, r, id;
    };

    int n;
    vector<Query> q;

    RollbackMo(int n) : n(n)
    {
        assert(n >= 0);
    }

    int add(int l, int r)
    {
        assert(0 <= l && l <= r && r <= n);
        int id = q.size();
        q.push_back({l, r, id});
        return id;
    }

    template <class Add, class Snap, class Undo, class Ans>
    void run(Add add, Snap snapshot, Undo rollback, Ans ans, int block = 0) const
    {
        if (q.empty()) return;
        if (block == 0) block = max(1, int(n / sqrt(double(q.size()))));
        assert(block > 0);
        auto ord = q;
        sort(ord.begin(), ord.end(), [&](const Query &a, const Query &b)
        {
            int x = a.l / block, y = b.l / block;
            if (x != y) return x < y;
            return a.r < b.r;
        });
        auto empty = snapshot();
        int last = -1, r = 0;
        for (auto a : ord)
        {
            int b = a.l / block;
            int end = a.l + min(block - a.l % block, n - a.l);
            if (b != last)
            {
                rollback(empty);
                last = b;
                r = end;
            }
            if (a.r <= end)
            {
                auto saved = snapshot();
                for (int i = a.l; i < a.r; i++) add(i);
                ans(a.id);
                rollback(saved);
                continue;
            }
            while (r < a.r) add(r++);
            auto saved = snapshot();
            for (int i = end; i > a.l; ) add(--i);
            ans(a.id);
            rollback(saved);
        }
        rollback(empty);
    }
};

struct TreeMo
{
    struct Query
    {
        int l, r, extra, id;
    };

    const HLD &tree;
    vector<int> in, out, euler;
    vector<Query> q;

    TreeMo(const HLD &tree) : tree(tree), in(tree.n + 1), out(tree.n + 1)
    {
        assert(tree.n > 0 && tree.timer == tree.n);
        dfs(tree.rk[1], 0);
    }

    void dfs(int u, int p)
    {
        in[u] = euler.size();
        euler.push_back(u);
        for (int v : tree.g[u])
        {
            if (v == p) continue;
            dfs(v, u);
        }
        out[u] = euler.size();
        euler.push_back(u);
    }

    int add(int u, int v, bool edge = false)
    {
        assert(1 <= u && u <= tree.n && 1 <= v && v <= tree.n);
        if (in[u] > in[v]) swap(u, v);
        int w = tree.lca(u, v);
        int l = w == u ? in[u] : out[u];
        int extra = w == u ? 0 : w;
        if (edge) extra = w == u ? w : 0;
        int id = q.size();
        q.push_back({l, in[v] + 1, extra, id});
        return id;
    }

    template <class Add, class Del, class Ans>
    void run(Add add, Del del, Ans ans, int block = 0) const
    {
        if (q.empty()) return;
        int n = euler.size();
        if (block == 0) block = max(1, int(n / sqrt(double(q.size()))));
        assert(block > 0);
        auto ord = q;
        sort(ord.begin(), ord.end(), [&](const Query &a, const Query &b)
        {
            int x = a.l / block, y = b.l / block;
            if (x != y) return x < y;
            return (x & 1) ? a.r > b.r : a.r < b.r;
        });
        vector<bool> active(tree.n + 1);
        auto toggle = [&](int u)
        {
            if (active[u]) del(u);
            else add(u);
            active[u] = !active[u];
        };
        int l = 0, r = 0;
        for (auto a : ord)
        {
            while (l > a.l) toggle(euler[--l]);
            while (r < a.r) toggle(euler[r++]);
            while (l < a.l) toggle(euler[l++]);
            while (r > a.r) toggle(euler[--r]);
            if (a.extra) toggle(a.extra);
            ans(a.id);
            if (a.extra) toggle(a.extra);
        }
        for (int u = 1; u <= tree.n; u++)
        {
            if (active[u]) del(u);
        }
    }
};
