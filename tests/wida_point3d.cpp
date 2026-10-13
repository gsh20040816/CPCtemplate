#include <bits/stdc++.h>
#include "fixtures/wida_point3d/main.cpp"

int main()
{
    std::cout << std::setprecision(17);
    Point a{1, 2, 3}, b{4, -1, 2};
    Point s = a + b, d = a - b, m = a * 2, q = b / 2;
    std::cout << s.x << ' ' << s.y << ' ' << s.z << '\n';
    std::cout << d.x << ' ' << d.y << ' ' << d.z << '\n';
    std::cout << m.x << ' ' << m.y << ' ' << m.z << '\n';
    std::cout << q.x << ' ' << q.y << ' ' << q.z << '\n';
    std::cout << dot(a, b) << '\n';
    Point c = cross(Point{1, 0, 0}, Point{0, 1, 0});
    std::cout << c.x << ' ' << c.y << ' ' << c.z << '\n';
    std::cout << length(Point{3, 4, 12}) << '\n';
    Point u = normalize(Point{0, 3, 4});
    std::cout << u.x << ' ' << u.y << ' ' << u.z << '\n';
    std::cout << getAng(3, 4, 5) << '\n';
    Point z = normalize(Point{0, 0, 0});
    std::cout << z.x << ' ' << z.y << ' ' << z.z << '\n';
}
