#include "../../src/compact/real_space.hpp"
#include <iomanip>
#include <iostream>

int main()
{
    using G = RealSpace;
    G::Point a, b;
    cout << fixed << setprecision(15);
    while (cin >> a.x >> a.y >> a.z >> b.x >> b.y >> b.z)
    {
        auto c = RealSpace::cross(a, b);
        cout << G::dot(a, b) << '\n';
        cout << c.x << ' ' << c.y << ' ' << c.z << '\n';
        cout << G::norm(a) << ' ' << G::norm(b) << '\n';
        if (G::norm(a) > 0 && G::norm(b) > 0)
            cout << G::angle(a, b) << '\n';
        else
            cout << -1 << '\n';
    }
    return 0;
}
