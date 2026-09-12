#pragma once
#include "geometry.hpp"

struct Geometry_Extra
{
    using G = Integer_Geometry;
    using P = G::Point;
    using I = G::I;

    // No pair exists for n<2. Exact squared distance, O(n log n).
    static optional<I> Closest_Pair(vector<P> p)
    {
        int n = p.size();
        if ( n < 2 )
            return nullopt;
        sort(p.begin(), p.end());
        for ( int i = 1; i < n; i++ )
            if ( p[i] == p[i - 1] )
                return I(0);
        vector<P> tmp(n);
        auto by_y = [](P a, P b)
        {
            return tie(a.y, a.x) < tie(b.y, b.x);
        };
        function<I(int, int)> Solve = [&](int l, int r) -> I
        {
            if ( r - l <= 3 )
            {
                I best = I(1) << 120;
                for ( int i = l; i < r; i++ )
                    for ( int j = i + 1; j < r; j++ )
                        best = min(best, G::Distance_Squared(p[i], p[j]));
                sort(p.begin() + l, p.begin() + r, by_y);
                return best;
            }
            int m = (l + r) / 2;
            long long x = p[m].x;
            I best = min(Solve(l, m), Solve(m, r));
            merge(p.begin() + l,
                  p.begin() + m,
                  p.begin() + m,
                  p.begin() + r,
                  tmp.begin() + l,
                  by_y);
            copy(tmp.begin() + l, tmp.begin() + r, p.begin() + l);
            vector<P> strip;
            for ( int i = l; i < r; i++ )
                if ( (I(p[i].x) - x) * (I(p[i].x) - x) < best )
                {
                    for ( int j = (int)strip.size() - 1; j >= 0; j-- )
                    {
                        I dy = I(p[i].y) - strip[j].y;
                        if ( dy * dy >= best )
                            break;
                        best = min(best, G::Distance_Squared(p[i], strip[j]));
                    }
                    strip.push_back(p[i]);
                }
            return best;
        };
        return Solve(0, n);
    }

    // Inputs strict CCW hulls. Coordinate sums must obey IntegerGeometry's bound.
    static vector<P> Minkowski(vector<P> a, vector<P> b)
    {
        if ( a.empty() || b.empty() )
            return {};
        auto plus = [](P u, P v)
        {
            return P{u.x + v.x, u.y + v.y};
        };
        if ( a.size() < 3 || b.size() < 3 )
        {
            vector<P> p;
            for ( P u : a )
                for ( P v : b )
                    p.push_back(plus(u, v));
            return G::Convex_Hull(p);
        }
        auto start = [](vector<P> &p)
        {
            auto it = min_element(p.begin(),
                                  p.end(),
                                  [](P u, P v)
                                  {
                                      return tie(u.y, u.x) < tie(v.y, v.x);
                                  });
            rotate(p.begin(), it, p.end());
        };
        start(a);
        start(b);
        int n = a.size(), m = b.size(), i = 0, j = 0;
        vector<P> result;
        while ( i < n || j < m )
        {
            result.push_back(plus(a[i % n], b[j % m]));
            if ( i == n )
            {
                ++j;
                continue;
            }
            if ( j == m )
            {
                ++i;
                continue;
            }
            P u{a[(i + 1) % n].x - a[i].x, a[(i + 1) % n].y - a[i].y};
            P v{b[(j + 1) % m].x - b[j].x, b[(j + 1) % m].y - b[j].y};
            I c = G::Cross({0, 0}, u, v);
            if ( c >= 0 )
                ++i;
            if ( c <= 0 )
                ++j;
        }
        return result;
    }
};

struct Integer_Geometry_3D
{
    using I = __int128_t;

    // |coordinates|<=1e9: triple products fit signed int128.
    struct Point
    {
        long long x, y, z;
    };

    struct Vector
    {
        I x, y, z;
    };

    static Vector diff(Point a, Point b)
    {
        return {I(a.x) - b.x, I(a.y) - b.y, I(a.z) - b.z};
    }

    static Vector Cross(Vector a, Vector b)
    {
        return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x};
    }

    static I Dot(Vector a, Vector b)
    {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }

    static I orient(Point a, Point b, Point c, Point d)
    {
        return Dot(Cross(diff(b, a), diff(c, a)), diff(d, a));
    }

    static bool collinear(Point a, Point b, Point c)
    {
        auto v = Cross(diff(b, a), diff(c, a));
        return !v.x && !v.y && !v.z;
    }

    static bool On_Segment(Point p, Point a, Point b)
    {
        return collinear(p, a, b) && Dot(diff(a, p), diff(b, p)) <= 0;
    }
};
