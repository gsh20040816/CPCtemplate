#include "../../src/compact/real_plane.hpp"

int main()
{
    int n;
    cin >> n;
    vector<RealPlane::Point> p(n);
    for (auto &v : p)
        cin >> v.x >> v.y;
    auto c = polygon_centroid(p);
    if (!c)
        cout << "Undefined\n";
    else
        cout << fixed << setprecision(12) << c->x << ' ' << c->y << '\n';
}
