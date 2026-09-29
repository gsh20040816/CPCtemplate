#include "../../src/compact/tree_path_products.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using Z = ModInt<998244353>;
    int n, q;
    cin >> n >> q;
    vector<Z> weight(n);
    for (auto &w : weight)
    {
        int x;
        cin >> x;
        w = Z(1) - Z(x);
    }
    vector<vector<int>> g(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        u--;
        v--;
        g[u].push_back(v);
        g[v].push_back(u);
    }
    TreePathProducts<998244353> tree(g, weight);
    while (q--)
    {
        int op, u;
        cin >> op >> u;
        if (op == 1)
        {
            int x;
            cin >> x;
            tree.set(u - 1, Z(1) - Z(x));
        }
        else
            cout << tree.query(u - 1).v << '\n';
    }
}
