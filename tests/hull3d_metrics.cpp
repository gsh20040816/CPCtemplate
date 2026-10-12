#include "../src/compact/hull3d_metrics.hpp"

int main()
{
    int n;
    cout << setprecision(24);
    while (cin >> n)
    {
        vector<Hull3D<long long>::Point> p(n);
        for (auto &v : p) cin >> v.x >> v.y >> v.z;
        Hull3D<long long> h(p);
        Hull3DMetrics m(h);
        auto center = m.centroid();
        auto radius = m.clearance();
        cout << h.dimension << ' ' << m.planes().size() << ' ' << bool(center);
        assert(bool(center) == bool(radius));
        if (center)
        {
            for (auto x : *center) cout << ' ' << x;
            cout << ' ' << *radius;
        }
        cout << '\n';
        for (int i : m.planes())
        {
            auto f = h.faces[i];
            for (int j : f)
                cout << h.p[j].x << ' ' << h.p[j].y << ' ' << h.p[j].z << ' ';
            cout << m.plane_distance({123, -456, 789}, i) << '\n';
        }
    }
}
