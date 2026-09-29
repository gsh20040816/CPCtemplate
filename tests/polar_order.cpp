#include "../src/compact/integer_plane.hpp"
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <boost/multiprecision/cpp_int.hpp>
using B = boost::multiprecision::cpp_int;
using R = boost::multiprecision::cpp_dec_float_100;
using P = IntegerPlane::Point;

int main()
{
    IntegerPlane::PolarLess less;
    vector<P> grid;
    for (int x = -4; x <= 4; x++)
        for (int y = -4; y <= 4; y++) grid.push_back({x, y});
    for (auto a : grid)
    {
        assert(!less(a, a));
        for (auto b : grid)
        {
            assert(!(less(a, b) && less(b, a)));
            for (auto c : grid)
            {
                if (less(a, b) && less(b, c)) assert(less(a, c));
                if (!less(a, b) && !less(b, a) && !less(b, c) && !less(c, b))
                    assert(!less(a, c) && !less(c, a));
            }
        }
    }
    mt19937_64 rng(20260929);
    const long long m = 1000000000000LL;
    vector<P> points = grid;
    for (int i = 0; i < 1000; i++)
        points.push_back({(long long)(rng() % (2 * m + 1)) - m,
                          (long long)(rng() % (2 * m + 1)) - m});
    for (int sx : {-1, 1})
        for (int sy : {-1, 1})
            for (int i = 0; i < 20; i++)
                points.push_back({sx * (m - i), sy * (m - i - 1)});
    points.insert(points.end(), {{0, 0}, {0, 0}, {m, 0}, {-m, 0}, {0, m}, {0, -m}});
    vector<R> angles;
    vector<B> lengths;
    R pi = acos(R(-1));
    for (auto p : points)
    {
        R angle = p.x || p.y ? atan2(R(p.y), R(p.x)) : R(0);
        if (angle < 0) angle += 2 * pi;
        angles.push_back(angle);
        lengths.push_back(B(p.x) * p.x + B(p.y) * p.y);
    }
    for (int i = 0; i < (int)points.size(); i++)
        for (int j = 0; j < (int)points.size(); j++)
        {
            bool want = angles[i] < angles[j] ||
                        (angles[i] == angles[j] && lengths[i] < lengths[j]);
            assert(less(points[i], points[j]) == want);
        }
    shuffle(points.begin(), points.end(), rng);
    sort(points.begin(), points.end(), less);
    assert(points.front() == (P{0, 0}));
    cout << "PolarLess: 81-point all triples strict weak order; 100-digit atan2 "
            "all pairs with origin, axes, duplicate rays and trillion-scale "
            "near-parallel vectors PASS\n";
}
