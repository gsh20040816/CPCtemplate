#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

struct DivideSegmentTree
{
    using ll = long long;
    static constexpr ll limit = 1000000000000LL;

    struct Node
    {
        ll sum = 0, low = 0, high = 0;
        ll cover = -1, delta = 0;
    };

    int n;
    vector<Node> t;

    DivideSegmentTree(const vector<ll> &a) : n(a.size()), t(4 * a.size() + 4)
    {
        assert(a.size() <= 500000);
        for (ll x : a)
            assert(0 <= x && x <= limit);
        if (n)
            build(1, 0, n, a);
    }

    void pull(int p)
    {
        t[p].sum = t[p * 2].sum + t[p * 2 + 1].sum;
        t[p].low = min(t[p * 2].low, t[p * 2 + 1].low);
        t[p].high = max(t[p * 2].high, t[p * 2 + 1].high);
    }

    void cover(int p, int len, ll x)
    {
        t[p] = {x * len, x, x, x, 0};
    }

    void shift(int p, int len, ll x)
    {
        t[p].sum += x * len;
        t[p].low += x;
        t[p].high += x;
        if (t[p].cover != -1)
            t[p].cover += x;
        else
            t[p].delta += x;
    }

    void push(int p, int l, int r)
    {
        int m = (l + r) / 2;
        if (t[p].cover != -1)
        {
            cover(p * 2, m - l, t[p].cover);
            cover(p * 2 + 1, r - m, t[p].cover);
            t[p].cover = -1;
        }
        if (t[p].delta)
        {
            shift(p * 2, m - l, t[p].delta);
            shift(p * 2 + 1, r - m, t[p].delta);
            t[p].delta = 0;
        }
    }

    void build(int p, int l, int r, const vector<ll> &a)
    {
        if (r - l == 1)
        {
            cover(p, 1, a[l]);
            return;
        }
        int m = (l + r) / 2;
        build(p * 2, l, m, a);
        build(p * 2 + 1, m, r, a);
        pull(p);
    }

    // kind: 0 = add, 1 = assign, 2 = divide.
    void change(int p, int l, int r, int a, int b, ll x, int kind)
    {
        if (a <= l && r <= b)
        {
            if (kind == 0)
            {
                assert(-t[p].low <= x && x <= limit - t[p].high);
                shift(p, r - l, x);
                return;
            }
            if (kind == 1)
            {
                cover(p, r - l, x);
                return;
            }
            ll low = t[p].low / x, high = t[p].high / x;
            if (low == high)
            {
                cover(p, r - l, low);
                return;
            }
            if (t[p].low - low == t[p].high - high)
            {
                shift(p, r - l, low - t[p].low);
                return;
            }
        }
        push(p, l, r);
        int m = (l + r) / 2;
        if (a < m)
            change(p * 2, l, m, a, b, x, kind);
        if (m < b)
            change(p * 2 + 1, m, r, a, b, x, kind);
        pull(p);
    }

    void update(int l, int r, ll x, int kind)
    {
        assert(0 <= l && l <= r && r <= n);
        if (l < r)
            change(1, 0, n, l, r, x, kind);
    }

    void add(int l, int r, ll x)
    {
        update(l, r, x, 0);
    }

    void assign(int l, int r, ll x)
    {
        assert(0 <= x && x <= limit);
        update(l, r, x, 1);
    }

    void divide(int l, int r, ll x)
    {
        assert(x >= 1);
        update(l, r, x, 2);
    }

    ll query(int p, int l, int r, int a, int b)
    {
        if (a <= l && r <= b)
            return t[p].sum;
        push(p, l, r);
        int m = (l + r) / 2;
        ll result = 0;
        if (a < m)
            result += query(p * 2, l, m, a, b);
        if (m < b)
            result += query(p * 2 + 1, m, r, a, b);
        return result;
    }

    ll sum(int l, int r)
    {
        assert(0 <= l && l <= r && r <= n);
        return l == r ? 0 : query(1, 0, n, l, r);
    }
};
