#pragma once
#include <algorithm>
#include <cassert>
#include <utility>
#include <vector>
using namespace std;

// BEGIN Fenwick2D
template <class T = long long> struct Fenwick2D
{
    using ll = long long;
    int n = 0;
    vector<pair<ll, ll>> pt;
    vector<ll> xs;
    vector<vector<ll>> ys;
    vector<vector<T>> bit;

    Fenwick2D(vector<pair<ll, ll>> p = {})
    {
        init(move(p));
    }

    // Register every future update coordinate; all weights start at zero.
    void init(vector<pair<ll, ll>> p)
    {
        sort(p.begin(), p.end());
        p.erase(unique(p.begin(), p.end()), p.end());
        assert(p.size() < (1U << 30));
        pt = p;
        xs.clear();
        for (auto [x, y] : p)
            if (xs.empty() || xs.back() != x) xs.push_back(x);
        n = xs.size();
        ys.assign(n + 1, {});
        bit.assign(n + 1, {});
        sort(p.begin(), p.end(), [](auto a, auto b)
        {
            return a.second < b.second;
        });
        for (auto [x, y] : p)
        {
            int k = lower_bound(xs.begin(), xs.end(), x) - xs.begin() + 1;
            for (int i = k; i <= n; i += i & -i)
                if (ys[i].empty() || ys[i].back() != y) ys[i].push_back(y);
        }
        for (int i = 1; i <= n; i++) bit[i].assign(ys[i].size() + 1, T{});
    }

    void add(ll x, ll y, T v)
    {
        assert(binary_search(pt.begin(), pt.end(), pair<ll, ll>{x, y}));
        int k = lower_bound(xs.begin(), xs.end(), x) - xs.begin() + 1;
        for (int i = k; i <= n; i += i & -i)
        {
            int j = lower_bound(ys[i].begin(), ys[i].end(), y) - ys[i].begin() + 1;
            for (; j < (int)bit[i].size(); j += j & -j) bit[i][j] += v;
        }
    }

    // Sum over coordinates strictly less than x and y; no endpoint +/-1.
    T prefix(ll x, ll y) const
    {
        T ans{};
        int i = lower_bound(xs.begin(), xs.end(), x) - xs.begin();
        for (; i; i -= i & -i)
        {
            int j = lower_bound(ys[i].begin(), ys[i].end(), y) - ys[i].begin();
            for (; j; j -= j & -j) ans += bit[i][j];
        }
        return ans;
    }

    T sum(ll l, ll d, ll r, ll u) const
    {
        assert(l <= r && d <= u);
        if (l == r || d == u) return T{};
        return prefix(r, u) - prefix(l, u) - prefix(r, d) + prefix(l, d);
    }
};
// END Fenwick2D
