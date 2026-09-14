#pragma once
#include "integer_plane.hpp"

// BEGIN closest_pair_i64
optional<IntegerPlane::I> closest_pair_i64(vector<IntegerPlane::Point> p)
{
    using G = IntegerPlane;
    using P = G::Point;
    using I = G::I;
    int n = p.size();
    if (n < 2) return nullopt;
    sort(p.begin(), p.end());
    for (int i = 1; i < n; i++)
        if (p[i] == p[i - 1]) return I(0);
    vector<P> tmp(n);
    auto by_y = [](P a, P b)
    {
        return tie(a.y, a.x) < tie(b.y, b.x);
    };
    function<I(int, int)> solve = [&](int l, int r) -> I
    {
        if (r - l <= 3)
        {
            I best = I(1) << 120;
            for (int i = l; i < r; i++)
                for (int j = i + 1; j < r; j++) best = min(best, G::dist2(p[i], p[j]));
            sort(p.begin() + l, p.begin() + r, by_y);
            return best;
        }
        int m = (l + r) / 2;
        long long x = p[m].x;
        I best = min(solve(l, m), solve(m, r));
        merge(p.begin() + l,
              p.begin() + m,
              p.begin() + m,
              p.begin() + r,
              tmp.begin() + l,
              by_y);
        copy(tmp.begin() + l, tmp.begin() + r, p.begin() + l);
        vector<P> strip;
        for (int i = l; i < r; i++)
            if ((I(p[i].x) - x) * (I(p[i].x) - x) < best)
            {
                for (int j = (int)strip.size() - 1; j >= 0; j--)
                {
                    I dy = I(p[i].y) - strip[j].y;
                    if (dy * dy >= best) break;
                    best = min(best, G::dist2(p[i], strip[j]));
                }
                strip.push_back(p[i]);
            }
        return best;
    };
    return solve(0, n);
}

// END closest_pair_i64
