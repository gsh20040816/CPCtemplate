#include "../src/classic/closest_pair.hpp"
#include "../src/compact/closest_pair.hpp"
#include <boost/multiprecision/cpp_dec_float.hpp>
using B = boost::multiprecision::cpp_dec_float_100;
using R = long double;
using P = ClosestPair::Point;

void check(const vector<P> &p, optional<R> expected = nullopt)
{
    if (!expected && p.size() >= 2)
    {
        B best = B("1e300");
        for (int i = 0; i < (int)p.size(); i++)
            for (int j = 0; j < i; j++)
            {
                B x = B(p[i].x) - B(p[j].x);
                B y = B(p[i].y) - B(p[j].y);
                B d = sqrt(x * x + y * y);
                if (d < best)
                    best = d;
            }
        expected = best.convert_to<R>();
    }
    vector<Closest_Pair::Point> q;
    for (auto a : p)
        q.push_back({a.x, a.y});
    auto a = ClosestPair::solve(p);
    auto b = Closest_Pair::Solve(q);
    assert(a == b);
    assert(bool(a) == bool(expected));
    if (a)
    {
        assert(isfinite(*a) && *a >= 0);
        R tolerance = 32 * numeric_limits<R>::epsilon() * *expected;
        tolerance = max(tolerance, 4 * numeric_limits<R>::denorm_min());
        assert(fabsl(*a - *expected) <= tolerance);
    }
}

int main()
{
    check({});
    check({{1, 2}});
    check({{0, 0}, {-0.L, 0}});
    check({{-1e100L, -1e100L}, {1e100L, 1e100L}});
    check({{0, 0}, {3e-100L, 4e-100L}});
    R tiny = numeric_limits<R>::denorm_min();
    check({{0, 0}, {tiny, tiny}});
    mt19937_64 rng(20260914);
    for (int t = 0; t < 2000; t++)
    {
        vector<P> p;
        R scale = powl(10.L, int(rng() % 201) - 100);
        for (int i = 0, n = 2 + rng() % 35; i < n; i++)
            p.push_back({(R(rng() % 2001) / 1000 - 1) * scale,
                         (R(rng() % 2001) / 1000 - 1) * scale});
        check(p);
    }
    for (R x : {1e-100L, 1.L, 1e100L})
    {
        R y = nextafterl(x, 0.L);
        check({{x, x}, {y, y}, {-x, 0}, {x, -x}});
    }
    vector<P> p;
    for (int i = 0; i < 200000; i++)
        p.push_back({R(i) / 8, R(i % 2) / 4});
    shuffle(p.begin(), p.end(), rng);
    check(p, R(0.25L));
    p.push_back(p[0]);
    check(p, R(0));
    cout << "Floating closest pair dual 100-digit distance oracle, decimal/adjacent/subnormal scales and 200000 points PASS\n";
}
