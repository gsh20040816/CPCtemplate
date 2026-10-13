#include <bits/stdc++.h>
using i64 = long long;
#include "fixtures/wida_hulla/main.cpp"

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::cout << dot(Point(3, 4), Point(1, 0)) << ' ' << cross(Point(3, 4), Point(1, 0)) << '\n';
    std::cout << sgn(Point(0, 1)) << ' ' << sgn(Point(1, 0)) << ' ' << sgn(Point(-1, 0)) << ' ' << sgn(Point(0, 0)) << '\n';
    std::vector<Point> ring{Point(1, 2), Point(0, 3), Point(-1, 0)};
    norm(ring);
    std::cout << ring[0].x << ' ' << ring[0].y << '\n';
    int n;
    std::cin >> n;
    std::vector<Point> p(n);
    for (auto &q : p)
        std::cin >> q.x >> q.y;
    auto h = getHull(p);
    std::cout << h.size();
    for (auto a : h)
        std::cout << ' ' << a.x << ' ' << a.y;
    std::cout << '\n';
}
