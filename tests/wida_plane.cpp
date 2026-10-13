#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_plane/main.cpp"
using namespace Geometry;

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "overflow") {
        cout << dis(Point<int>(0, 0), Point<int>(100000, 100000)) << '\n';
        return 0;
    }
    Point<long long> a(3, 4), b(1, 0);
    cout << dot(a, b) << ' ' << cross(a, b) << ' ' << dis1(a, Point<long long>(-1, 2)) << '\n';
    Point<long long> r = rotate(a, b);
    cout << r.x << ' ' << r.y << '\n';
    Point<long long> s = a + 10;
    cout << s.x << ' ' << s.y << '\n';
    cout << (Point<long long>(0, 0) < Point<long long>(0, 1)) << ' ' << (a == a) << '\n';
    cout << sign(0.0) << ' ' << sign(1e-8) << ' ' << sign(-1.0) << '\n';
    cout << setprecision(12) << dis(Point<long long>(0, 0), a) << ' ' << fgcd(6.0L, 3.0L) << ' ' << fgcd(-6.0L, 3.0L) << '\n';
    Point<ld> u = standardize(Point<ld>(3, 4));
    Point<ld> z = standardize(Point<ld>(0, 0));
    cout << u.x << ' ' << u.y << ' ' << isfinite(z.x) << '\n';
#ifdef cc
    cout << 1 << '\n';
#else
    cout << 0 << '\n';
#endif
}
