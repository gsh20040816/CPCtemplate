#pragma once
#include "line_projection.hpp"
#include "segment_distance_real.hpp"
#include "line_intersection_real.hpp"
#include "line_circle_intersections.hpp"
#include "circle_intersections.hpp"
#include "circle_overlap_area.hpp"

struct RealGeometry : RealPlane
{
    R eps;

    RealGeometry(R eps = 1e-12L) : eps(eps) { assert(eps > 0); }

    Point projection(Point p, Point a, Point b) const
    {
        return line_projection(p, a, b);
    }

    R segment_distance(Point p, Point a, Point b) const
    {
        return segment_distance_real(p, a, b);
    }

    Result line_intersection(Point a, Point b, Point c, Point d) const
    {
        return line_intersection_real(a, b, c, d, eps);
    }

    Result line_circle(Point a, Point b, Circle c) const
    {
        return line_circle_intersections(a, b, c, eps);
    }

    Result circles(Circle a, Circle b) const { return circle_intersections(a, b, eps); }

    R overlap(Circle a, Circle b) const { return circle_overlap_area(a, b); }
};
