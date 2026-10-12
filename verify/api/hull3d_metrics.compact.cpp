#include "../../src/compact/hull3d_metrics.hpp"

int main()
{
    int n;
    cin >> n;
    vector<Hull3D<long long>::Point> p(n);
    for (auto &v : p) cin >> v.x >> v.y >> v.z;
    Hull3D<long long> h(p);
    Hull3DMetrics metrics(h);
    cout << fixed << setprecision(12);
    auto center = metrics.centroid();
    if (!center)
        cout << "NO VOLUME\n";
    else
    {
        for (auto x : *center) cout << x << ' ';
        cout << *metrics.clearance() << '\n';
    }
    auto planes = metrics.planes();
    cout << planes.size() << '\n';
    for (int i : planes)
    {
        cout << i << ' ';
        for (int v : h.faces[i]) cout << h.id[v] << ' ';
        cout << metrics.plane_distance({0, 0, 0}, i) << '\n';
    }
}
