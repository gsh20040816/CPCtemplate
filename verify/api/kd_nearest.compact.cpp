#include "../../src/compact/kd_nearest.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, d, m;
    cin >> n >> d >> m;
    vector<KDNearest<10>::Point> p(n);
    for (auto &x : p)
    {
        for (int j = 0; j < d; j++) cin >> x[j];
    }
    KDNearest<10> tree(p);
    while (m--)
    {
        KDNearest<10>::Point q{};
        for (int j = 0; j < d; j++) cin >> q[j];
        int k, far;
        cin >> k >> far;
        auto ids = tree.query(q, k, far);
        for (int id : ids) cout << id << ' ';
        cout << '\n';
    }
}
