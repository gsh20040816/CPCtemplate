#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct RealGeometry
{
    using R = long double;
    // Tolerance is explicit, not used in sorting. Requires finite, well-scaled input.
    R eps;

    RealGeometry(R eps = 1e-12L) : eps(eps) { assert(eps > 0); }

    struct Point
    {
        R x = 0, y = 0;

        Point operator+(Point b) const { return {x + b.x, y + b.y}; }

        Point operator-(Point b) const { return {x - b.x, y - b.y}; }

        Point operator*(R k) const { return {x * k, y * k}; }

        Point operator/(R k) const { return {x / k, y / k}; }
    };

    struct Circle
    {
        Point o;
        R r;
    };
    enum class Kind
    {
        none,
        one,
        two,
        infinite,
        degenerate
    };

    struct Result
    {
        Kind kind;
        vector<Point> p;
    };

    static R dot(Point a, Point b) { return a.x * b.x + a.y * b.y; }

    static R cross(Point a, Point b) { return a.x * b.y - a.y * b.x; }

    static R norm(Point a) { return hypotl(a.x, a.y); }

    static Point perp(Point a) { return {-a.y, a.x}; }

    Point projection(Point p, Point a, Point b) const
    {
        Point v = b - a;
        R d = dot(v, v);
        if (d == 0) return a;
        return a + v * (dot(p - a, v) / d);
    }

    R segment_distance(Point p, Point a, Point b) const
    {
        Point v = b - a;
        R d = dot(v, v);
        if (d == 0) return norm(p - a);
        R t = clamp(dot(p - a, v) / d, R(0), R(1));
        return norm(p - (a + v * t));
    }

    Result line_intersection(Point a, Point b, Point c, Point d) const
    {
        Point u = b - a, v = d - c;
        R nu = norm(u), nv = norm(v);
        if (nu == 0 || nv == 0) return {Kind::degenerate, {}};
        R det = cross(u, v);
        if (fabsl(det) <= eps * nu * nv)
            return {fabsl(cross(c - a, u)) <= eps * nu * max(R(1), norm(c - a))
                        ? Kind::infinite
                        : Kind::none,
                    {}};
        return {Kind::one, {a + u * (cross(c - a, v) / det)}};
    }

    Result line_circle(Point a, Point b, Circle c) const
    {
        assert(c.r >= 0);
        Point v = b - a;
        R len = norm(v);
        if (len == 0) return {Kind::degenerate, {}};
        Point h = projection(c.o, a, b);
        R d = norm(h - c.o), tol = eps * max(d, c.r);
        if (d > c.r + tol) return {Kind::none, {}};
        if (fabsl(d - c.r) <= tol) return {Kind::one, {h}};
        R t = sqrtl(max(R(0), (c.r - d) * (c.r + d)));
        Point w = v * (t / len);
        return {Kind::two, {h - w, h + w}};
    }

    Result circles(Circle a, Circle b) const
    {
        assert(a.r >= 0 && b.r >= 0);
        Point v = b.o - a.o;
        R d = norm(v);
        R tol = eps * max({d, a.r, b.r});
        // Infinite intersections require identical positive-radius circles.
        if (d == 0)
        {
            if (a.r != b.r) return {Kind::none, {}};
            if (a.r == 0) return {Kind::one, {a.o}};
            return {Kind::infinite, {}};
        }
        if (a.r == 0 && b.r == 0) return {Kind::none, {}};
        if (a.r == 0 || b.r == 0)
        {
            R radius = max(a.r, b.r);
            if (fabsl(d - radius) > tol) return {Kind::none, {}};
            return {Kind::one, {a.r == 0 ? a.o : b.o}};
        }
        if (d > a.r + b.r + tol || d < fabsl(a.r - b.r) - tol) return {Kind::none, {}};
        R x = (d * d + (a.r - b.r) * (a.r + b.r)) / (2 * d);
        Point h = a.o + v * (x / d);
        // Near-concentric circles must not be mistaken for internal tangency.
        if (fabsl(x) > a.r + tol) return {Kind::none, {}};
        if (fabsl(fabsl(x) - a.r) <= tol) return {Kind::one, {h}};
        R y = sqrtl(max(R(0), (a.r - x) * (a.r + x)));
        Point w = perp(v) * (y / d);
        return {Kind::two, {h - w, h + w}};
    }

    R overlap(Circle a, Circle b) const
    {
        assert(a.r >= 0 && b.r >= 0);
        R d = norm(a.o - b.o), pi = acosl(-1.L);
        if (d >= a.r + b.r) return 0;
        if (d <= fabsl(a.r - b.r)) return pi * min(a.r, b.r) * min(a.r, b.r);
        R difference = (a.r - b.r) * (a.r + b.r);
        R x = acosl(clamp((d * d + difference) / (2 * d * a.r), R(-1), R(1)));
        R y = acosl(clamp((d * d - difference) / (2 * d * b.r), R(-1), R(1)));
        auto segment = [](R angle)
        {
            if (angle < 1e-3L)
            {
                R z = angle * angle;
                return angle * z * (R(2) / 3 + z * (-R(2) / 15 + z * R(4) / 315));
            }
            return angle - sinl(2 * angle) / 2;
        };
        return a.r * a.r * segment(x) + b.r * b.r * segment(y);
    }
};
