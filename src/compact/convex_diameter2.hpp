#pragma once
#include "integer_plane.hpp"

// BEGIN convex_diameter2
IntegerPlane::I convex_diameter2(const vector<IntegerPlane::Point> &p)
{
    using G = IntegerPlane;
    using I = G::I;
    int n = (int)p.size();
    if (n < 2) return 0;
    if (n == 2) return G::dist2(p[0], p[1]);
    I ans = 0;
    int j = 1;
    for (int i = 0; i < n; i++)
    {
        int k = (i + 1) % n;
        while (G::cross(p[i], p[k], p[(j + 1) % n]) > G::cross(p[i], p[k], p[j]))
            j = (j + 1) % n;
        ans = max({ans, G::dist2(p[i], p[j]), G::dist2(p[k], p[j])});
    }
    return ans;
}

// END convex_diameter2
