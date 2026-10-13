#include <bits/stdc++.h>
#include "fixtures/wida_point2d/main.cpp"

int main()
{
    using P = Point<long long>;
    using L = Line<long long>;
    P a(3, 4), b(1, 0);
    std::cout << dot(a, b) << ' ' << cross(a, b) << ' ' << square(a) << '\n';
    P r = rotate(a);
    std::cout << r.x << ' ' << r.y << '\n';
    std::cout << sgn(P(0, 1)) << ' ' << sgn(P(1, 0)) << ' ' << sgn(P(-1, 0)) << ' ' << sgn(P(0, 0)) << '\n';
    L h(P(0, 0), P(4, 0)), v(P(1, 1), P(1, 3)), p2(P(2, 0), P(6, 0));
    std::cout << parallel(h, v) << ' ' << parallel(h, p2) << '\n';
    std::cout << pointOnLineLeft(P(0, 1), h) << ' ' << pointOnSegment(P(2, 0), h) << ' ' << pointOnSegment(P(5, 0), h) << '\n';
    P hit = lineIntersection(h, v);
    std::cout << hit.x << ' ' << hit.y << '\n';
    std::cout << std::setprecision(12) << distance(P(0, 0), P(3, 4)) << ' ' << distancePL(P(0, 1), h) << ' ' << distancePS(P(5, 1), h) << '\n';
}
