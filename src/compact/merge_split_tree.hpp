#pragma once
#include <cassert>
#include <climits>
#include <utility>
#include <vector>
using namespace std;

// BEGIN MergeSplitTree
struct MergeSplitTree
{
    using ll = long long;
    struct Node
    {
        int l = 0, r = 0;
        ll sum = 0;
    };

    int n;
    vector<Node> t{Node{}};
    vector<int> root{0}, free;

    MergeSplitTree(int n) : n(n)
    {
        assert(n > 0);
    }

    MergeSplitTree(const vector<ll> &a) : MergeSplitTree((int)a.size())
    {
        root[0] = build(0, n, a);
    }

    int make()
    {
        if (free.empty())
        {
            t.push_back(Node{});
            return (int)t.size() - 1;
        }
        int p = free.back();
        free.pop_back();
        return p;
    }

    void release(int p)
    {
        t[p] = Node{};
        free.push_back(p);
    }

    void pull(int p)
    {
        assert(t[t[p].l].sum <= LLONG_MAX - t[t[p].r].sum);
        t[p].sum = t[t[p].l].sum + t[t[p].r].sum;
    }

    int build(int l, int r, const vector<ll> &a)
    {
        if (r - l == 1)
        {
            assert(a[l] >= 0);
            if (!a[l]) return 0;
            int p = make();
            t[p].sum = a[l];
            return p;
        }
        int m = l + (r - l) / 2;
        int x = build(l, m, a);
        int y = build(m, r, a);
        if (!x && !y) return 0;
        int p = make();
        t[p].l = x;
        t[p].r = y;
        pull(p);
        return p;
    }

    int add_node(int p, int l, int r, int x, ll v)
    {
        if (!p) p = make();
        if (r - l == 1)
        {
            assert(v >= -t[p].sum);
            t[p].sum += v;
        }
        else
        {
            int m = l + (r - l) / 2;
            if (x < m)
            {
                int q = add_node(t[p].l, l, m, x, v);
                t[p].l = q;
            }
            else
            {
                int q = add_node(t[p].r, m, r, x, v);
                t[p].r = q;
            }
            pull(p);
        }
        if (t[p].sum) return p;
        release(p);
        return 0;
    }

    // Sets and coordinates are 0-based; resulting multiplicities are nonnegative.
    void add(int s, int x, ll v)
    {
        assert(0 <= s && s < (int)root.size());
        assert(0 <= x && x < n);
        assert(v <= 0 || t[root[s]].sum <= LLONG_MAX - v);
        if (!v) return;
        root[s] = add_node(root[s], 0, n, x, v);
    }

    int meld(int p, int q, int l, int r)
    {
        if (!p || !q) return p ? p : q;
        if (r - l == 1)
            t[p].sum += t[q].sum;
        else
        {
            int m = l + (r - l) / 2;
            t[p].l = meld(t[p].l, t[q].l, l, m);
            t[p].r = meld(t[p].r, t[q].r, m, r);
            pull(p);
        }
        release(q);
        return p;
    }

    // Consume src; its set ID remains valid and becomes empty.
    void merge(int dst, int src)
    {
        assert(0 <= dst && dst < (int)root.size());
        assert(0 <= src && src < (int)root.size() && dst != src);
        assert(t[root[dst]].sum <= LLONG_MAX - t[root[src]].sum);
        root[dst] = meld(root[dst], root[src], 0, n);
        root[src] = 0;
    }

    pair<int, int> cut(int p, int l, int r, int a, int b)
    {
        if (!p || b <= l || r <= a) return {p, 0};
        if (a <= l && r <= b) return {0, p};
        int m = l + (r - l) / 2;
        auto [x, u] = cut(t[p].l, l, m, a, b);
        auto [y, v] = cut(t[p].r, m, r, a, b);
        t[p].l = x;
        t[p].r = y;
        pull(p);
        if (!t[p].sum)
        {
            release(p);
            p = 0;
        }
        int q = 0;
        if (u || v)
        {
            q = make();
            t[q].l = u;
            t[q].r = v;
            pull(q);
        }
        return {p, q};
    }

    // Move [l,r) into a new set, even when the extracted set is empty.
    int split(int s, int l, int r)
    {
        assert(0 <= s && s < (int)root.size());
        assert(0 <= l && l <= r && r <= n);
        auto [p, q] = cut(root[s], 0, n, l, r);
        root[s] = p;
        root.push_back(q);
        return (int)root.size() - 1;
    }

    ll query(int p, int l, int r, int a, int b) const
    {
        if (!p || b <= l || r <= a) return 0;
        if (a <= l && r <= b) return t[p].sum;
        int m = l + (r - l) / 2;
        return query(t[p].l, l, m, a, b) + query(t[p].r, m, r, a, b);
    }

    ll sum(int s, int l, int r) const
    {
        assert(0 <= s && s < (int)root.size());
        assert(0 <= l && l <= r && r <= n);
        return query(root[s], 0, n, l, r);
    }

    int select(int p, int l, int r, ll k) const
    {
        if (r - l == 1) return l;
        int m = l + (r - l) / 2;
        ll left = t[t[p].l].sum;
        if (k <= left) return select(t[p].l, l, m, k);
        return select(t[p].r, m, r, k - left);
    }

    int kth(int s, ll k) const
    {
        assert(0 <= s && s < (int)root.size());
        if (k <= 0 || k > t[root[s]].sum) return -1;
        return select(root[s], 0, n, k);
    }
};
// END MergeSplitTree
