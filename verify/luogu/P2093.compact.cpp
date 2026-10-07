#include "../../src/compact/kd_nearest.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<KDNearest<>::Point> p(n);
    for (auto &x : p) cin >> x[0] >> x[1];
    KDNearest<> tree(p);
    int m;
    cin >> m;
    while (m--)
    {
        KDNearest<>::Point q;
        int k;
        cin >> q[0] >> q[1] >> k;
        auto ids = tree.query(q, k, true);
        cout << ids.back() + 1 << '\n';
    }
}
