#include "../../src/compact/tree.hpp"
#include "../../src/compact/data_structure.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, q;
    while (cin >> n >> m >> q)
    {
        vector<long long> a(n + 1);
        for (int u = 1; u <= n; u++) cin >> a[u];
        HLD h(n);
        for (int i = 0; i < m; i++)
        {
            int u, v;
            cin >> u >> v;
            h.add(u, v);
        }
        h.build();
        auto bit = Fenwick<long long>(n);
        while (q--)
        {
            char op;
            int u;
            cin >> op >> u;
            if (op == 'Q') cout << a[u] + bit.sum(h.dfn[u]) << '\n';
            else
            {
                int v;
                long long x;
                cin >> v >> x;
                if (op == 'D') x = -x;
                h.path(u, v, [&](int l, int r)
                {
                    bit.add(l, x);
                    bit.add(r + 1, -x);
                });
            }
        }
    }
}
