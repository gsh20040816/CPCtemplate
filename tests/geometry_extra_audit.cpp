#include "compat_layers.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B = boost::multiprecision::cpp_int;
using P = IntegerGeometry::Point;
using I = __int128_t;

B turn(P a, P b, P c)
{
    return (B(b.x) - a.x) * (B(c.y) - a.y) - (B(b.y) - a.y) * (B(c.x) - a.x);
}

// Independent gift wrapping with arbitrary-precision orientation.
vector<P> hull(vector<P> p)
{
    sort(p.begin(), p.end());
    p.erase(unique(p.begin(), p.end()), p.end());
    if (p.size() < 2)
        return p;
    vector<P> h;
    int i = 0;
    do
    {
        h.push_back(p[i]);
        int j = (i + 1) % p.size();
        for (int k = 0; k < (int)p.size(); k++)
        {
            B t = turn(p[i], p[j], p[k]);
            auto distance = [&](int v) -> B
            {
                B x = B(p[v].x) - p[i].x;
                B y = B(p[v].y) - p[i].y;
                return x * x + y * y;
            };
            if (t < 0 || (t == 0 && distance(k) > distance(j)))
                j = k;
        }
        i = j;
    } while (i != 0);
    return h;
}

void minkowski(vector<P> a, vector<P> b)
{
    a = hull(a);
    b = hull(b);
    vector<P> sums;
    for (P u : a)
        for (P v : b)
            sums.push_back({u.x + v.x, u.y + v.y});
    auto want = hull(sums);
    sort(want.begin(), want.end());
    for (int repeat = 0; repeat < 3; repeat++)
    {
        auto got = minkowski_sum(a, b);
        for (int i = 0; i < (int)got.size(); i++)
        {
            if (got.size() >= 3)
                assert(turn(got[i], got[(i + 1) % got.size()], got[(i + 2) % got.size()]) > 0);
        }
        sort(got.begin(), got.end());
        assert(got == want);
        if (!a.empty())
            rotate(a.begin(), a.begin() + 1, a.end());
        if (!b.empty())
            rotate(b.begin(), b.begin() + 1, b.end());
    }
}

int main()
{
    minkowski({}, {{0, 0}});
    minkowski({{0, 0}, {3, 3}}, {{0, 0}, {-3, -3}});
    mt19937_64 rng(20260912);
    for (int test = 0; test < 2000; test++)
    {
        vector<P> a, b;
        long long scale = test % 2 ? 1 : 10000000000LL;
        for (int i = 0, n = rng() % 25; i < n; i++)
            a.push_back({(long long)(rng() % 101) * scale - 50 * scale,
                         (long long)(rng() % 101) * scale - 50 * scale});
        for (int i = 0, n = rng() % 25; i < n; i++)
            b.push_back({(long long)(rng() % 101) * scale - 50 * scale,
                         (long long)(rng() % 101) * scale - 50 * scale});
        minkowski(a, b);
    }
    vector<P> curve;
    for (long long x = -20000; x <= 20000; x++)
        curve.push_back({x, x * x});
    auto sum = minkowski_sum(curve, curve);
    vector<P> expected;
    for (auto v : curve)
        expected.push_back({2 * v.x, 2 * v.y});
    assert(sum.size() == expected.size());
    sort(sum.begin(), sum.end());
    assert(sum == expected);
    cout << "Geometry extra: 2000 cpp_int gift-wrap Minkowski oracles, rotated hulls and parabola sum PASS\n";
}
