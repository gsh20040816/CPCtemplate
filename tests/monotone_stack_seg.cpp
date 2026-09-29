#include "../src/compact/monotone_stack_seg.hpp"
#include <iostream>
#include <random>

using ll = long long;

ll water(const vector<ll> &a)
{
    vector<ll> l = a, r = a;
    for (int i = 1; i < int(a.size()); i++) l[i] = max(l[i], l[i - 1]);
    for (int i = int(a.size()) - 2; i >= 0; i--) r[i] = max(r[i], r[i + 1]);
    ll answer = 0;
    for (int i = 0; i < int(a.size()); i++) answer += min(l[i], r[i]) - a[i];
    return answer;
}

pair<ll, ll> scan(const vector<ll> &a, int l, int r, ll h, bool reverse)
{
    ll answer = 0;
    for (int i = 0; i < r - l; i++)
    {
        ll x = a[reverse ? r - 1 - i : l + i];
        h = max(h, x);
        answer += h - x;
    }
    return {answer, h};
}

void audit(MonotoneStackSeg &s, int p, int l, int r, const vector<ll> &a)
{
    assert(s.t[p].len == r - l);
    ll sum = 0, mx = a[l];
    for (int i = l; i < r; i++)
    {
        sum += a[i];
        mx = max(mx, a[i]);
    }
    assert(s.t[p].sum == sum && s.t[p].mx == mx);
    assert(s.t[p].fill[0] == scan(a, l, r, a[l], false).first);
    assert(s.t[p].fill[1] == scan(a, l, r, a[r - 1], true).first);
    if (r - l == 1) return;
    s.push(p);
    int m = (l + r) / 2;
    audit(s, p * 2, l, m, a);
    audit(s, p * 2 + 1, m, r, a);
}

int main()
{
    for (int n = 1, total = 3; n <= 6; n++, total *= 3)
        for (int code = 0; code < total; code++)
        {
            vector<ll> a(n);
            int v = code;
            for (ll &x : a)
            {
                x = v % 3 - 1;
                v /= 3;
            }
            MonotoneStackSeg s(a);
            assert(s.water() == water(a));
            for (int l = 0; l <= n; l++)
                for (int r = l; r <= n; r++)
                    for (int h = -2; h <= 2; h++)
                        for (bool rev : {false, true})
                            assert(s.scan(l, r, h, rev) == scan(a, l, r, h, rev));
            if (n <= 4)
                for (int l = 0; l <= n; l++)
                    for (int r = l; r <= n; r++)
                        for (int delta : {-3, 0, 3})
                        {
                            s.add(l, r, delta);
                            for (int i = l; i < r; i++) a[i] += delta;
                            assert(s.water() == water(a));
                            audit(s, 1, 0, n, a);
                            s.add(l, r, -delta);
                            for (int i = l; i < r; i++) a[i] -= delta;
                        }
        }
    mt19937 rng(4600125);
    for (int test = 0; test < 1200; test++)
    {
        int n = 1 + rng() % 80;
        vector<ll> a(n);
        for (ll &x : a) x = int(rng() % 101) - 50;
        MonotoneStackSeg s(a);
        for (int op = 0; op < 250; op++)
        {
            int l = rng() % (n + 1), r = rng() % (n + 1);
            if (l > r) swap(l, r);
            ll delta = int(rng() % 101) - 50;
            s.add(l, r, delta);
            for (int i = l; i < r; i++) a[i] += delta;
            assert(s.water() == water(a));
            ll h = int(rng() % 2001) - 1000;
            for (bool rev : {false, true})
                assert(s.scan(l, r, h, rev) == scan(a, l, r, h, rev));
            if (op % 25 == 0) audit(s, 1, 0, n, a);
        }
    }
    int n = 200000;
    vector<ll> a(n, -1000000000000LL);
    a.front() = a.back() = 1000000000000LL;
    MonotoneStackSeg s(a);
    assert(s.water() == 2000000000000LL * (n - 2));
    for (int step = 0; step < 50000; step++)
    {
        s.add(1, n - 1, 1);
        s.add(0, n, -1);
        ll gap = 2000000000000LL - step - 1;
        assert(s.water() == gap * (n - 2));
        assert(s.scan(0, n, a.front() - step - 1).first == gap * (n - 2));
    }
    for (int i = 0; i < n; i++) a[i] = i;
    MonotoneStackSeg increasing(a);
    assert(increasing.water() == 0);
    reverse(a.begin(), a.end());
    MonotoneStackSeg decreasing(a);
    assert(decreasing.water() == 0);
    cout << "MonotoneStackSeg: exhaustive signed arrays, 300000 updates, scans, "
            "invariants, 200000 scale PASS\n";
}
