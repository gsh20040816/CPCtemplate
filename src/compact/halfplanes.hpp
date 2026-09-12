#pragma once
#include <algorithm>
#include <cassert>
#include <deque>
#include <vector>
using namespace std;

// BEGIN IntegerHalfplanes
struct IntegerHalfplanes
{
    using I = __int128_t;
    using ll = long long;

    struct Line
    {
        ll a, b, c;
    };

    struct Point
    {
        ll x, y, d;
    };

    static I cross(Line u, Line v)
    {
        return I(u.a) * v.b - I(u.b) * v.a;
    }

    static int half(Line u)
    {
        return u.b < 0 || (u.b == 0 && u.a < 0);
    }

    static Point meet(Line u, Line v)
    {
        I d = cross(u, v);
        assert(d != 0);
        I x = I(u.c) * v.b - I(u.b) * v.c;
        I y = I(u.a) * v.c - I(u.c) * v.a;
        if (d < 0)
        {
            d = -d;
            x = -x;
            y = -y;
        }
        return {(ll)x, (ll)y, (ll)d};
    }

    static I value(Line u, Point p)
    {
        return I(u.a) * p.x + I(u.b) * p.y - I(u.c) * p.d;
    }

    static bool same(Point p, Point q)
    {
        return I(p.x) * q.d == I(q.x) * p.d && I(p.y) * q.d == I(q.y) * p.d;
    }

    static vector<Point> bounded_polygon(vector<Line> lines)
    {
        vector<Line> h;
        for (auto u : lines)
        {
            assert(-1000000000 <= u.a && u.a <= 1000000000);
            assert(-1000000000 <= u.b && u.b <= 1000000000);
            assert(-1000000000 <= u.c && u.c <= 1000000000);
            if (!u.a && !u.b)
            {
                if (u.c < 0)
                    return {};
            }
            else
                h.push_back(u);
        }
        sort(h.begin(),
             h.end(),
             [](Line u, Line v)
             {
                 if (half(u) != half(v))
                     return half(u) < half(v);
                 I d = cross(u, v);
                 if (d)
                     return d > 0;
                 ll x = u.a ? (u.a > 0 ? u.a : -u.a) : (u.b > 0 ? u.b : -u.b);
                 ll y = v.a ? (v.a > 0 ? v.a : -v.a) : (v.b > 0 ? v.b : -v.b);
                 return I(u.c) * y < I(v.c) * x;
             });
        deque<Line> q;
        for (int i = 0; i < (int)h.size(); i++)
        {
            Line u = h[i];
            if (i && half(u) == half(h[i - 1]) && cross(u, h[i - 1]) == 0)
                continue;
            while (q.size() >= 2 && value(u, meet(q[q.size() - 2], q.back())) > 0)
                q.pop_back();
            while (q.size() >= 2 && value(u, meet(q[0], q[1])) > 0)
                q.pop_front();
            if (!q.empty() && cross(q.back(), u) == 0)
                return {};
            q.push_back(u);
        }
        while (q.size() >= 3 && value(q.front(), meet(q[q.size() - 2], q.back())) > 0)
            q.pop_back();
        while (q.size() >= 3 && value(q.back(), meet(q[0], q[1])) > 0)
            q.pop_front();
        if (q.size() < 3 || cross(q.front(), q.back()) == 0)
            return {};
        vector<Point> answer;
        for (int i = 0; i < (int)q.size(); i++)
        {
            Point p = meet(q[i], q[(i + 1) % q.size()]);
            if (answer.empty() || !same(answer.back(), p))
                answer.push_back(p);
        }
        if (answer.size() > 1 && same(answer.front(), answer.back()))
            answer.pop_back();
        if (answer.size() < 3)
            return {};
        return answer;
    }
};

// END IntegerHalfplanes
