#pragma once
#include "integer_plane.hpp"

// BEGIN closest_pair_i64
optional<IntegerPlane::I> closest_pair_i64(const vector<IntegerPlane::Point> &p,
                                           pair<int, int> *endpoints = nullptr)
{
    using G = IntegerPlane;
    using I = G::I;
    int n = p.size();
    if (endpoints) *endpoints = {-1, -1};
    if (n < 2) return nullopt;
    vector<int> id(n), tmp(n);
    iota(id.begin(), id.end(), 0);
    sort(id.begin(), id.end(), [&](int a, int b) { return p[a] < p[b]; });
    for (int i = 1; i < n; i++)
        if (p[id[i]] == p[id[i - 1]])
        {
            if (endpoints) *endpoints = {id[i - 1], id[i]};
            return I(0);
        }
    I ans = I(1) << 120;
    auto distance = [&](int a, int b)
    {
        I d = G::dist2(p[a], p[b]);
        if (d < ans)
        {
            ans = d;
            if (endpoints) *endpoints = {a, b};
        }
        return d;
    };
    auto by_y = [&](int a, int b)
    {
        return tie(p[a].y, p[a].x) < tie(p[b].y, p[b].x);
    };
    function<I(int, int)> solve = [&](int l, int r) -> I
    {
        if (r - l <= 3)
        {
            I best = I(1) << 120;
            for (int i = l; i < r; i++)
                for (int j = i + 1; j < r; j++)
                    best = min(best, distance(id[i], id[j]));
            sort(id.begin() + l, id.begin() + r, by_y);
            return best;
        }
        int m = (l + r) / 2;
        long long x = p[id[m]].x;
        I best = min(solve(l, m), solve(m, r));
        merge(id.begin() + l,
              id.begin() + m,
              id.begin() + m,
              id.begin() + r,
              tmp.begin() + l,
              by_y);
        copy(tmp.begin() + l, tmp.begin() + r, id.begin() + l);
        vector<int> strip;
        for (int i = l; i < r; i++)
            if ((I(p[id[i]].x) - x) * (I(p[id[i]].x) - x) < best)
            {
                for (int j = (int)strip.size() - 1; j >= 0; j--)
                {
                    I dy = I(p[id[i]].y) - p[strip[j]].y;
                    if (dy * dy >= best) break;
                    best = min(best, distance(id[i], strip[j]));
                }
                strip.push_back(id[i]);
            }
        return best;
    };
    return solve(0, n);
}

// END closest_pair_i64
