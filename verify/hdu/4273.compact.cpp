#include "../../src/compact/hull3d_metrics.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    while (cin >> n)
    {
        vector<Hull3D<long long>::Point> p(n);
        for (auto &v : p) cin >> v.x >> v.y >> v.z;
        Hull3D<long long> h(p);
        Hull3DMetrics metrics(h);
        cout << fixed << setprecision(3) << *metrics.clearance() << '\n';
    }
}
