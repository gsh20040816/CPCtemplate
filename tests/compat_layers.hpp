#pragma once
// Test-only adapters. Issue #21 removed these forwarding layers from the library;
// existing regression tests keep calling the underlying modules through them.
#include "../src/compact/integer_hull.hpp"
#include "../src/compact/integer_plane.hpp"
#include "../src/compact/integer_plane.hpp"
#include "../src/compact/integer_plane.hpp"
#include "../src/compact/integer_plane.hpp"
#include "../src/compact/real_plane.hpp"
#include "../src/compact/real_plane.hpp"
#include "../src/compact/real_plane.hpp"
#include "../src/compact/real_plane.hpp"
#include "../src/compact/real_plane.hpp"
#include "../src/compact/real_plane.hpp"
#include "../src/compact/minkowski_sum.hpp"
#include "../src/compact/space3.hpp"
#include "../src/compact/fps_functions.hpp"
#include "../src/compact/set_convolution.hpp"
#include "../src/compact/recurrence.hpp"
#include "../src/compact/algebra.hpp"
#include "../src/compact/gauss_mod.hpp"
#include "../src/compact/determinant_mod.hpp"
#include "../src/compact/mod_matrix.hpp"
#include "compat_number_theory.hpp"

struct IntegerGeometry : IntegerPlane
{
    static vector<Point> hull(vector<Point> p) { return integer_hull(move(p)); }

    static I area2(const vector<Point> &p) { return polygon_area2(p); }

    static int contains(const vector<Point> &p, Point q)
    {
        return polygon_contains(p, q);
    }

    static int convex_contains(const vector<Point> &p, Point q)
    {
        return convex_contains_i64(p, q);
    }

    static I diameter2(const vector<Point> &p) { return convex_diameter2(p); }
};

struct RealGeometry : RealPlane
{
    R eps;

    RealGeometry(R eps = 1e-12L) : eps(eps) { assert(eps > 0); }

    Point projection(Point p, Point a, Point b) const
    {
        return line_projection(p, a, b);
    }

    R segment_distance(Point p, Point a, Point b) const
    {
        return segment_distance_real(p, a, b);
    }

    Result line_intersection(Point a, Point b, Point c, Point d) const
    {
        return line_intersection_real(a, b, c, d, eps);
    }

    Result line_circle(Point a, Point b, Circle c) const
    {
        return line_circle_intersections(a, b, c, eps);
    }

    Result circles(Circle a, Circle b) const { return circle_intersections(a, b, eps); }

    R overlap(Circle a, Circle b) const { return circle_overlap_area(a, b); }
};

struct GeometryExtra
{
    using G = IntegerGeometry;
    using P = G::Point;
    using I = G::I;

    static vector<P> minkowski(vector<P> a, vector<P> b)
    {
        return minkowski_sum(move(a), move(b));
    }
};

namespace polynomial_detail
{
constexpr auto bm = berlekamp_massey;
constexpr auto nth = recurrence_nth;
} // namespace polynomial_detail

// Compatibility entry; the handbook prints the independently classified modules.
struct Polynomial : FpsFunctions
{
    static void fwt(Poly &a, char op, bool invert = false)
    {
        SetConvolution<mod>::transform(a, op, invert);
    }

    static Poly berlekamp_massey(const Poly &s)
    {
        vector<int> a;
        for (auto x : s) a.push_back(x.v);
        auto c = polynomial_detail::bm(a, mod);
        return Poly(c.begin(), c.end());
    }

    static Z recurrence(Poly init, const Poly &c, unsigned long long n)
    {
        if (n < init.size()) return init[n];
        if (c.empty()) return 0;
        assert(init.size() >= c.size());
        vector<int> a, b;
        for (int i = 0; i < (int)c.size(); i++)
        {
            a.push_back(init[i].v);
            b.push_back(c[i].v);
        }
        return polynomial_detail::nth(a, b, n, mod);
    }
};

template <int mod> struct LinearAlgebra : GaussMod<mod>, ModMatrix<mod>
{
    using Z = ModInt<mod>;
    using Matrix = vector<vector<Z>>;

    static Z determinant(Matrix a)
    {
        vector<vector<long long>> b(a.size());
        for (int i = 0; i < (int)a.size(); i++)
            for (auto x : a[i]) b[i].push_back(x.v);
        return Z(determinant_mod(move(b), mod));
    }

    // Undirected multigraph, vertices 0..n-1; loops ignored.
    static Z spanning_trees(int n, const vector<pair<int, int>> &edges)
    {
        assert(n > 0);
        Matrix lap(n, vector<Z>(n));
        for (auto [u, v] : edges)
            if (u != v)
            {
                lap[u][u] = lap[u][u] + 1;
                lap[v][v] = lap[v][v] + 1;
                lap[u][v] = lap[u][v] - 1;
                lap[v][u] = lap[v][u] - 1;
            }
        lap.pop_back();
        for (auto &row : lap) row.pop_back();
        return determinant(lap);
    }
};
