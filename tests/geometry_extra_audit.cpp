#include "../src/classic/geometry_extra.hpp"
#include "../src/compact/geometry_extra.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B = boost::multiprecision::cpp_int;
using P = IntegerGeometry::Point;
using Q = Integer_Geometry::Point;
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

vector<Q> classic(const vector<P> &p)
{
    vector<Q> q;
    for (auto a : p)
        q.push_back({a.x, a.y});
    return q;
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
    assert(closest_pair_i64(p) == expected);
    assert(Geometry_Extra::Closest_Pair(classic(p)) == expected);
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
        auto old = Geometry_Extra::Minkowski(classic(a), classic(b));
        assert(got.size() == old.size());
        for (int i = 0; i < (int)got.size(); i++)
        {
            assert(got[i].x == old[i].x && got[i].y == old[i].y);
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
    auto old_sum = Geometry_Extra::Minkowski(classic(curve), classic(curve));
    vector<P> expected;
    for (auto v : curve)
        expected.push_back({2 * v.x, 2 * v.y});
    assert(sum.size() == expected.size());
    vector<P> old_points;
    for (auto v : old_sum)
        old_points.push_back({v.x, v.y});
    sort(sum.begin(), sum.end());
    sort(old_points.begin(), old_points.end());
    assert(sum == expected && old_points == expected);
    cout << "Geometry extra dual cpp_int distance/gift-wrap oracle, rotated hulls, degeneracies, trillion coordinates and 200000 points PASS\n";
}
