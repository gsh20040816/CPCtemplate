#include "../../src/compact/centroid_diameter.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    CentroidDiameter t(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        t.add(u - 1, v - 1, w);
    }
    t.build();
    for (int u = 0; u < n; u++) t.set(u, true);
    int q;
    cin >> q;
    while (q--)
    {
        char op;
        cin >> op;
        if (op == 'C')
        {
            int u;
            cin >> u;
            --u;
            t.set(u, !t.active[u]);
        }
        else
        {
            auto ans = t.query();
            if (ans) cout << get<0>(*ans) << '\n';
            else cout << "They have disappeared.\n";
        }
    }
}
