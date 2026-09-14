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

        bool operator<(Point b) const { return tie(x, y) < tie(b.x, b.y); }

        bool operator==(Point b) const { return x == b.x && y == b.y; }
    };

    static I cross(Point a, Point b, Point c)
    {
        return (I(b.x) - a.x) * (I(c.y) - a.y) - (I(b.y) - a.y) * (I(c.x) - a.x);
    }

    static I dot(Point a, Point b, Point c)
    {
        return (I(b.x) - a.x) * (I(c.x) - a.x) + (I(b.y) - a.y) * (I(c.y) - a.y);
    }

    static I dist2(Point a, Point b) { return dot(a, b, b); }

    static int sign(I x) { return (x > 0) - (x < 0); }

    static bool on_segment(Point p, Point a, Point b)
    {
        return cross(a, b, p) == 0 && dot(p, a, b) <= 0;
    }

    static bool intersect(Point a, Point b, Point c, Point d)
    {
        int x = sign(cross(a, b, c)), y = sign(cross(a, b, d));
        int z = sign(cross(c, d, a)), w = sign(cross(c, d, b));
        if (!x && on_segment(c, a, b)) return true;
        if (!y && on_segment(d, a, b)) return true;
        if (!z && on_segment(a, c, d)) return true;
        if (!w && on_segment(b, c, d)) return true;
        return x * y < 0 && z * w < 0;
    }

    static vector<Point> hull(vector<Point> p)
    {
        sort(p.begin(), p.end());
        p.erase(unique(p.begin(), p.end()), p.end());
        int n = (int)p.size();
        if (n < 3) return p;
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
            if (on_segment(q, a, b)) return 1;
            I c = cross(a, b, q);
            if (a.y <= q.y && b.y > q.y && c > 0) ++winding;
            if (a.y > q.y && b.y <= q.y && c < 0) --winding;
        }
        return winding ? 2 : 0;
    }

    // Input must be the strict CCW hull above. O(log n).
    static int convex_contains(const vector<Point> &p, Point q)
    {
        int n = (int)p.size();
        if (n < 3) return contains(p, q);
        I a = cross(p[0], p[1], q), b = cross(p[0], p[n - 1], q);
        if (a < 0 || b > 0) return 0;
        if (!a) return on_segment(q, p[0], p[1]) ? 1 : 0;
        if (!b) return on_segment(q, p[0], p[n - 1]) ? 1 : 0;
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
        if (n < 2) return 0;
        if (n == 2) return dist2(p[0], p[1]);
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
        static int half(Point p) { return p.y < 0 || (p.y == 0 && p.x < 0); }

        bool operator()(Point a, Point b) const
        {
            if (half(a) != half(b)) return half(a) < half(b);
            I c = cross({0, 0}, a, b);
            if (c) return c > 0;
            return dist2({0, 0}, a) < dist2({0, 0}, b);
        }
    };
};
