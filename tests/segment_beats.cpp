#include "../src/compact/segment_beats.hpp"
#include <iostream>
#include <numeric>
#include <random>
using ll = long long;

void invariant(SegmentBeats &t, const vector<ll> &a, int p, int l, int r)
{
    vector<ll> values(a.begin() + l, a.begin() + r);
    sort(values.begin(), values.end());
    auto &u = t.t[p];
    assert(u.mn == values.front() && u.mx == values.back());
    assert(u.cmn == count(values.begin(), values.end(), u.mn));
    assert(u.cmx == count(values.begin(), values.end(), u.mx));
    assert(u.sum == accumulate(values.begin(), values.end(), (__int128)0));
    values.erase(unique(values.begin(), values.end()), values.end());
    assert(u.mn2 == (values.size() == 1 ? SegmentBeats::inf : values[1]));
    assert(u.mx2 == (values.size() == 1 ? -SegmentBeats::inf
                                      : values[values.size() - 2]));
    if (r - l == 1) return;
    t.push(p, l, r);
    int m = (l + r) / 2;
    invariant(t, a, p * 2, l, m);
    invariant(t, a, p * 2 + 1, m, r);
}

void check(SegmentBeats &t, const vector<ll> &a, bool all)
{
    int n = a.size();
    if (n) invariant(t, a, 1, 0, n);
    assert(t.sum(0, n) == accumulate(a.begin(), a.end(), 0LL));
    for (int i = 0; i < n; i++) assert(t.sum(i, i + 1) == a[i]);
    if (all)
    {
        for (int l = 0; l <= n; l++)
        {
            ll sum = 0;
            for (int r = l; r <= n; r++)
            {
                assert(t.sum(l, r) == sum);
                if (r < n) sum += a[r];
            }
        }
    }
}

void change(SegmentBeats &t, vector<ll> &a, int type, int l, int r, ll x)
{
    if (type == 0) t.chmin(l, r, x);
    else if (type == 1) t.chmax(l, r, x);
    else t.add(l, r, x);
    for (int i = l; i < r; i++)
    {
        if (type == 0) a[i] = min(a[i], x);
        else if (type == 1) a[i] = max(a[i], x);
        else a[i] += x;
    }
}

int main()
{
    mt19937_64 rng(2026093003);
    // All tiny ternary arrays and threshold equalities, with overlapping adds.
    for (int n = 0; n <= 6; n++)
    {
        int count = 1;
        for (int i = 0; i < n; i++) count *= 3;
        for (int mask = 0; mask < count; mask++)
        {
            vector<ll> base(n);
            int code = mask;
            for (auto &x : base)
            {
                x = code % 3 - 1;
                code /= 3;
            }
            for (int type = 0; type < 3; type++)
                for (int x = -2; x <= 2; x++)
                {
                    auto a = base;
                    SegmentBeats t(a);
                    change(t, a, type, 0, n, x);
                    change(t, a, 2, n / 3, n, 3);
                    change(t, a, 1, 0, n * 2 / 3, 2);
                    change(t, a, 0, n / 2, n, 2);
                    check(t, a, true);
                }
        }
    }
    for (int trial = 0; trial < 500; trial++)
    {
        int n = rng() % 100 + 1;
        vector<ll> a(n);
        for (int i = 0; i < n; i++)
        {
            if (trial % 3 == 0) a[i] = 7;
            else if (trial % 3 == 1) a[i] = i % 2 * 14 - 7;
            else a[i] = (ll)(rng() % 101) - 50;
        }
        SegmentBeats t(a);
        for (int step = 0; step < 600; step++)
        {
            int l = rng() % (n + 1), r = rng() % (n + 1);
            if (l > r) swap(l, r);
            if (step % 5 == 0) l = 0, r = n;
            int type = rng() % 3;
            ll x = step % 4 == 0 ? a[rng() % n] : (ll)(rng() % 201) - 100;
            change(t, a, type, l, r, x);
            // Preserve deferred state for many updates before forcing leaves.
            if (step % 41 == 0) check(t, a, false);
            int ql = rng() % (n + 1), qr = rng() % (n + 1);
            if (ql > qr) swap(ql, qr);
            assert(t.sum(ql, qr) == accumulate(a.begin() + ql, a.begin() + qr, 0LL));
        }
        check(t, a, true);
    }
    // Sentinel-adjacent finite values, absent second extrema must not move.
    for (ll sign : {-1LL, 1LL})
    {
        vector<ll> a(4, sign * (SegmentBeats::inf - 100));
        SegmentBeats t(a);
        change(t, a, 2, 0, 4, -sign * 20);
        change(t, a, 0, 1, 3, sign * (SegmentBeats::inf - 150));
        change(t, a, 1, 0, 2, sign * (SegmentBeats::inf - 160));
        check(t, a, true);
    }
    // Public results can reach both signed-64 endpoints with finite values.
    vector<ll> high(8, SegmentBeats::inf - 1), low(8, -SegmentBeats::inf + 1);
    high.push_back(7);
    low.push_back(-8);
    SegmentBeats hi(high), lo(low);
    assert(hi.sum(0, 9) == LLONG_MAX);
    assert(lo.sum(0, 9) == LLONG_MIN);
    check(hi, high, true);
    check(lo, low, true);
    // Actual values always <= 1e12; stale push sums exceed signed 64-bit.
    int n = 200000;
    for (ll sign : {-1LL, 1LL})
    {
        SegmentBeats t(vector<ll>(n, 0));
        for (int step = 0; step < 99999; step++)
        {
            t.add(0, n, sign * 1000000000000LL);
            if (sign > 0) t.chmin(0, n, 0);
            else t.chmax(0, n, 0);
        }
        assert(t.sum(1, n - 1) == 0);
        assert(t.sum(n / 2, n / 2 + 1) == 0);
    }
    cout << "SegmentBeats PASS: exhaustive ternary arrays, 300000 random updates, "
            "sentinel-adjacent values, 2 maximum deferred-add stress cases\n";
}
