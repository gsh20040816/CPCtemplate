#include <bits/stdc++.h>
#include "../src/compact/wavelet_matrix.hpp"
using namespace std;

using ll = long long;
mt19937_64 rng(20260929);
long long queries = 0;

void check(const vector<ll> &a, bool exhaustive)
{
    vector<ll> saved = a;
    WaveletMatrix wm(a);
    assert(a == saved);
    int n = a.size();
    auto interval = [&](int l, int r)
    {
        vector<ll> s(a.begin() + l, a.begin() + r);
        sort(s.begin(), s.end());
        vector<ll> xs = {LLONG_MIN, LLONG_MAX, -4, -1, 0, 1, 4};
        for (ll x : s)
        {
            xs.push_back(x);
            if (x != LLONG_MIN) xs.push_back(x - 1);
            if (x != LLONG_MAX) xs.push_back(x + 1);
        }
        for (ll x : xs)
        {
            assert(wm.less(l, r, x) ==
                   count_if(s.begin(), s.end(), [&](ll y) { return y < x; }));
            assert(wm.freq(l, r, x) == count(s.begin(), s.end(), x));
            queries += 2;
        }
        for (int k = 0; k < r - l; k++)
        {
            assert(wm.kth(l, r, k) == s[k]);
            queries++;
        }
    };
    if (exhaustive)
    {
        for (int l = 0; l <= n; l++)
            for (int r = l; r <= n; r++) interval(l, r);
    }
    else
    {
        interval(0, n);
        for (int t = 0; t < 30; t++)
        {
            int l = rng() % (n + 1), r = rng() % (n + 1);
            if (l > r) swap(l, r);
            interval(l, r);
        }
    }
    for (int d = 0; d < wm.h; d++)
    {
        int cnt = 0;
        for (int i = 0; i <= n; i++)
        {
            assert(wm.rank(d, i) == cnt);
            if (i < n) cnt += wm.bit[d][i / 64] >> (i % 64) & 1;
        }
    }
}

int main()
{
    int exhaustive = 0;
    for (int n = 0, pow3 = 1; n <= 7; n++, pow3 *= 3)
        for (int mask = 0; mask < pow3; mask++)
        {
            vector<ll> a(n);
            int x = mask;
            for (ll &v : a)
            {
                v = x % 3 - 1;
                x /= 3;
            }
            check(a, true);
            exhaustive++;
        }
    for (int t = 0; t < 600; t++)
    {
        vector<ll> a(rng() % 100);
        for (ll &x : a)
        {
            if (t % 3 == 0)
                x = (ll)(rng() % 9) - 4;
            else if (t % 3 == 1)
                x = rng() & 1 ? LLONG_MIN : LLONG_MAX;
            else
                x = bit_cast<ll>(rng());
        }
        check(a, false);
    }
    for (int n : {63, 64, 65, 127, 128, 129, 255, 256, 257})
    {
        vector<ll> a(n);
        iota(a.begin(), a.end(), -100);
        check(a, false);
        reverse(a.begin(), a.end());
        check(a, false);
        shuffle(a.begin(), a.end(), rng);
        check(a, false);
    }
    const int n = 500000;
    vector<ll> a(n);
    iota(a.begin(), a.end(), -250000);
    for (int mode = 0; mode < 3; mode++)
    {
        if (mode == 1) reverse(a.begin(), a.end());
        if (mode == 2) fill(a.begin(), a.end(), LLONG_MAX);
        WaveletMatrix wm(a);
        for (int t = 0; t < n; t++)
        {
            int l = rng() % n, r = l + 1 + rng() % (n - l);
            int k = rng() % (r - l);
            ll expected = mode == 0 ? a[l + k] : mode == 1 ? a[r - 1 - k] : LLONG_MAX;
            assert(wm.kth(l, r, k) == expected);
            assert(wm.freq(l, r, expected) == (mode == 2 ? r - l : 1));
            assert(wm.less(l, r, expected) == (mode == 2 ? 0 : k));
            queries += 3;
        }
        size_t bytes = wm.val.capacity() * sizeof(ll) + wm.mid.capacity() * sizeof(int);
        for (auto &v : wm.bit) bytes += v.capacity() * sizeof(unsigned long long);
        for (auto &v : wm.sum) bytes += v.capacity() * sizeof(int);
        assert(bytes <= 6000000);
    }
    cout << "WaveletMatrix PASS: " << exhaustive
         << " exhaustive arrays; 600 random; 27 word-boundary arrays; 3 x 500000 scale "
            "queries; "
         << queries << " API checks\n";
}
