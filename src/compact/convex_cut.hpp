#pragma once
#include "real_plane.hpp"

// BEGIN convex_cut
vector<RealPlane::Point> convex_cut(const vector<RealPlane::Point> &p,
    RealPlane::Point a, RealPlane::Point b)
{
    using G = RealPlane;
    assert(a.x != b.x || a.y != b.y);
    int n = int(p.size());
    vector<G::Point> q;
    auto e = b - a;
    for (int i = 0; i < n; i++)
    {
        auto u = p[i];
        auto v = p[(i + 1) % n];
        auto s = G::cross(e, u - a);
        auto t = G::cross(e, v - a);
        if (s >= 0)
            q.push_back(u);
        if ((s < 0 && t > 0) || (s > 0 && t < 0))
            q.push_back(u + (v - u) * (s / (s - t)));
    }
    return q;
}
// END convex_cut
