#include "../src/classic/geometry_extra.hpp"
#include "../src/compact/geometry_extra.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B = boost::multiprecision::cpp_int;
using G = IntegerGeometry3D;
using C = Integer_Geometry_3D;
using P = G::Point;
using I = G::I;

C::Point classic(P p)
{
    return {p.x, p.y, p.z};
}

// Leibniz determinant, independent of cross/dot implementation.
B determinant(array<P, 4> p)
{
    array<array<B, 4>, 4> a;
    for (int i = 0; i < 4; i++)
        a[i] = {1, p[i].x, p[i].y, p[i].z};
    array<int, 4> q{0, 1, 2, 3};
    B answer = 0;
    do
    {
        int inversions = 0;
        B term = 1;
        for (int i = 0; i < 4; i++)
        {
            term *= a[i][q[i]];
            for (int j = 0; j < i; j++)
                inversions += q[j] > q[i];
        }
        if (inversions % 2)
            answer -= term;
        else
            answer += term;
    } while (next_permutation(q.begin(), q.end()));
    return answer;
}

bool collinear(P a, P b, P c)
{
    array<B, 3> u{B(b.x) - a.x, B(b.y) - a.y, B(b.z) - a.z};
    array<B, 3> v{B(c.x) - a.x, B(c.y) - a.y, B(c.z) - a.z};
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < i; j++)
            if (u[i] * v[j] != u[j] * v[i])
                return false;
    return true;
}

bool between(long long p, long long a, long long b)
{
    return min(a, b) <= p && p <= max(a, b);
}

void check(array<P, 4> p)
{
    I want = determinant(p).convert_to<I>();
    assert(G::orient(p[0], p[1], p[2], p[3]) == want);
    assert(C::orient(classic(p[0]), classic(p[1]), classic(p[2]), classic(p[3])) == want);
    auto [a, b, c, d] = p;
    bool line = collinear(a, b, c);
    bool segment = line && between(c.x, a.x, b.x) && between(c.y, a.y, b.y) && between(c.z, a.z, b.z);
    assert(G::collinear(a, b, c) == line);
    assert(C::collinear(classic(a), classic(b), classic(c)) == line);
    assert(G::on_segment(c, a, b) == segment);
    assert(C::On_Segment(classic(c), classic(a), classic(b)) == segment);
    // Verify the exposed coordinate names as well as aggregate construction.
    auto v = C::diff(classic(b), classic(a));
    assert(v.x == I(b.x) - a.x && v.y == I(b.y) - a.y && v.z == I(b.z) - a.z);
}

int main()
{
    vector<P> grid;
    for (int x = 0; x < 2; x++)
        for (int y = 0; y < 2; y++)
            for (int z = 0; z < 2; z++)
                grid.push_back({x, y, z});
    for (auto a : grid)
        for (auto b : grid)
            for (auto c : grid)
                for (auto d : grid)
                    check({a, b, c, d});
    mt19937_64 rng(20260913);
    for (int t = 0; t < 10000; t++)
    {
        array<P, 4> p;
        for (auto &v : p)
            v = {long(rng() % 2000000001) - 1000000000,
                 long(rng() % 2000000001) - 1000000000,
                 long(rng() % 2000000001) - 1000000000};
        check(p);
        swap(p[0], p[1]);
        check(p);
    }
    check({P{-1000000000, -1000000000, -1000000000},
           P{1000000000, -1000000000, -1000000000},
           P{-1000000000, 1000000000, -1000000000},
           P{-1000000000, -1000000000, 1000000000}});
    for (long long k = -10; k <= 10; k++)
    {
        check({P{-1000000000, 1000000000, -1000000000},
               P{1000000000, -1000000000, 1000000000},
               P{k * 100000000, -k * 100000000, k * 100000000}, P{1, 2, 3}});
        check({P{0, 0, 0}, P{300000000, -300000000, 0},
               P{k * 100000000, -k * 100000000, 0}, P{1, 2, 3}});
    }
    cout << "Integer 3D dual cpp_int determinant/minor oracle, exhaustive cube, degenerate segments and billion coordinates PASS\n";
}
