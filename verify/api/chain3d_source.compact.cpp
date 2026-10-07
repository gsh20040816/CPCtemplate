#include "../../src/compact/chain_3d.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n;
        cin >> n;
        vector<Chain3D::Point> p(n);
        for (auto &v : p) cin >> v[0] >> v[1] >> v[2];
        Chain3D chain(p, 1 << 30, false);
        cout << chain.length << ' ' << chain.count << '\n';
    }
}
