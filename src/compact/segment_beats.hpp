#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

// 0-based [l,r); empty array/ranges allowed, empty sum = 0. Reconstruct to reset.
// All values, thresholds, pending adds and finite deferred extrema must stay
// strictly inside (-inf,inf), including push's add-before-clip intermediate.
// Each returned sum must fit signed 64-bit. Internal sums use __int128 because
// stale children can temporarily exceed 64-bit before the parent's clip applies.
// LC fits: n,q <= 2e5, actual |a[i]| <= 1e12, update |x| <= 2e12.
// Thus finite deferred extrema/adds stay below (2q+1)*1e12 < inf.
// O(n) build/space, O(log n) sum/add; chmin/chmax may take O(n) once.
// Mixed updates have the standard beats O((n+q) log^2 n) amortized total bound.
struct SegmentBeats
{
    using ll = long long;
    static constexpr ll inf = 1LL << 60;

    struct Node
    {
        __int128 sum = 0;
        ll mx = -inf, mx2 = -inf, mn = inf, mn2 = inf, tag = 0;
        int cmx = 0, cmn = 0;
    };

    int n;
    vector<Node> t;

    SegmentBeats(const vector<ll> &a) : n(a.size()), t(4 * a.size() + 4)
    {
        assert(a.size() <= (INT_MAX - 4) / 4);
        if (n) build(1, 0, n, a);
    }

    void pull(int p)
    {
        auto &u = t[p];
        const auto &a = t[p * 2], &b = t[p * 2 + 1];
        u.sum = a.sum + b.sum;
        u.mx = max(a.mx, b.mx);
        u.mx2 = max(a.mx == u.mx ? a.mx2 : a.mx,
                    b.mx == u.mx ? b.mx2 : b.mx);
        u.cmx = (a.mx == u.mx ? a.cmx : 0) + (b.mx == u.mx ? b.cmx : 0);
        u.mn = min(a.mn, b.mn);
        u.mn2 = min(a.mn == u.mn ? a.mn2 : a.mn,
                    b.mn == u.mn ? b.mn2 : b.mn);
        u.cmn = (a.mn == u.mn ? a.cmn : 0) + (b.mn == u.mn ? b.cmn : 0);
        u.tag = 0;
    }

    void build(int p, int l, int r, const vector<ll> &a)
    {
        if (r - l == 1)
        {
            assert(-inf < a[l] && a[l] < inf);
            t[p].sum = t[p].mx = t[p].mn = a[l];
            t[p].cmx = t[p].cmn = 1;
            return;
        }
        int m = (l + r) / 2;
        build(p * 2, l, m, a);
        build(p * 2 + 1, m, r, a);
        pull(p);
    }

    void apply_add(int p, int len, ll x)
    {
        auto &u = t[p];
        assert(-(__int128)inf < (__int128)u.mn + x &&
               (__int128)u.mx + x < inf);
        assert(-(__int128)inf < (__int128)u.tag + x &&
               (__int128)u.tag + x < inf);
        u.sum += (__int128)x * len;
        u.mx += x;
        u.mn += x;
        if (u.mx2 != -inf) u.mx2 += x;
        if (u.mn2 != inf) u.mn2 += x;
        u.tag += x;
    }

    // Only the maximum changes; equality with mx2 must descend instead.
    void apply_min(int p, ll x)
    {
        auto &u = t[p];
        if (u.mx <= x) return;
        assert(u.mx2 < x);
        u.sum += ((__int128)x - u.mx) * u.cmx;
        if (u.mn == u.mx) u.mn = x;
        else if (u.mn2 == u.mx) u.mn2 = x;
        u.mx = x;
    }

    void apply_max(int p, ll x)
    {
        auto &u = t[p];
        if (u.mn >= x) return;
        assert(x < u.mn2);
        u.sum += ((__int128)x - u.mn) * u.cmn;
        if (u.mx == u.mn) u.mx = x;
        else if (u.mx2 == u.mn) u.mx2 = x;
        u.mn = x;
    }

    void push(int p, int l, int r)
    {
        int m = (l + r) / 2;
        if (t[p].tag)
        {
            apply_add(p * 2, m - l, t[p].tag);
            apply_add(p * 2 + 1, r - m, t[p].tag);
            t[p].tag = 0;
        }
        for (int c : {p * 2, p * 2 + 1})
        {
            apply_min(c, t[p].mx);
            apply_max(c, t[p].mn);
        }
    }

    // type: 0 = chmin, 1 = chmax, 2 = add.
    void update(int p, int l, int r, int ql, int qr, ll x, int type)
    {
        if (qr <= l || r <= ql) return;
        if (type == 0 && t[p].mx <= x) return;
        if (type == 1 && t[p].mn >= x) return;
        if (ql <= l && r <= qr)
        {
            if (type == 0 && t[p].mx2 < x)
            {
                apply_min(p, x);
                return;
            }
            if (type == 1 && x < t[p].mn2)
            {
                apply_max(p, x);
                return;
            }
            if (type == 2)
            {
                apply_add(p, r - l, x);
                return;
            }
        }
        push(p, l, r);
        int m = (l + r) / 2;
        update(p * 2, l, m, ql, qr, x, type);
        update(p * 2 + 1, m, r, ql, qr, x, type);
        pull(p);
    }

    void chmin(int l, int r, ll x)
    {
        assert(0 <= l && l <= r && r <= n && -inf < x && x < inf);
        if (l < r) update(1, 0, n, l, r, x, 0);
    }

    void chmax(int l, int r, ll x)
    {
        assert(0 <= l && l <= r && r <= n && -inf < x && x < inf);
        if (l < r) update(1, 0, n, l, r, x, 1);
    }

    void add(int l, int r, ll x)
    {
        assert(0 <= l && l <= r && r <= n && -inf < x && x < inf);
        if (l < r) update(1, 0, n, l, r, x, 2);
    }

    __int128 query(int p, int l, int r, int ql, int qr)
    {
        if (qr <= l || r <= ql) return 0;
        if (ql <= l && r <= qr) return t[p].sum;
        push(p, l, r);
        int m = (l + r) / 2;
        return query(p * 2, l, m, ql, qr) + query(p * 2 + 1, m, r, ql, qr);
    }

    ll sum(int l, int r)
    {
        assert(0 <= l && l <= r && r <= n);
        __int128 ans = l < r ? query(1, 0, n, l, r) : 0;
        assert(LLONG_MIN <= ans && ans <= LLONG_MAX);
        return (ll)ans;
    }
};
