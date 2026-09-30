#include <iostream>
#include <random>
#include <set>
#include "../src/compact/rectangle_union.hpp"
using ll = long long;
using Rect = array<ll, 4>;

ll grid(const vector<Rect> &a)
{
    set<pair<ll, ll>> cells;
    for (auto [l, d, r, u] : a)
        for (ll x = l; x < r; ++x)
            for (ll y = d; y < u; ++y) cells.insert({x, y});
    return cells.size();
}

int main()
{
    vector<Rect> all;
    for (int l = -1; l <= 1; ++l)
        for (int r = l; r <= 1; ++r)
            for (int d = -1; d <= 1; ++d)
                for (int u = d; u <= 1; ++u) all.push_back({l, d, r, u});
    assert(rectangle_union_area({}) == 0);
    for (auto a : all) for (auto b : all) for (auto c : all)
    {
        vector<Rect> v{a, b, c};
        assert(rectangle_union_area(v) == grid(v));
    }
    mt19937 rng(63293835);
    for (int t = 0; t < 4000; ++t)
    {
        vector<Rect> a;
        int n = rng() % 16;
        for (int i = 0; i < n; ++i)
        {
            ll l = int(rng() % 13) - 6, r = int(rng() % 13) - 6;
            ll d = int(rng() % 13) - 6, u = int(rng() % 13) - 6;
            if (l > r) swap(l, r);
            if (d > u) swap(d, u);
            a.push_back({l, d, r, u});
        }
        auto original = a;
        auto expected = grid(a);
        assert(rectangle_union_area(a) == expected);
        assert(a == original);
        shuffle(a.begin(), a.end(), rng);
        assert(rectangle_union_area(a) == expected);
        for (auto &r : a) for (auto &x : r) x += 999999999999999000LL;
        assert(rectangle_union_area(a) == expected);
    }
    ll m = 1000000000000000000LL;
    assert(rectangle_union_area({{-m, -m, m, m}}) == (__int128)4 * m * m);
    assert(rectangle_union_area({{-m, -m, 0, m}, {0, -m, m, m}}) == (__int128)4 * m * m);
    const int n = 500000;
    vector<Rect> a;
    for (int i = 0; i < n; ++i) a.push_back({2LL*i, 2LL*i, 2LL*i+1, 2LL*i+1});
    assert(rectangle_union_area(a) == n);
    for (int i = 0; i < n; ++i) a[i] = {i, i, 1000000000LL-i, 1000000000LL-i};
    assert(rectangle_union_area(a) == 1000000000000000000LL);
    fill(a.begin(), a.end(), Rect{0, 0, 1000000000LL, 1000000000LL});
    assert(rectangle_union_area(a) == 1000000000000000000LL);
    cout << "Rectangle union: 46656 exhaustive triples, 4000 grid oracles with permutations/translations, int128 extremes and three n=500000 families PASS\n";
}
