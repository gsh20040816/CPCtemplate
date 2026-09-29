#include "../src/compact/geometry_extra.hpp"
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

void closest(const vector<P> &p, optional<I> expected = nullopt)
{
    if (!expected && p.size() >= 2)
    {
        B best = B(1) << 120;
        for (int i = 0; i < (int)p.size(); i++)
            for (int j = 0; j < i; j++)
            {
                B x = B(p[i].x) - p[j].x;
                B y = B(p[i].y) - p[j].y;
                B d = x * x + y * y;
                if (d < best)
                    best = d;
            }
        expected = best.convert_to<I>();
    }
    auto original = p;
    pair<int, int> ids{123, 456};
    assert(closest_pair_i64(p, &ids) == expected);
    assert(p == original);
    assert(closest_pair_i64(p) == expected);
    if (expected)
    {
        auto [a, b] = ids;
        assert(a >= 0 && a < (int)p.size());
        assert(b >= 0 && b < (int)p.size() && a != b);
        B x = B(p[a].x) - p[b].x;
        B y = B(p[a].y) - p[b].y;
        assert(x * x + y * y == B(*expected));
        assert(GeometryExtra::closest_pair(p) == expected);
    }
    else
        assert(ids == make_pair(-1, -1));
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
    closest({});
    closest({{0, 0}});
    closest({{-1000000000000LL, -1000000000000LL}, {1000000000000LL, 1000000000000LL}});
    minkowski({}, {{0, 0}});
    minkowski({{0, 0}, {3, 3}}, {{0, 0}, {-3, -3}});
    vector<P> grid;
    for (int x = -1; x <= 1; x++)
        for (int y = -1; y <= 1; y++) grid.push_back({x, y});
    for (int mask = 0; mask < 512; mask++)
    {
        vector<P> points;
        for (int i = 0; i < 9; i++)
            if (mask >> i & 1) points.push_back(grid[i]);
        closest(points);
        reverse(points.begin(), points.end());
        closest(points);
        if (!points.empty()) points.push_back(points[0]);
        closest(points);
    }
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
        closest(a);
        minkowski(a, b);
    }
    vector<P> p;
    for (int i = 0; i < 200000; i++)
        p.push_back({1000000000000LL, -1000000000000LL + 3LL * i});
    shuffle(p.begin(), p.end(), rng);
    closest(p, I(9));
    p.push_back(p[0]);
    closest(p, I(0));
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
    cout << "Geometry extra: original closest-pair endpoints, 512 grid subsets/reversal/duplicates, 2000 cpp_int distance/gift-wrap oracles, rotated hulls, trillion coordinates and 200000 points PASS\n";
}
