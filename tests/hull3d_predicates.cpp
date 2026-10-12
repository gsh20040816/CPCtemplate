#include "../src/compact/hull3d.hpp"

int main()
{
    int n;
    cin >> n;
    while (n--)
    {
        array<Hull3D<>::Point, 4> p;
        for (auto &v : p) cin >> v.x >> v.y >> v.z;
        auto normal = Hull3D<>::normal_sign(p[0], p[1], p[2]);
        cout << Hull3D<>::orient_sign(p[0], p[1], p[2], p[3]);
        for (int v : normal) cout << ' ' << v;
        cout << '\n';
    }
}
