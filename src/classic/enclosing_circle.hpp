#pragma once
#include "geometry.hpp"

struct Enclosing_Circle
{
    using G = Real_Geometry;
    using R = G::R;
    using Point = G::Point;
    using Circle = G::Circle;

    static Circle Diameter(Point a, Point b)
    {
        Point o = a + (b - a) / 2;
        return {o, max(G::norm(o - a), G::norm(o - b))};
    }

    static Circle Through(Point a, Point b, Point c)
    {
        Point u = b - a, v = c - a;
        R scale = max({fabsl(u.x), fabsl(u.y), fabsl(v.x), fabsl(v.y)});
        if ( scale == 0 )
            return {a, 0};
        u = u / scale;
        v = v / scale;
        R det = 2 * G::Cross(u, v);
        if ( det == 0 )
        {
            Circle best = Diameter(a, b);
            for ( Circle q : {Diameter(a, c), Diameter(b, c)} )
                if ( q.r > best.r )
                    best = q;
            return best;
        }
        R x = G::Dot(u, u), y = G::Dot(v, v);
        Point offset{(x * v.y - y * u.y) / det, (u.x * y - v.x * x) / det};
        Point o = a + offset * scale;
        return {o, max({G::norm(o - a), G::norm(o - b), G::norm(o - c)})};
    }

    static optional<Circle>
    Solve(vector<Point> p, mt19937_64 &rng, R eps = 32 * numeric_limits<R>::epsilon())
    {
        assert(eps >= 0 && eps < 1);
        if ( p.empty() )
            return nullopt;
        shuffle(p.begin(), p.end(), rng);
        Circle c{p[0], 0};
        auto outside = [&](Point q)
        {
            return G::norm(q - c.o) > c.r * (1 + eps);
        };
        for ( int i = 1; i < (int)p.size(); i++ )
            if ( outside(p[i]) )
            {
                c = {p[i], 0};
                for ( int j = 0; j < i; j++ )
                    if ( outside(p[j]) )
                    {
                        c = Diameter(p[i], p[j]);
                        for ( int k = 0; k < j; k++ )
                            if ( outside(p[k]) )
                                c = Through(p[i], p[j], p[k]);
                    }
            }
        return c;
    }
};
