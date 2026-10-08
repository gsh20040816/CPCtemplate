#include "../../src/compact/plane3.hpp"
#include <iomanip>
#include <iostream>

int main()
{
    using G = RealSpace;
    G::Point n, q, a, b;
    G::R h;
    cout << fixed << setprecision(15);
    while (cin >> n.x >> n.y >> n.z >> h
               >> q.x >> q.y >> q.z
               >> a.x >> a.y >> a.z >> b.x >> b.y >> b.z)
    {
        auto f = Plane3::equation(n, h);
        auto p = f.projection(q);
        cout << f.signed_distance(q) << '\n';
        cout << p.x << ' ' << p.y << ' ' << p.z << '\n';
        G::Point x;
        int type = f.intersect(Line3::through(a, b), x);
        cout << type << '\n';
        if (type == 1)
            cout << x.x << ' ' << x.y << ' ' << x.z << '\n';
    }
    return 0;
}
