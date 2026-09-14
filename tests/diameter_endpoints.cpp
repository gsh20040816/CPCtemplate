#include "../src/compact/integer_hull.hpp"
#include "../src/compact/convex_diameter2.hpp"
#include <iostream>
#include <random>
using namespace std;

int main()
{
    using G = IntegerPlane;
    auto check = [&](vector<G::Point> points)
    {
        G::I want = 0;
        for (auto a : points)
            for (auto b : points) want = max(want, G::dist2(a, b));
        auto hull = integer_hull(points);
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
                assert(G::dist2(hull[ends.first], hull[ends.second]) == want);
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
    cout << "Diameter endpoints: all 3x3 subsets, random all-pairs oracle, every "
            "cyclic hull start, degeneracies and coordinate bounds PASS\n";
}
