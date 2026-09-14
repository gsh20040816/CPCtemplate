#include "../src/compact/integer_hull.hpp"
#include "../src/compact/polygon_area2.hpp"
#include "../src/compact/polygon_contains.hpp"
#include "../src/compact/convex_contains_i64.hpp"
#include "../src/compact/convex_diameter2.hpp"

int main()
{
    using P = IntegerPlane::Point;
    using I = IntegerPlane::I;
    assert(integer_hull({}).empty());
    assert(polygon_area2({}) == 0);
    assert(convex_diameter2({}) == 0);
    assert(convex_contains_i64({}, {0, 0}) == 0);
    for (long long r : {1LL, 2LL, 1000000LL, 999999999999LL})
    {
        vector<P> square{{-r, -r}, {r, -r}, {r, r}, {-r, r}};
        vector<P> cloud = square;
        cloud.push_back({0, 0});
        cloud.push_back({0, -r});
        cloud.push_back(square[0]);
        assert(integer_hull(cloud) == square);
        for (int shift = 0; shift < 4; shift++)
        {
            assert(polygon_area2(square) == I(8) * r * r);
            assert(convex_diameter2(square) == I(8) * r * r);
            for (long long x : {-r - 1, -r, 0LL, r, r + 1})
                for (long long y : {-r - 1, -r, 0LL, r, r + 1})
                {
                    int want = abs(x) > r || abs(y) > r ? 0 :
                               abs(x) == r || abs(y) == r ? 1 : 2;
                    assert(polygon_contains(square, {x, y}) == want);
                    assert(convex_contains_i64(square, {x, y}) == want);
                }
            rotate(square.begin(), square.begin() + 1, square.end());
        }
        reverse(square.begin(), square.end());
        assert(polygon_area2(square) == -I(8) * r * r);
        assert(polygon_contains(square, {0, 0}) == 2);
        vector<P> line{{-r, 0}, {0, 0}, {r, 0}, {r, 0}};
        auto h = integer_hull(line);
        assert(h.size() == 2 && polygon_area2(h) == 0);
        assert(convex_contains_i64(h, {0, 0}) == 1);
        assert(convex_contains_i64(h, {0, 1}) == 0);
        assert(convex_diameter2(h) == I(4) * r * r);
    }
    cout << "Integer geometry components: standalone headers, analytic scaled squares, rotated hulls, boundary/exterior queries, signed area and degenerate segments PASS\n";
}
