#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct IntegerGeometry
{
    using ll = long long;
    using I = __int128_t;

    // Contract: |coordinate|<=1e12. Differences/products widened before arithmetic.
    struct Point
    {
        ll x = 0, y = 0;

        bool operator<(Point b) const
        {
            return tie(x, y) < tie(b.x, b.y);
        }

        bool operator==(Point b) const
        {
            return x == b.x && y == b.y;
        }
    };

    static I cross(Point a, Point b, Point c)
    {
        return (I(b.x) - a.x) * (I(c.y) - a.y) - (I(b.y) - a.y) * (I(c.x) - a.x);
    }

    static I dot(Point a, Point b, Point c)
    {
        return (I(b.x) - a.x) * (I(c.x) - a.x) + (I(b.y) - a.y) * (I(c.y) - a.y);
    }

    static I dist2(Point a, Point b)
    {
        return dot(a, b, b);
    }

    static int sign(I x)
    {
        return (x > 0) - (x < 0);
    }

    static bool on_segment(Point p, Point a, Point b)
    {
        return cross(a, b, p) == 0 && dot(p, a, b) <= 0;
    }

    static bool intersect(Point a, Point b, Point c, Point d)
    {
        int x = sign(cross(a, b, c)), y = sign(cross(a, b, d));
        int z = sign(cross(c, d, a)), w = sign(cross(c, d, b));
        if (!x && on_segment(c, a, b))
            return true;
        if (!y && on_segment(d, a, b))
            return true;
        if (!z && on_segment(a, c, d))
            return true;
        if (!w && on_segment(b, c, d))
            return true;
        return x * y < 0 && z * w < 0;
    }

    static vector<Point> hull(vector<Point> p)
    {
        sort(p.begin(), p.end());
        p.erase(unique(p.begin(), p.end()), p.end());
        int n = (int)p.size();
        if (n < 3)
            return p;
        vector<Point> h;
        for (Point v : p)
        {
            while (h.size() > 1 && cross(h[h.size() - 2], h.back(), v) <= 0)
                h.pop_back();
            h.push_back(v);
        }
        int low = (int)h.size();
        for (int i = n - 2; i >= 0; i--)
        {
            while ((int)h.size() > low && cross(h[h.size() - 2], h.back(), p[i]) <= 0)
                h.pop_back();
            h.push_back(p[i]);
        }
        h.pop_back();
        return h; // CCW, no repeated endpoint, no collinear interior points.
    }

    static I area2(const vector<Point> &p)
    {
        I ans = 0;
        int n = (int)p.size();
        for (int i = 0; i < n; i++)
            ans += I(p[i].x) * p[(i + 1) % n].y - I(p[i].y) * p[(i + 1) % n].x;
        return ans;
    }

    // 0 outside, 1 boundary, 2 inside. Simple polygon; either orientation.
    static int contains(const vector<Point> &p, Point q)
    {
        int winding = 0, n = (int)p.size();
        for (int i = 0; i < n; i++)
        {
            Point a = p[i], b = p[(i + 1) % n];
            if (on_segment(q, a, b))
                return 1;
            I c = cross(a, b, q);
            if (a.y <= q.y && b.y > q.y && c > 0)
                ++winding;
            if (a.y > q.y && b.y <= q.y && c < 0)
                --winding;
        }
        return winding ? 2 : 0;
    }

    // Input must be the strict CCW hull above. O(log n).
    static int convex_contains(const vector<Point> &p, Point q)
    {
        int n = (int)p.size();
        if (n < 3)
            return contains(p, q);
        I a = cross(p[0], p[1], q), b = cross(p[0], p[n - 1], q);
        if (a < 0 || b > 0)
            return 0;
        if (!a)
            return on_segment(q, p[0], p[1]) ? 1 : 0;
        if (!b)
            return on_segment(q, p[0], p[n - 1]) ? 1 : 0;
        int l = 1, r = n - 1;
        while (l + 1 < r)
        {
            int m = (l + r) / 2;
            if (cross(p[0], p[m], q) >= 0)
                l = m;
            else
                r = m;
        }
        I c = cross(p[l], p[r], q);
        return c < 0 ? 0 : c == 0 ? 1 : 2;
    }

    static I diameter2(const vector<Point> &p)
    {
        int n = (int)p.size();
        if (n < 2)
            return 0;
        if (n == 2)
            return dist2(p[0], p[1]);
        I ans = 0;
        int j = 1;
        for (int i = 0; i < n; i++)
        {
            int k = (i + 1) % n;
            while (cross(p[i], p[k], p[(j + 1) % n]) > cross(p[i], p[k], p[j]))
                j = (j + 1) % n;
            ans = max({ans, dist2(p[i], p[j]), dist2(p[k], p[j])});
        }
        return ans;
    }

    struct PolarLess
    {
        static int half(Point p)
        {
            return p.y < 0 || (p.y == 0 && p.x < 0);
        }

        bool operator()(Point a, Point b) const
        {
            if (half(a) != half(b))
                return half(a) < half(b);
            I c = cross({0, 0}, a, b);
            if (c)
                return c > 0;
            return dist2({0, 0}, a) < dist2({0, 0}, b);
        }
    };
};

