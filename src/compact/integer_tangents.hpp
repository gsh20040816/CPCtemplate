#pragma once
#include "real_plane.hpp"
#include "integer_plane.hpp"

struct IntegerTangents
{
    using I = __int128_t;
    using R = RealPlane::R;
    using Point = IntegerPlane::Point;

    struct Tangent
    {
        RealPlane::Point a, b, normal;
        int side;
    };

    struct Result
    {
        bool infinite = false;
        vector<Tangent> lines;
    };

    static int sign(I x) { return (x > 0) - (x < 0); }

    // Internal: sign(a + b * sqrt(c)), c >= 0.
    static int root_sign(I a, I b, I c)
    {
        if (b == 0 || c == 0) return sign(a);
        if (a == 0 || sign(a) == sign(b)) return sign(b);
        return sign(a) * sign(a * a - b * b * c);
    }

    // Internal: sign(a + b * sqrt(c) + e * sqrt(f)).
    static int compare(I a, I b, I c, I e, I f)
    {
        int u = root_sign(a, b, c), v = f == 0 ? 0 : sign(e);
        if (u == 0) return v;
        if (v == 0 || u == v) return u;
        return u * root_sign(a * a + b * b * c - e * e * f, 2 * a * b, c);
    }

    // |coordinates| <= 10000, 0 <= radii <= 10000.
    // Lines are ordered by their exact contact (x, y) on the first circle.
    static Result solve(Point a, long long r, Point b, long long s)
    {
        for (auto p : {a, b})
            assert(-10000 <= p.x && p.x <= 10000 && -10000 <= p.y && p.y <= 10000);
        assert(0 <= r && r <= 10000 && 0 <= s && s <= 10000);
        I x = I(b.x) - a.x, y = I(b.y) - a.y;
        I q = x * x + y * y;
        if (q == 0) return {r == s, {}};
        RealPlane::Point v{R(x), R(y)}, o{R(a.x), R(a.y)}, p{R(b.x), R(b.y)};
        if (r == 0 && s == 0)
            return {false, {{o, p, RealPlane::perp(v) / sqrtl(R(q)), 0}}};

        struct Item
        {
            I g, d;
            int sign, side;
        };

        vector<Item> items;
        for (int side : {1, -1})
        {
            if (side == -1 && (r == 0 || s == 0)) continue;
            I g = I(r) - side * s, d = q - g * g;
            if (d < 0) continue;
            items.push_back({g, d, -1, side});
            if (d > 0) items.push_back({g, d, 1, side});
        }
        sort(items.begin(),
             items.end(),
             [&](Item a, Item b)
             {
                 int k = compare(x * (a.g - b.g), -y * a.sign, a.d, y * b.sign, b.d);
                 if (k != 0) return k < 0;
                 return compare(y * (a.g - b.g), x * a.sign, a.d, -x * b.sign, b.d) < 0;
             });
        Result answer;
        for (auto t : items)
        {
            auto n =
                (v * R(t.g) + RealPlane::perp(v) * (t.sign * sqrtl(R(t.d)))) / R(q);
            answer.lines.push_back({o + n * R(r), p + n * R(t.side * s), n, t.side});
        }
        return answer;
    }
};
