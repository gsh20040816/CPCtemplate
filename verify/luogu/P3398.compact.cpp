#include "../../src/compact/euler_lca.hpp"
#include "../../src/compact/path_intersection.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    EulerLCA tree(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        tree.add(u, v);
    }
    tree.build();
    auto lca = [&](int u, int v)
    {
        return tree.lca(u, v);
    };
    while (q--)
    {
        int a, b, c, d;
        cin >> a >> b >> c >> d;
        auto result = path_intersection(a, b, c, d, tree.depth, lca);
        cout << (result.vertices ? 'Y' : 'N') << '\n';
    }
    return 0;
}
