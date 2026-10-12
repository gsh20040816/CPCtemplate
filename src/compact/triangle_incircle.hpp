#pragma once
#include "real_plane.hpp"

// BEGIN triangle_incircle
optional<RealPlane::Circle> triangle_incircle(RealPlane::Point a,
                                               RealPlane::Point b,
                                               RealPlane::Point c)
{
    using G = RealPlane;
    using R = G::R;
    auto u = b - a, v = c - a;
    R scale = max({fabsl(u.x), fabsl(u.y), fabsl(v.x), fabsl(v.y)});
    if (scale == 0)
        return nullopt;
    R area = fabsl(G::cross(u, v));
    if (area == 0)
        return nullopt;
    u = u / scale;
    v = v / scale;
    R x = G::norm(v - u), y = G::norm(v), z = G::norm(u);
    R sum = x + y + z;
    auto o = a + (u * (y / sum) + v * (z / sum)) * scale;
    return G::Circle{o, area / scale / sum};
}
// END triangle_incircle
