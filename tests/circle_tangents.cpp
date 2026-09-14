#include "../src/classic/circle_tangents.hpp"
#include "../src/compact/circle_tangents.hpp"
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <boost/multiprecision/cpp_int.hpp>
using B = boost::multiprecision::cpp_dec_float_100;
using I = boost::multiprecision::cpp_int;
using T = CircleTangents;
using G = RealPlane;
using R = G::R;
using C = G::Circle;

B dot(G::Point a, G::Point b)
{
    return B(a.x) * b.x + B(a.y) * b.y;
}

void check(C a, C b, int expected)
{
    auto answer = T::solve(a, b);
    auto old = Circle_Tangents::Solve({{a.o.x,a.o.y},a.r}, {{b.o.x,b.o.y},b.r});
    assert(answer.infinite == (expected == -1));
    assert(old.infinite == answer.infinite);
    assert(answer.lines.size() == old.lines.size());
    assert((int)answer.lines.size() == max(0, expected));
    R scale = max({fabsl(a.o.x), fabsl(a.o.y), fabsl(b.o.x), fabsl(b.o.y), a.r, b.r});
    B tolerance = B(scale) * B("1e-10");
    for (int i = 0; i < (int)answer.lines.size(); i++)
    {
        auto l = answer.lines[i];
        auto q = old.lines[i];
        assert(l.a.x == q.a.x && l.a.y == q.a.y && l.b.x == q.b.x && l.b.y == q.b.y);
        assert(l.normal.x == q.normal.x && l.normal.y == q.normal.y && l.side == q.side);
        assert(abs(dot(l.normal, l.normal) - 1) < B("1e-13"));
        auto distance = [](G::Point x, G::Point y) -> B
        {
            B dx = B(x.x) - y.x;
            B dy = B(x.y) - y.y;
            return sqrt(dx * dx + dy * dy);
        };
        assert(abs(distance(l.a, a.o) - a.r) <= tolerance);
        assert(abs(distance(l.b, b.o) - b.r) <= tolerance);
        B dx = B(l.b.x) - l.a.x;
        B dy = B(l.b.y) - l.a.y;
        assert(abs(B(l.normal.x) * dx + B(l.normal.y) * dy) <= tolerance);
        // Signed distance from each center to the returned line.
        dx = B(a.o.x) - l.a.x;
        dy = B(a.o.y) - l.a.y;
        assert(abs(abs(B(l.normal.x)*dx+B(l.normal.y)*dy) - a.r) <= tolerance);
        dx = B(b.o.x) - l.a.x;
        dy = B(b.o.y) - l.a.y;
        assert(abs(abs(B(l.normal.x)*dx+B(l.normal.y)*dy) - b.r) <= tolerance);
        for (int j = 0; j < i; j++)
        {
            auto k = answer.lines[j];
            R cross = G::cross(l.normal, k.normal);
            R offset = G::dot(l.normal, k.a - l.a);
            assert(fabsl(cross) > 1e-8L || fabsl(offset) > scale * 1e-8L);
        }
    }
    if (a.r == 0)
    {
        auto point = T::from_point(a.o, b);
        auto old_point = Circle_Tangents::From_Point({a.o.x,a.o.y},{{b.o.x,b.o.y},b.r});
        assert(point.infinite == answer.infinite && point.lines.size() == answer.lines.size());
        assert(old_point.infinite == answer.infinite && old_point.lines.size() == answer.lines.size());
    }
}

int main()
{
    mt19937 rng(20260915);
    for (int t = 0; t < 3000; t++)
    {
        long long x = int(rng() % 41) - 20, y = int(rng() % 41) - 20;
        long long r = rng() % 12, s = rng() % 12;
        I d = I(x)*x + I(y)*y;
        int expected = 0;
        if (d == 0)
            expected = r == s ? -1 : 0;
        else if (r == 0 && s == 0)
            expected = 1;
        else
            for (int sign : {1, -1})
            {
                if (sign == -1 && (r == 0 || s == 0))
                    continue;
                I gap = r - sign*s;
                expected += d > gap*gap ? 2 : d == gap*gap ? 1 : 0;
            }
        for (R scale : {1e-100L, 1.L, 1e100L})
        {
            // Divide integer coordinates first to remain within 1e100.
            C a{{0,0}, R(r)/32*scale};
            C b{{R(x)/32*scale,R(y)/32*scale},R(s)/32*scale};
            check(a, b, expected);
            check(b, a, expected);
            a.o = {-a.o.y - scale/4, a.o.x + scale/8};
            b.o = {-b.o.y - scale/4, b.o.x + scale/8};
            check(a, b, expected);
        }
    }
    check({{0,0},1},{{2,0},1},3);
    check({{0,0},2},{{1,0},1},1);
    check({{0,0},0},{{0,0},0},-1);
    check({{0,0},1},{{1e-100L,0},1},2);
    check({{0,0},1},{{1e-100L,0},2},0);
    check({{0,0},1},{{2+1e-13L,0},1},3);
    check({{0,0},1},{{2-1e-13L,0},1},3);
    cout << "Circle tangents dual exact count oracle, 100-digit line/contact certificates, point circles, tangencies and scale extremes PASS\n";
}
