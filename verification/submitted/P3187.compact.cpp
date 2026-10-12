#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct IntegerPlane
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


// BEGIN integer_hull
vector<IntegerPlane::Point> integer_hull(vector<IntegerPlane::Point> p)
{
    using G = IntegerPlane;
    using Point = G::Point;
    sort(p.begin(), p.end());
    p.erase(unique(p.begin(), p.end()), p.end());
    int n = (int)p.size();
    if (n < 3) return p;
    vector<Point> h;
    for (Point v : p)
    {
        while (h.size() > 1 && G::cross(h[h.size() - 2], h.back(), v) <= 0)
            h.pop_back();
        h.push_back(v);
    }
    int low = (int)h.size();
    for (int i = n - 2; i >= 0; i--)
    {
        while ((int)h.size() > low && G::cross(h[h.size() - 2], h.back(), p[i]) <= 0)
            h.pop_back();
        h.push_back(p[i]);
    }
    h.pop_back();
    return h; // CCW, no repeated endpoint, no collinear interior points.
}

// END integer_hull

#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct RealPlane
{
    using R = long double;

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
};


// BEGIN minimum_rectangle
pair<RealPlane::R, array<RealPlane::Point, 4>> minimum_rectangle(
    const vector<RealPlane::Point> &p)
{
    using G = RealPlane;
    using R = G::R;
    using P = G::Point;
    int n = int(p.size());
    if (n == 0)
        return {0, {}};
    if (n == 1)
        return {0, {p[0], p[0], p[0], p[0]}};
    if (n == 2)
        return {0, {p[0], p[1], p[1], p[0]}};
    int hi = 0;
    int lo = 0;
    int top = 0;
    P e = p[1] - p[0];
    for (int j = 1; j < n; j++)
    {
        if (G::dot(e, p[j] - p[hi]) > 0)
            hi = j;
        if (G::dot(e, p[j] - p[lo]) < 0)
            lo = j;
        if (G::cross(e, p[j] - p[top]) > 0)
            top = j;
    }
    R best = numeric_limits<R>::infinity();
    array<P, 4> box;
    for (int i = 0; i < n; i++)
    {
        e = p[(i + 1) % n] - p[i];
        auto advance = [&](int &j, auto better)
        {
            int steps = 0;
            while (steps < n && better(p[(j + 1) % n] - p[j]))
            {
                j = (j + 1) % n;
                steps++;
            }
        };
        advance(hi, [&](P v)
        {
            return G::dot(e, v) >= 0;
        });
        advance(lo, [&](P v)
        {
            return G::dot(e, v) <= 0;
        });
        advance(top, [&](P v)
        {
            return G::cross(e, v) >= 0;
        });
        R d = G::dot(e, e);
        R l = G::dot(e, p[lo] - p[i]);
        R r = G::dot(e, p[hi] - p[i]);
        R h = G::cross(e, p[top] - p[i]);
        R area = (r - l) * h / d;
        if (area < best)
        {
            best = area;
            P a = p[i] + e * (l / d);
            P b = p[i] + e * (r / d);
            P v = G::perp(e) * (h / d);
            box = {a, b, b + v, a + v};
        }
    }
    return {best, box};
}
// END minimum_rectangle


int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<IntegerPlane::Point> points(n);
    for (auto &p : points)
    {
        long double x, y;
        cin >> x >> y;
        p = {llroundl(x * 100000), llroundl(y * 100000)};
    }
    auto hull = integer_hull(points);
    vector<RealPlane::Point> p;
    for (auto q : hull)
        p.push_back({(long double)q.x, (long double)q.y});
    auto [area, box] = minimum_rectangle(p);
    cout << fixed << setprecision(10) << area / 10000000000.L << '\n';
    for (auto q : box)
        cout << q.x / 100000 << ' ' << q.y / 100000 << '\n';
}
