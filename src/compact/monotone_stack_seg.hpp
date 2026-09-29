#pragma once
#include <algorithm>
#include <array>
#include <cassert>
#include <utility>
#include <vector>
using namespace std;

struct MonotoneStackSeg
{
    using ll = long long;

    struct Node
    {
        int len = 0;
        ll mx = 0, sum = 0, lazy = 0;
        array<ll, 2> fill{};
    };

    int n;
    vector<Node> t;

    MonotoneStackSeg(const vector<ll> &a) : n(a.size()), t(4 * n)
    {
        assert(n > 0);
        build(1, 0, n, a);
    }

    void apply(int p, ll delta)
    {
        t[p].mx += delta;
        t[p].sum += delta * t[p].len;
        t[p].lazy += delta;
    }

    void push(int p)
    {
        if (!t[p].lazy) return;
        apply(p * 2, t[p].lazy);
        apply(p * 2 + 1, t[p].lazy);
        t[p].lazy = 0;
    }

    ll extra(int p, ll height, int dir)
    {
        if (height >= t[p].mx) return height * t[p].len - t[p].sum;
        if (t[p].len == 1) return 0;
        push(p);
        int first = p * 2 + dir, second = p * 2 + 1 - dir;
        if (height >= t[first].mx)
            return height * t[first].len - t[first].sum + extra(second, height, dir);
        return extra(first, height, dir) + (t[p].fill[dir] - t[first].fill[dir]);
    }

    void pull(int p)
    {
        int l = p * 2, r = l + 1;
        t[p].len = t[l].len + t[r].len;
        t[p].mx = max(t[l].mx, t[r].mx);
        t[p].sum = t[l].sum + t[r].sum;
        t[p].fill[0] = t[l].fill[0] + extra(r, t[l].mx, 0);
        t[p].fill[1] = t[r].fill[1] + extra(l, t[r].mx, 1);
    }

    void build(int p, int l, int r, const vector<ll> &a)
    {
        if (r - l == 1)
        {
            t[p].len = 1;
            t[p].mx = a[l];
            t[p].sum = a[l];
            return;
        }
        int m = (l + r) / 2;
        build(p * 2, l, m, a);
        build(p * 2 + 1, m, r, a);
        pull(p);
    }

    void add(int p, int l, int r, int ql, int qr, ll delta)
    {
        if (ql <= l && r <= qr) return apply(p, delta);
        push(p);
        int m = (l + r) / 2;
        if (ql < m) add(p * 2, l, m, ql, qr, delta);
        if (m < qr) add(p * 2 + 1, m, r, ql, qr, delta);
        pull(p);
    }

    void add(int l, int r, ll delta)
    {
        assert(0 <= l && l <= r && r <= n);
        if (l < r) add(1, 0, n, l, r, delta);
    }

    ll scan(int p, int l, int r, int ql, int qr, ll &height, int dir)
    {
        if (ql <= l && r <= qr)
        {
            ll answer = extra(p, height, dir);
            height = max(height, t[p].mx);
            return answer;
        }
        push(p);
        int m = (l + r) / 2;
        ll answer = 0;
        if (dir && m < qr) answer += scan(p * 2 + 1, m, r, ql, qr, height, dir);
        if (ql < m) answer += scan(p * 2, l, m, ql, qr, height, dir);
        if (!dir && m < qr) answer += scan(p * 2 + 1, m, r, ql, qr, height, dir);
        return answer;
    }

    // Return (sum of running maximum - a[i], final running maximum).
    pair<ll, ll> scan(int l, int r, ll height, bool reverse = false)
    {
        assert(0 <= l && l <= r && r <= n);
        ll answer = 0;
        if (l < r) answer = scan(1, 0, n, l, r, height, reverse);
        return {answer, height};
    }

    ll water() const
    {
        ll gap = t[1].mx * n - t[1].sum;
        return t[1].fill[0] - (gap - t[1].fill[1]);
    }
};
