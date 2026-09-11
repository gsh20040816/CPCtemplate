#include "../src/compact/geometry.hpp"
#include "../src/classic/geometry.hpp"
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <iostream>
#include <random>

using Big = boost::multiprecision::cpp_dec_float_100;

Big overlap_reference(long double x, long double r, long double s)
{
    Big d(x), a(r), b(s);
    if (d >= a + b)
        return 0;
    if (d <= abs(a - b))
        return acos(Big(-1)) * min(a, b) * min(a, b);
    Big u = acos((d * d + a * a - b * b) / (2 * d * a));
    Big v = acos((d * d + b * b - a * a) / (2 * d * b));
    return a * a * (u - sin(2 * u) / 2) + b * b * (v - sin(2 * v) / 2);
}

template <class G, class Intersect, class Line, class Area>
void check(Intersect intersect, Line line, Area area)
{
    using K = typename G::Kind;
    using P = typename G::Point;
    using C = typename G::Circle;
    C unit{{0, 0}, 1};
    assert(intersect(unit, unit).kind == K::infinite);
    assert(intersect(C{{0, 0}, 0}, C{{0, 0}, 0}).kind == K::one);
    assert(intersect(C{{0, 0}, 0}, C{{1e-15L, 0}, 0}).kind == K::none);
    assert(intersect(C{{0, 0}, 0}, C{{0, 0}, 1e-15L}).kind == K::none);
    assert(intersect(unit, C{{0, 0}, 1 + 1e-15L}).kind == K::none);
    for (long double radius : {1.L, 1.L - 5e-15L})
    {
        C other{{1e-14L, 0}, radius};
        auto result = intersect(unit, other);
        assert(result.kind == K::two && result.p.size() == 2);
        for (P p : result.p)
        {
            assert(fabsl(G::norm(p - unit.o) - unit.r) < 1e-15L);
            assert(fabsl(G::norm(p - other.o) - other.r) < 1e-15L);
        }
    }
    for (long double scale : {1e-15L, 1e-9L, 1.L, 1e9L})
    {
        C a{{0, 0}, scale}, b{{1.5L * scale, 0}, scale};
        auto result = intersect(a, b);
        assert(result.kind == K::two);
        for (P p : result.p)
        {
            assert(fabsl(G::norm(p - a.o) - scale) < scale * 1e-12L);
            assert(fabsl(G::norm(p - b.o) - scale) < scale * 1e-12L);
        }
        assert(line(P{0, 2 * scale}, P{scale, 2 * scale}, a).kind == K::none);
        assert(line(P{0, scale}, P{scale, scale}, a).kind == K::one);
        assert(line(P{-scale, 0}, P{scale, 0}, a).kind == K::two);
    }
    for (long double delta : {1e-2L, 1e-6L, 1e-10L, 1e-14L})
    {
        long double d = 2 - delta;
        long double expected = overlap_reference(d, 1, 1).convert_to<long double>();
        long double actual = area(unit, C{{d, 0}, 1});
        assert(actual > 0);
        assert(fabsl(actual - expected) < expected * 1e-9L);
    }
    std::mt19937 rng(329755);
    for (int i = 0; i < 200; i++)
    {
        long double a = 1 + rng() % 100, b = 1 + rng() % 100;
        long double d = 1 + rng() % 210;
        long double expected = overlap_reference(d, a, b).convert_to<long double>();
        long double actual = area(C{{0, 0}, a}, C{{d, 0}, b});
        assert(fabsl(actual - expected) <= 1e-11L * std::max(1.L, expected));
    }
}

int main()
{
    RealGeometry a;
    Real_Geometry b;
    check<RealGeometry>(
        [&](auto x, auto y)
        {
            return a.circles(x, y);
        },
        [&](auto x, auto y, auto c)
        {
            return a.line_circle(x, y, c);
        },
        [&](auto x, auto y)
        {
            return a.overlap(x, y);
        });
    check<Real_Geometry>(
        [&](auto x, auto y)
        {
            return b.Circles(x, y);
        },
        [&](auto x, auto y, auto c)
        {
            return b.Line_Circle(x, y, c);
        },
        [&](auto x, auto y)
        {
            return b.Overlap(x, y);
        });
    std::cout
        << "Circle degeneracy, scale invariance and 100-digit overlap reference PASS\n";
}
