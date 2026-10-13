#include <bits/stdc++.h>
using i64 = long long;
#include "fixtures/wida_hullb/main.cpp"

static void show(const std::vector<Point> &h)
{
    std::cout << h.size();
    for (auto p : h)
        std::cout << ' ' << p.x << ' ' << p.y;
    std::cout << '\n';
}

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    Point a(3, 4), b(1, 0);
    std::cout << dot(a, b) << ' ' << cross(a, b) << '\n';
    int n;
    std::cin >> n;
    std::vector<Point> p(n);
    for (auto &q : p)
        std::cin >> q.x >> q.y;
    auto [hi, lo] = getHull(p);
    show(hi);
    show(lo);
}
