#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN lazy_segtree
template <class S, class F, auto op, auto e, auto mapping, auto composition, auto id>
struct lazy_segtree
{
    int n;
    vector<S> d;
    vector<F> tag;

    lazy_segtree(int n = 0) : lazy_segtree(vector<S>(n, e())) {}

    lazy_segtree(const vector<S> &a)
        : n(a.size()), d(4 * n + 4, e()), tag(4 * n + 4, id())
    {
        if (n) build(1, 0, n, a);
    }

    void pull(int p) { d[p] = op(d[p * 2], d[p * 2 + 1]); }

    void build(int p, int l, int r, const vector<S> &a)
    {
        if (r - l == 1)
        {
            d[p] = a[l];
            return;
        }
        int m = (l + r) / 2;
        build(p * 2, l, m, a);
        build(p * 2 + 1, m, r, a);
        pull(p);
    }

    void act(int p, F f)
    {
        d[p] = mapping(f, d[p]);
        tag[p] = composition(f, tag[p]);
    }

    void push(int p)
    {
        act(p * 2, tag[p]);
        act(p * 2 + 1, tag[p]);
        tag[p] = id();
    }

    void set(int x, S v)
    {
        assert(0 <= x && x < n);
        put(1, 0, n, x, v);
    }

    void put(int p, int l, int r, int x, S v)
    {
        if (r - l == 1)
        {
            d[p] = v;
            tag[p] = id();
            return;
        }
        push(p);
        int m = (l + r) / 2;
        if (x < m)
            put(p * 2, l, m, x, v);
        else
            put(p * 2 + 1, m, r, x, v);
        pull(p);
    }

    void apply(int l, int r, F f)
    {
        assert(0 <= l && l <= r && r <= n);
        if (l < r) update(1, 0, n, l, r, f);
    }

    void update(int p, int l, int r, int a, int b, F f)
    {
        if (a <= l && r <= b)
        {
            act(p, f);
            return;
        }
        push(p);
        int m = (l + r) / 2;
        if (a < m) update(p * 2, l, m, a, b, f);
        if (m < b) update(p * 2 + 1, m, r, a, b, f);
        pull(p);
    }

    S all() const { return d[1]; }

    S get(int x)
    {
        assert(0 <= x && x < n);
        return prod(x, x + 1);
    }

    S prod(int l, int r)
    {
        assert(0 <= l && l <= r && r <= n);
        return l == r ? e() : query(1, 0, n, l, r);
    }

    S query(int p, int l, int r, int a, int b)
    {
        if (a <= l && r <= b) return d[p];
        push(p);
        int m = (l + r) / 2;
        if (b <= m) return query(p * 2, l, m, a, b);
        if (m <= a) return query(p * 2 + 1, m, r, a, b);
        return op(query(p * 2, l, m, a, b), query(p * 2 + 1, m, r, a, b));
    }

    template <class G> int max_right(int l, G ok)
    {
        assert(0 <= l && l <= n && ok(e()));
        S s = e();
        return l == n ? n : right(1, 0, n, l, s, ok);
    }

    template <class G> int right(int p, int l, int r, int a, S &s, G &ok)
    {
        if (r <= a) return n;
        if (a <= l && ok(op(s, d[p])))
        {
            s = op(s, d[p]);
            return n;
        }
        if (r - l == 1) return l;
        push(p);
        int m = (l + r) / 2;
        int x = right(p * 2, l, m, a, s, ok);
        return x != n ? x : right(p * 2 + 1, m, r, a, s, ok);
    }

    template <class G> int min_left(int r, G ok)
    {
        assert(0 <= r && r <= n && ok(e()));
        S s = e();
        return r == 0 ? 0 : left(1, 0, n, r, s, ok);
    }

    template <class G> int left(int p, int l, int r, int b, S &s, G &ok)
    {
        if (b <= l) return 0;
        if (r <= b && ok(op(d[p], s)))
        {
            s = op(d[p], s);
            return 0;
        }
        if (r - l == 1) return r;
        push(p);
        int m = (l + r) / 2;
        int x = left(p * 2 + 1, m, r, b, s, ok);
        return x != 0 ? x : left(p * 2, l, m, b, s, ok);
    }
};

// END lazy_segtree
