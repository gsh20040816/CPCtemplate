#pragma once
#include <cassert>
#include <vector>
using namespace std;

struct Support_Hull
{
    using ll = long long;
    using I = __int128_t;

    struct Point
    {
        ll x, y;
    };

    static I Cross(Point a, Point b, Point c)
    {
        return (I(b.x) - a.x) * (I(c.y) - a.y) - (I(b.y) - a.y) * (I(c.x) - a.x);
    }

    // oracle(a,b) maximizes a*x+b*y exactly; |coordinates| <= 1e18.
    // left/right: lowest points at the minimum/maximum x.
    template <class Oracle>
    static vector<Point> Build(Point left, Point right, Oracle &&oracle)
    {
        assert(left.x <= right.x);
        vector<Point> hull{left};
        auto dfs = [&](auto &&self, Point a, Point b) -> void
        {
            Point c = oracle(b.y - a.y, a.x - b.x);
            I turn = Cross(a, b, c);
            assert(turn <= 0);
            if ( turn < 0 )
            {
                assert(a.x < c.x && c.x < b.x);
                self(self, a, c);
                self(self, c, b);
            }
            else
            {
                while ( hull.size() >= 2 &&
                        Cross(hull[hull.size() - 2], hull.back(), b) == 0 )
                    hull.pop_back();
                hull.push_back(b);
            }
        };
        if ( left.x < right.x )
            dfs(dfs, left, right);
        else
            assert(left.y == right.y);
        return hull;
    }
};
