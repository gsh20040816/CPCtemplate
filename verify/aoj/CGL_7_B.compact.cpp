#include "../../src/compact/triangle_incircle.hpp"

int main()
{
    RealPlane::Point a, b, c;
    cin >> a.x >> a.y >> b.x >> b.y >> c.x >> c.y;
    auto circle = triangle_incircle(a, b, c);
    if (circle)
        cout << fixed << setprecision(12) << circle->o.x << ' '
             << circle->o.y << ' ' << circle->r << '\n';
}
