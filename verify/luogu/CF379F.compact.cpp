#include "../../src/compact/tree.hpp"
#include "../../src/compact/tree_diameter.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    int n = 4 + 2 * q;
    HLD tree(n);
    for (int v = 2; v <= 4; v++) tree.add(1, v);
    for (int i = 0; i < q; i++)
    {
        int v;
        cin >> v;
        tree.add(v, 5 + 2 * i);
        tree.add(v, 6 + 2 * i);
    }
    tree.build();
    auto dis = [&](int u, int v)
    {
        return tree.dep[u] + tree.dep[v] - 2 * tree.dep[tree.lca(u, v)];
    };
    TreeDiameter cur;
    for (int v = 1; v <= 4; v++) cur.insert(v, dis);
    for (int i = 0; i < q; i++)
    {
        cur.insert(5 + 2 * i, dis);
        cur.insert(6 + 2 * i, dis);
        cout << cur.length << '\n';
    }
    return 0;
}
