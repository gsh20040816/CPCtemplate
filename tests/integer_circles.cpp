#include "../src/compact/line_circle_i64.hpp"
#include "../src/compact/circle_intersections_i64.hpp"
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <boost/multiprecision/cpp_int.hpp>

using Z = boost::multiprecision::cpp_int;
using B = boost::multiprecision::cpp_dec_float_100;
using P = IntegerPlane::Point;
using K = RealPlane::Kind;
using BP = pair<B, B>;
long long line_count = 0, circle_count = 0;
long double worst = 0;

void compare(const RealPlane::Result &got, K kind, vector<BP> expected,
             long double tolerance)
{
    assert(got.kind == kind);
    assert(got.p.size() == expected.size());
    vector<bool> used(expected.size());
    for (auto p : got.p)
    {
        assert(isfinite(p.x) && isfinite(p.y));
        int at = -1;
        long double error = numeric_limits<long double>::infinity();
        for (int i = 0; i < int(expected.size()); i++)
        {
            if (used[i]) continue;
            long double e = max(abs(B(p.x) - expected[i].first),
                                abs(B(p.y) - expected[i].second)).convert_to<long double>();
            if (e < error)
            {
                error = e;
                at = i;
            }
        }
        assert(at >= 0 && error < tolerance);
        used[at] = true;
        worst = max(worst, error);
    }
}

void line(P a, P b, P o, long long r, long double tol)
{
    // Independent parametric quadratic: |a + t(b-a) - o|^2 = r^2.
    Z x = Z(b.x) - a.x, y = Z(b.y) - a.y;
    Z u = Z(a.x) - o.x, v = Z(a.y) - o.y;
    Z aa = x * x + y * y;
    Z bb = 2 * (x * u + y * v);
    Z cc = u * u + v * v - Z(r) * r;
    Z d = bb * bb - 4 * aa * cc;
    K kind = aa == 0 ? K::degenerate : d < 0 ? K::none : d == 0 ? K::one : K::two;
    vector<BP> pts;
    if (aa != 0 && d >= 0)
    {
        for (int sign : {-1, 1})
        {
            B t = (-B(bb) + sign * sqrt(B(d))) / (2 * B(aa));
            pts.push_back({B(a.x) + t * B(x), B(a.y) + t * B(y)});
            if (d == 0) break;
        }
    }
    compare(line_circle_i64(a, b, o, r), kind, pts, tol);
    line_count++;
}

void circle(P a, long long r, P b, long long s, long double tol)
{
    Z x = Z(b.x) - a.x, y = Z(b.y) - a.y;
    Z q = x * x + y * y;
    Z sum = Z(r) + s, diff = Z(r) - s;
    K kind;
    vector<BP> pts;
    if (q == 0)
    {
        kind = r != s ? K::none : r == 0 ? K::one : K::infinite;
        if (kind == K::one) pts.push_back({B(a.x), B(a.y)});
    }
    else if (q > sum * sum || q < diff * diff)
        kind = K::none;
    else
    {
        kind = q == sum * sum || q == diff * diff ? K::one : K::two;
        B dist = sqrt(B(q));
        B along = (B(q) + B(r) * r - B(s) * s) / (2 * dist);
        B height = kind == K::one ? B(0) : B(sqrt(B(r) * r - along * along));
        for (int sign : {-1, 1})
        {
            pts.push_back({B(a.x) + along * B(x) / dist - sign * height * B(y) / dist,
                            B(a.y) + along * B(y) / dist + sign * height * B(x) / dist});
            if (kind == K::one) break;
        }
    }
    compare(circle_intersections_i64(a, r, b, s), kind, pts, tol);
    circle_count++;
}

int main()
{
    vector<P> small;
    for (int x = -2; x <= 2; x++)
        for (int y = -2; y <= 2; y++) small.push_back({x, y});
    for (auto a : small)
        for (auto b : small)
            for (int r = 0; r <= 3; r++)
            {
                for (auto o : small) line(a, b, o, r, 1e-11L);
                for (int s = 0; s <= 3; s++) circle(a, r, b, s, 1e-11L);
            }
    line({-10000, -367}, {-5909, -108}, {-7717, -10000}, 9758, 1e-8L);
    line({-5909, -108}, {-10000, -367}, {-7717, -10000}, 9758, 1e-8L);
    mt19937_64 rng(293741);
    for (long long bound : {10000LL, 1000000000LL})
    {
        auto coord = [&]() { return (long long)(rng() % (2 * bound + 1)) - bound; };
        long double tol = bound == 10000 ? 1e-8L : 3e-6L;
        for (int it = 0; it < 10000; it++)
        {
            P a{coord(), coord()}, b{coord(), coord()}, o{coord(), coord()};
            long long r = rng() % (bound + 1), s = rng() % (bound + 1);
            line(a, b, o, r, tol);
            circle(a, r, b, s, tol);
            circle(b, s, a, r, tol);
        }
        vector<P> extremes;
        for (long long x : {-bound, 0LL, bound})
            for (long long y : {-bound, 0LL, bound}) extremes.push_back({x, y});
        for (auto a : extremes)
            for (auto b : extremes)
                for (long long r : {0LL, 1LL, bound})
                {
                    for (auto o : extremes) line(a, b, o, r, tol);
                    for (long long s : {0LL, 1LL, bound}) circle(a, r, b, s, tol);
                }
    }
    cout << "line cases " << line_count << ", circle cases " << circle_count
         << ", maximum coordinate error " << setprecision(12) << worst << '\n';
}
