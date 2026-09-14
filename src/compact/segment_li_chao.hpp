#pragma once
#include <algorithm>
#include <cassert>
#include <utility>
#include <vector>
using namespace std;

struct SegmentLiChao
{
    using ll = long long;
    using I = __int128_t;

    struct Line
    {
        ll x1, y1, x2, y2;
    };

    vector<ll> xs;
    vector<Line> lines{{0, 0, 0, 0}};
    vector<int> t;

    SegmentLiChao(vector<ll> x) : xs(move(x))
    {
        sort(xs.begin(), xs.end());
        xs.erase(unique(xs.begin(), xs.end()), xs.end());
        assert(!xs.empty() && xs.front() >= -1000000000 && xs.back() <= 1000000000);
        t.resize(4 * xs.size());
    }

    pair<I, I> value(int id, ll x) const
    {
        auto [a, b, c, d] = lines[id];
        if (a == c) return {max(b, d), 1};
        return {I(b) * (c - x) + I(d) * (x - a), c - a};
    }

    bool better(int u, int v, ll x) const
    {
        if (!u || !v) return u != 0;
        auto [a, b] = value(u, x);
        auto [c, d] = value(v, x);
        return a * d == c * b ? u < v : a * d > c * b;
    }

    void insert(int p, int l, int r, int ql, int qr, int id)
    {
        int m = (l + r) / 2;
        if (ql <= l && r <= qr)
        {
            if (better(id, t[p], xs[m])) swap(id, t[p]);
            if (!id || l == r) return;
            if (better(id, t[p], xs[l]))
                insert(p * 2, l, m, l, m, id);
            else if (better(id, t[p], xs[r]))
                insert(p * 2 + 1, m + 1, r, m + 1, r, id);
            return;
        }
        if (ql <= m) insert(p * 2, l, m, ql, qr, id);
        if (qr > m) insert(p * 2 + 1, m + 1, r, ql, qr, id);
    }

    int add(ll x1, ll y1, ll x2, ll y2)
    {
        assert(-1000000000 <= x1 && x1 <= 1000000000);
        assert(-1000000000 <= x2 && x2 <= 1000000000);
        assert(-2000000000000000000LL <= y1 && y1 <= 2000000000000000000LL);
        assert(-2000000000000000000LL <= y2 && y2 <= 2000000000000000000LL);
        if (x1 > x2)
        {
            swap(x1, x2);
            swap(y1, y2);
        }
        int id = lines.size();
        lines.push_back({x1, y1, x2, y2});
        int l = lower_bound(xs.begin(), xs.end(), x1) - xs.begin();
        int r = upper_bound(xs.begin(), xs.end(), x2) - xs.begin() - 1;
        if (l <= r) insert(1, 0, (int)xs.size() - 1, l, r, id);
        return id;
    }

    int query(ll x) const
    {
        int i = lower_bound(xs.begin(), xs.end(), x) - xs.begin();
        assert(i < (int)xs.size() && xs[i] == x);
        int p = 1, l = 0, r = (int)xs.size() - 1, ans = 0;
        while (true)
        {
            if (better(t[p], ans, x)) ans = t[p];
            if (l == r) return ans;
            int m = (l + r) / 2;
            if (i <= m)
            {
                p *= 2;
                r = m;
            }
            else
            {
                p = p * 2 + 1;
                l = m + 1;
            }
        }
    }
};
