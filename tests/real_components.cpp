#include "../src/compact/line_projection.hpp"
#include "../src/compact/segment_distance_real.hpp"
#include "../src/compact/line_intersection_real.hpp"
#include "../src/compact/line_circle_intersections.hpp"
#include "../src/compact/circle_intersections.hpp"
#include "../src/compact/circle_overlap_area.hpp"

int main()
{
    using G = RealPlane;
    using K = G::Kind;
    using P = G::Point;
    for (long double s : {1e-6L, 1.L, 1e6L})
    {
        auto near = [&](long double a, long double b)
        {
            assert(fabsl(a - b) <= 1e-10L * max(s * s, max(fabsl(a), fabsl(b))));
        };
        P a{0, 0}, b{2 * s, 0}, p{s, 3 * s};
        auto h = line_projection(p, a, b);
        near(h.x, s);
        near(h.y, 0);
        near(segment_distance_real(p, a, b), 3 * s);
        near(segment_distance_real({-3 * s, 4 * s}, a, b), 5 * s);
        h = line_projection(p, a, a);
        near(h.x, 0);
        near(h.y, 0);
        assert(line_intersection_real(a, a, a, b).kind == K::degenerate);
        assert(line_intersection_real(a, b, {0, s}, {2 * s, s}).kind == K::none);
        assert(line_intersection_real(a, b, b, a).kind == K::infinite);
        auto lines = line_intersection_real(a, b, {s, -s}, {s, s});
        assert(lines.kind == K::one && lines.p.size() == 1);
        near(lines.p[0].x, s);
        near(lines.p[0].y, 0);
        auto hit = line_circle_intersections(a, b, {{0, 0}, 2 * s});
        assert(hit.kind == K::two && hit.p.size() == 2);
        for (auto q : hit.p)
        {
            near(fabsl(q.x), 2 * s);
            near(q.y, 0);
        }
        assert(line_circle_intersections({0, 2 * s}, {s, 2 * s}, {{0, 0}, 2 * s}).kind == K::one);
        assert(circle_intersections({a, s}, {a, s}).kind == K::infinite);
        assert(circle_intersections({a, 0}, {a, 0}).kind == K::one);
        assert(circle_intersections({a, 0}, {b, 0}).kind == K::none);
        hit = circle_intersections({a, 5 * s}, {{6 * s, 0}, 5 * s});
        assert(hit.kind == K::two && hit.p.size() == 2);
        for (auto q : hit.p)
        {
            near(q.x, 3 * s);
            near(fabsl(q.y), 4 * s);
        }
        near(circle_overlap_area({a, s}, {a, 2 * s}), acosl(-1.L) * s * s);
        near(circle_overlap_area({a, s}, {b, s}), 0);
    }
    cout << "Real geometry components: standalone headers, scaled analytic projection/distance/intersections, tangencies, point circles and containment area PASS\n";
}
