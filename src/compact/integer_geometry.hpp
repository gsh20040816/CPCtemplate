#pragma once
#include "integer_hull.hpp"
#include "polygon_area2.hpp"
#include "polygon_contains.hpp"
#include "convex_contains_i64.hpp"
#include "convex_diameter2.hpp"

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