struct RealGeometry
{
    using R = long double;
    // Tolerance is explicit, not used in sorting. Requires finite, well-scaled input.
    R eps;

    RealGeometry(R eps = 1e-12L) : eps(eps)
    {
        assert(eps > 0);
    }

    struct Point
    {
        R x = 0, y = 0;

        Point operator+(Point b) const
        {
            return {x + b.x, y + b.y};
        }

        Point operator-(Point b) const
        {
            return {x - b.x, y - b.y};
        }

        Point operator*(R k) const
        {
            return {x * k, y * k};
        }

        Point operator/(R k) const
        {
            return {x / k, y / k};
        }
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

    static R dot(Point a, Point b)
    {
        return a.x * b.x + a.y * b.y;
    }

    static R cross(Point a, Point b)
    {
        return a.x * b.y - a.y * b.x;
    }

    static R norm(Point a)
    {
        return hypotl(a.x, a.y);
    }

    static Point perp(Point a)
    {
        return {-a.y, a.x};
    }

    Point projection(Point p, Point a, Point b) const
    {
        Point v = b - a;
        R d = dot(v, v);
        if (d == 0)
            return a;
        return a + v * (dot(p - a, v) / d);
    }

    R segment_distance(Point p, Point a, Point b) const
    {
        Point v = b - a;
        R d = dot(v, v);
        if (d == 0)
            return norm(p - a);
        R t = clamp(dot(p - a, v) / d, R(0), R(1));
        return norm(p - (a + v * t));
    }

    Result line_intersection(Point a, Point b, Point c, Point d) const
    {
        Point u = b - a, v = d - c;
        R nu = norm(u), nv = norm(v);
        if (nu == 0 || nv == 0)
            return {Kind::degenerate, {}};
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
        if (len == 0)
            return {Kind::degenerate, {}};
        Point h = projection(c.o, a, b);
        R d = norm(h - c.o), tol = eps * max(d, c.r);
        if (d > c.r + tol)
            return {Kind::none, {}};
        if (fabsl(d - c.r) <= tol)
            return {Kind::one, {h}};
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
            if (a.r != b.r)
                return {Kind::none, {}};
            if (a.r == 0)
                return {Kind::one, {a.o}};
            return {Kind::infinite, {}};
        }
        if (a.r == 0 && b.r == 0)
            return {Kind::none, {}};
        if (a.r == 0 || b.r == 0)
        {
            R radius = max(a.r, b.r);
            if (fabsl(d - radius) > tol)
                return {Kind::none, {}};
            return {Kind::one, {a.r == 0 ? a.o : b.o}};
        }
        if (d > a.r + b.r + tol || d < fabsl(a.r - b.r) - tol)
            return {Kind::none, {}};
        R x = (d * d + (a.r - b.r) * (a.r + b.r)) / (2 * d);
        Point h = a.o + v * (x / d);
        // Near-concentric circles must not be mistaken for internal tangency.
        if (fabsl(x) > a.r + tol)
            return {Kind::none, {}};
        if (fabsl(fabsl(x) - a.r) <= tol)
            return {Kind::one, {h}};
        R y = sqrtl(max(R(0), (a.r - x) * (a.r + x)));
        Point w = perp(v) * (y / d);
        return {Kind::two, {h - w, h + w}};
    }

    R overlap(Circle a, Circle b) const
    {
        assert(a.r >= 0 && b.r >= 0);
        R d = norm(a.o - b.o), pi = acosl(-1.L);
        if (d >= a.r + b.r)
            return 0;
        if (d <= fabsl(a.r - b.r))
            return pi * min(a.r, b.r) * min(a.r, b.r);
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
