#include "../../src/compact/mixed_euler.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n, m;
        cin >> n >> m;
        vector<array<int, 3>> edges(m);
        for (auto &edge : edges)
            cin >> edge[0] >> edge[1] >> edge[2];

        auto result = mixed_euler_orientation(n, edges);
        cout << (result ? "possible" : "impossible") << '\n';
    }
    return 0;
}
