#include "../src/compact/rectangle_union.hpp"
#include <iostream>
#include <random>
using ll = long long;
using Rect = array<ll, 4>;

// Independent weighted-cell oracle: test membership directly, with no sweep or tree.
__int128 cells(const vector<Rect> &rect)
{
    vector<ll> xs, ys;
    for (auto [l, d, r, u] : rect)
    {
        xs.push_back(l);
        xs.push_back(r);
        ys.push_back(d);
        ys.push_back(u);
    }
    sort(xs.begin(), xs.end());
    sort(ys.begin(), ys.end());
    __int128 area = 0;
    for (int i = 1; i < int(xs.size()); ++i)
        for (int j = 1; j < int(ys.size()); ++j)
            for (auto [l, d, r, u] : rect)
                if (l <= xs[i - 1] && xs[i] <= r && d <= ys[j - 1] && ys[j] <= u)
                {
                    area += (__int128)(xs[i] - xs[i - 1]) * (ys[j] - ys[j - 1]);
                    break;
                }
    return area;
}

int main()
{
    const ll m = 1000000000000000000LL;
    vector<ll> points{-m, -m + 1, -m + 19, -m / 100, -7, -1, 0,
                      1, 3, 21, m / 1000, m - 27, m - 1, m};
    mt19937 rng(20261001);
    for (int t = 0; t < 6000; ++t)
    {
        vector<Rect> a;
        for (int n = rng() % 9; n--;)
        {
            ll l = points[rng() % points.size()], r = points[rng() % points.size()];
            ll d = points[rng() % points.size()], u = points[rng() % points.size()];
            if (l > r) swap(l, r);
            if (d > u) swap(d, u);
            a.push_back({l, d, r, u});
        }
        auto expected = cells(a);
        assert(rectangle_union_area(a) == expected);
        for (auto &v : a) swap(v[0], v[1]), swap(v[2], v[3]);
        assert(rectangle_union_area(a) == expected);
    }
    cout << "Rectangle union wide coordinates: 6000 weighted-cell oracles and axis swaps PASS\n";
}
