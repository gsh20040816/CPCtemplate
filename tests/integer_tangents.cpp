#include "../src/compact/integer_tangents.hpp"
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <boost/multiprecision/cpp_int.hpp>

using B = boost::multiprecision::cpp_dec_float_100;
using Z = boost::multiprecision::cpp_int;
using T = IntegerTangents;
using P = T::Point;
using R = RealPlane::R;
struct Ref
{
    B x, y, nx, ny;
    int side;
};
long long cases = 0;
R worst = 0;

void check(P a, long long r, P b, long long s)
{
    Z x = Z(b.x) - a.x, y = Z(b.y) - a.y;
    Z q = x * x + y * y;
    auto got = T::solve(a, r, b, s);
    assert(got.infinite == (q == 0 && r == s));
    vector<Ref> want;
    if (q != 0)
    {
        if (r == 0 && s == 0)
        {
            B d = sqrt(B(q));
            want.push_back({B(a.x), B(a.y), -B(y) / d, B(x) / d, 0});
        }
        else
        {
            B angle = atan2(B(y), B(x)), d = sqrt(B(q));
            for (int side : {1, -1})
            {
                if (side == -1 && (r == 0 || s == 0)) continue;
                Z gap = Z(r) - side * s;
                if (q < gap * gap) continue;
                B delta = acos(B(gap) / d);
                for (int sign : {-1, 1})
                {
                    B nx = cos(angle + sign * delta), ny = sin(angle + sign * delta);
                    want.push_back({B(a.x) + r * nx, B(a.y) + r * ny, nx, ny, side});
                    if (q == gap * gap) break;
                }
            }
        }
    }
    // 100-digit angular oracle; true nonzero x separation exceeds 1e-40
    // on this integer domain (degree <= 4 algebraic-integer norm bound).
    sort(want.begin(), want.end(), [](const Ref &a, const Ref &b)
    {
        if (abs(a.x - b.x) < B("1e-60")) return a.y < b.y;
        return a.x < b.x;
    });
    assert(want.size() == got.lines.size());
    vector<bool> used(want.size());
    for (int i = 0; i < int(got.lines.size()); i++)
    {
        auto t = got.lines[i];
        int match = -1;
        R error = numeric_limits<R>::infinity();
        for (int j = 0; j < int(want.size()); j++)
        {
            if (used[j] || t.side != want[j].side) continue;
            R e = max(abs(B(t.normal.x) - want[j].nx),
                      abs(B(t.normal.y) - want[j].ny)).convert_to<R>();
            if (e < error)
            {
                error = e;
                match = j;
            }
        }
        assert(match >= 0 && error < 1e-12L);
        used[match] = true;
        if (r > 0) assert(match == i);
        auto w = want[match];
        for (auto pair : {make_pair(B(t.a.x), w.x), make_pair(B(t.a.y), w.y),
                          make_pair(B(t.b.x), B(B(b.x) + t.side * s * w.nx)),
                          make_pair(B(t.b.y), B(B(b.y) + t.side * s * w.ny))})
        {
            R e = abs(pair.first - pair.second).convert_to<R>();
            assert(e < 3e-9L);
            worst = max(worst, e);
        }
    }
    cases++;
}

int main()
{
    for (int a = -10; a <= 10; a++)
        for (int b = -10; b <= 10; b++)
            for (int c = 0; c <= 20; c++)
            {
                B v = B(a) + b * sqrt(B(c));
                int expected = abs(v) < B("1e-80") ? 0 : v > 0 ? 1 : -1;
                assert(T::root_sign(a, b, c) == expected);
            }
    mt19937_64 rng(2970);
    for (int it = 0; it < 10000; it++)
    {
        long long a = (long long)(rng() % 800000001) - 400000000;
        long long b = (long long)(rng() % 40001) - 20000;
        long long c = rng() % 800000001;
        long long e = (long long)(rng() % 40001) - 20000;
        long long f = rng() % 800000001;
        B v = B(a) + b * sqrt(B(c)) + e * sqrt(B(f));
        int expected = abs(v) < B("1e-70") ? 0 : v > 0 ? 1 : -1;
        assert(T::compare(a, b, c, e, f) == expected);
        assert(T::compare(0, b, c, -b, c) == 0);
    }
    for (int x = -3; x <= 3; x++)
        for (int y = -3; y <= 3; y++)
            for (int r = 0; r <= 4; r++)
                for (int s = 0; s <= 4; s++)
                {
                    check({0, 0}, r, {x, y}, s);
                    check({-7, 5}, s, {x - 7, y + 5}, r);
                }
    for (int t : {1, 2, 100, 1000})
        for (int sx : {-1, 1})
            for (int sy : {-1, 1})
            {
                check({0, 0}, 3 * t, {sx * 5 * t, sy * 5 * t}, 4 * t);
                check({sx * 5 * t, sy * 5 * t}, 4 * t, {0, 0}, 3 * t);
            }
    for (long long bound : {1000LL, 10000LL})
    {
        auto coordinate = [&]() { return (long long)(rng() % (2 * bound + 1)) - bound; };
        for (int it = 0; it < 1000; it++)
            check({coordinate(), coordinate()}, rng() % (bound + 1),
                  {coordinate(), coordinate()}, rng() % (bound + 1));
        for (long long x : {-bound, 0LL, bound})
            for (long long y : {-bound, 0LL, bound})
                for (long long r : {0LL, 1LL, bound})
                    for (long long s : {0LL, 1LL, bound})
                        check({-bound, -bound}, r, {x, y}, s);
    }
    cout << cases << " integer tangent cases, 9261 single-radical signs, 10000 double-radical signs and cancellations PASS; max contact error "
         << setprecision(12) << worst << '\n';
}
