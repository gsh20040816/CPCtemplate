#pragma once
#include "real_plane.hpp"

// BEGIN polygon_centroid
optional<RealPlane::Point> polygon_centroid(const vector<RealPlane::Point> &p)
{
    using G = RealPlane;
    using R = G::R;
    int n = int(p.size());
    if (n < 3)
        return nullopt;
    array<R, 3> sum{};
    array<R, 3> error{};
    auto add = [&](int i, R v)
    {
        R y = v - error[i];
        R next = sum[i] + y;
        error[i] = (next - sum[i]) - y;
        sum[i] = next;
    };
    for (int i = 1; i + 1 < n; i++)
    {
        auto a = p[i] - p[0];
        auto b = p[i + 1] - p[0];
        R s = G::cross(a, b);
        add(0, s);
        add(1, (a.x + b.x) * s);
        add(2, (a.y + b.y) * s);
    }
    if (sum[0] == 0)
        return nullopt;
    G::Point offset{sum[1] / sum[0] / 3, sum[2] / sum[0] / 3};
    return p[0] + offset;
}
// END polygon_centroid
