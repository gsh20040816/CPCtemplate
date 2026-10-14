#include "../src/compact/odt.hpp"
#include <iostream>
#include <random>

// CF896C operations on ODT versus a plain array.
using ll = long long;
mt19937_64 rng(896);

ll power(ll a, ll e, ll m)
{
    ll r = 1 % m;
    for (a %= m; e; e >>= 1, a = a * a % m)
        if (e & 1) r = r * a % m;
    return r;
}

int main()
{
    long long checks = 0;
    for (int it = 0; it < 3000; it++)
    {
        int lo = (int)(rng() % 5) - 2, n = 1 + rng() % 40;
        int hi = lo + n;
        ll init = rng() % 10;
        ODT<ll> t(lo, hi, init);
        vector<ll> a(n, init);
        for (int op = 0; op < 60; op++)
        {
            int l = lo + rng() % n, r = lo + rng() % n;
            if (l > r) swap(l, r);
            r++; // [l, r) non-empty
            if (rng() % 10 == 0) r = l; // empty range
            int kind = rng() % 4;
            if (kind == 0)
            {
                ll x = rng() % 7;
                t.each(l, r, [&](ll, ll, ll &v) { v += x; });
                for (int i = l; i < r; i++) a[i - lo] += x;
            }
            else if (kind == 1)
            {
                ll v = rng() % 7;
                t.assign(l, r, v);
                for (int i = l; i < r; i++) a[i - lo] = v;
            }
            else if (kind == 2 && l < r)
            {
                vector<pair<ll, ll>> segs;
                t.each(l, r, [&](ll x, ll y, ll &v) { segs.push_back({v, y - x}); });
                sort(segs.begin(), segs.end());
                vector<ll> b(a.begin() + (l - lo), a.begin() + (r - lo));
                sort(b.begin(), b.end());
                ll k = 1 + rng() % (r - l), left = k;
                ll got = -1;
                for (auto [v, len] : segs)
                    if ((left -= len) <= 0)
                    {
                        got = v;
                        break;
                    }
                assert(got == b[k - 1]);
            }
            else if (kind == 3)
            {
                ll x = rng() % 5, m = 1 + rng() % 1000, s = 0, want = 0;
                t.each(l, r, [&](ll a0, ll b0, ll &v) { s = (s + (b0 - a0) % m * power(v, x, m)) % m; });
                for (int i = l; i < r; i++) want = (want + power(a[i - lo], x, m)) % m;
                assert(s == want);
            }
            // structure: keys strictly increase, cover [lo, hi], and expand back to the array
            assert(t.mp.begin()->first == lo && prev(t.mp.end())->first == hi);
            vector<ll> c;
            for (auto p = t.mp.begin(); next(p) != t.mp.end(); ++p)
                for (ll i = p->first; i < next(p)->first; i++) c.push_back(p->second);
            assert(c == a);
            checks++;
        }
    }
    // assignments keep the segment count small
    ODT<int> t(0, 1000000, 0);
    for (int i = 0; i < 1000; i++) t.assign(i * 1000, i * 1000 + 500, i);
    t.assign(0, 1000000, 7);
    assert(t.mp.size() == 2);
    cout << "ODT: add, assign, k-th and power-sum queries vs array on 3000 random runs, "
            "empty ranges and segment merging PASS (" << checks << " checks)\n";
}
