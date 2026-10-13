#include <bits/stdc++.h>
using i64 = long long;
#include "fixtures/wida_hullc/main.cpp"

static void show(const std::vector<Point> &h)
{
    std::cout << h.size();
    for (auto p : h)
        std::cout << ' ' << p.real() << ' ' << p.imag();
    std::cout << '\n';
}

int main(int argc, char **argv)
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::string mode = argc > 1 ? argv[1] : "hull";
    if (mode == "tiny")
    {
        show(complexHull({}));
        show(complexHull({Point(1, 2)}));
        return 0;
    }
    if (mode == "labels")
    {
        Point r = rot(Point(3, 4));
        std::cout << r.real() << ' ' << r.imag() << '\n';
        std::cout << sgn(Point(0, 1)) << ' ' << sgn(Point(0, 0)) << ' ' << sgn(Point(-1, 0)) << ' ' << sgn(Point(1, 0)) << '\n';
        return 0;
    }
    int n;
    std::cin >> n;
    std::vector<Point> a(n);
    for (auto &p : a)
    {
        i64 px, py;
        std::cin >> px >> py;
        p = Point(px, py);
    }
    show(complexHull(a));
}
