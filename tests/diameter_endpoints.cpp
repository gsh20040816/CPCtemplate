#include "../src/compact/integer_hull.hpp"
#include "../src/compact/convex_diameter2.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <random>
using namespace std;

using B = boost::multiprecision::cpp_int;
using P = IntegerPlane::Point;

B distance(P a, P b)
{
    B x = B(a.x) - b.x;
    B y = B(a.y) - b.y;
    return x * x + y * y;
}

// Gift wrapping: independent from the library's monotone chain.
vector<P> reference_hull(vector<P> p)
{
    sort(p.begin(), p.end());
    p.erase(unique(p.begin(), p.end()), p.end());
    if (p.size() < 2) return p;
    vector<P> h;
    int i = 0;
    do
    {
        h.push_back(p[i]);
        int j = (i + 1) % p.size();
        for (int k = 0; k < (int)p.size(); k++)
        {
            B turn = (B(p[j].x) - p[i].x) * (B(p[k].y) - p[i].y) -
                     (B(p[j].y) - p[i].y) * (B(p[k].x) - p[i].x);
            if (turn < 0 || (turn == 0 && distance(p[i], p[k]) > distance(p[i], p[j])))
                j = k;
        }
        i = j;
    } while (i != 0);
    return h;
}

int main()
{
    using G = IntegerPlane;
    auto check = [&](vector<G::Point> points)
    {
        B want = 0;
        for (auto a : points)
            for (auto b : points) want = max(want, distance(a, b));
        auto hull = integer_hull(points);
        assert(hull == reference_hull(points));
        for (int shift = 0; shift < max(1, int(hull.size())); shift++)
        {
            pair<int, int> ends;
            assert(convex_diameter2(hull, &ends) == want);
            assert(convex_diameter2(hull) == want);
            if (hull.empty())
                assert(ends == make_pair(-1, -1));
            else
            {
                assert(0 <= ends.first && ends.first < int(hull.size()));
                assert(0 <= ends.second && ends.second < int(hull.size()));
                assert(distance(hull[ends.first], hull[ends.second]) == want);
                if (hull.size() > 1) assert(ends.first != ends.second);
                rotate(hull.begin(), hull.begin() + 1, hull.end());
            }
        }
    };
    for (int mask = 0; mask < 512; mask++)
    {
        vector<G::Point> points;
        for (int i = 0; i < 9; i++)
            if (mask >> i & 1) points.push_back({i / 3, i % 3});
        check(points);
    }
    mt19937 rng(1452);
    for (int t = 0; t < 2000; t++)
    {
        vector<G::Point> points;
        for (int i = 0; i < 20; i++)
            points.push_back({int(rng() % 101) - 50, int(rng() % 101) - 50});
        check(points);
    }
    const long long m = 1000000000000LL;
    check({{-m, -m}, {-m, m}, {m, m}, {m, -m}});
    check({{2, 3}, {2, 3}});
    mt19937_64 wide(20260929);
    for (int t = 0; t < 1000; t++)
    {
        vector<P> p;
        for (int i = 0; i < 20; i++)
            p.push_back({(long long)(wide() % (2 * m + 1)) - m,
                         (long long)(wide() % (2 * m + 1)) - m});
        check(p);
    }
    check({{0, 0}, {m, m - 1}, {m - 1, m - 2}, {-m, -m + 1}});
    cout << "Diameter endpoints: all 3x3 subsets, independent cpp_int gift wrapping "
            "and all-pairs oracle, every "
            "cyclic hull start, degeneracies, near-collinearity and 1000 "
            "trillion-coordinate clouds PASS\n";
}
