#pragma once
#include "hull3d.hpp"

// BEGIN Hull3DMetrics
// Integer coordinates |x|, |y|, |z| <= 1e9. Keep h alive and unchanged.
struct Hull3DMetrics
{
    using Hull = Hull3D<long long>;
    using Point = Hull::Point;
    const Hull &h;
    vector<__int128> mass;
    __int128 total = 0;

    explicit Hull3DMetrics(const Hull &h) : h(h), mass(h.p.size())
    {
        if (h.dimension != 3) return;
        for (auto f : h.faces)
        {
            __int128 v = Hull::orient(h.p[0], h.p[f[0]], h.p[f[1]], h.p[f[2]]);
            mass[0] += v;
            for (int u : f) mass[u] += v;
            total += 4 * v;
        }
    }
    // Uniform volume centroid; absent for dimension < 3.
    optional<array<long double, 3>> centroid() const
    {
        if (total == 0) return nullopt;
        array<long long, 3> base{h.p[0].x, h.p[0].y, h.p[0].z};
        for (Point p : h.p)
        {
            base[0] = min(base[0], p.x);
            base[1] = min(base[1], p.y);
            base[2] = min(base[2], p.z);
        }
        array<long double, 3> result{};
        for (int i = 0; i < int(h.p.size()); i++)
        {
            array<long long, 3> p{h.p[i].x, h.p[i].y, h.p[i].z};
            for (int k = 0; k < 3; k++)
                result[k] += (long double)mass[i] * (p[k] - base[k]);
        }
        for (int k = 0; k < 3; k++) result[k] = base[k] + result[k] / total;
        return result;
    }
    long double normal_length(int face) const
    {
        auto f = h.faces[face];
        auto v = Hull::normal(h.p[f[0]], h.p[f[1]], h.p[f[2]]);
        return hypotl(hypotl((long double)v[0], (long double)v[1]),
                      (long double)v[2]);
    }
    // Distance to the infinite plane, NOT to the bounded triangle.
    long double plane_distance(Point p, int face) const
    {
        auto f = h.faces[face];
        auto v = Hull::orient(h.p[f[0]], h.p[f[1]], h.p[f[2]], p);
        return fabsl((long double)v) / normal_length(face);
    }
    // Distance from the volume centroid to the surface; O(n * faces).
    optional<long double> clearance() const
    {
        if (total == 0) return nullopt;
        long double answer = numeric_limits<long double>::infinity();
        for (int i = 0; i < int(h.faces.size()); i++)
        {
            auto f = h.faces[i];
            long double sum = 0;
            for (int j = 0; j < int(h.p.size()); j++)
            {
                auto d = -Hull::orient(h.p[f[0]], h.p[f[1]], h.p[f[2]], h.p[j]);
                sum += (long double)mass[j] * (long double)d;
            }
            answer = min(answer, sum / total / normal_length(i));
        }
        return answer;
    }
    // One representative triangle per geometric plane; O(faces^2).
    vector<int> planes() const
    {
        vector<int> result;
        for (int i = 0; i < int(h.faces.size()); i++)
        {
            bool found = false;
            for (int j : result)
            {
                auto f = h.faces[j];
                bool same = true;
                for (int u : h.faces[i])
                    if (Hull::orient(h.p[f[0]], h.p[f[1]], h.p[f[2]], h.p[u]) != 0)
                        same = false;
                if (same)
                {
                    found = true;
                    break;
                }
            }
            if (!found) result.push_back(i);
        }
        return result;
    }
};
// END Hull3DMetrics
