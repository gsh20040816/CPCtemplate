#include "../../src/classic/euler_lca.hpp"
#include "../../src/classic/path_intersection.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    static Euler_LCA<100000, 18> tree;
    tree.Init(n);
    for ( int i = 1; i < n; i++ )
    {
        int u, v;
        cin >> u >> v;
        tree.Insert(u, v);
    }
    tree.Build();
    auto lca = [&](int u, int v)
    {
        return tree.Lca(u, v);
    };
    while ( q-- )
    {
        int a, b, c, d;
        cin >> a >> b >> c >> d;
        auto result = Path_Intersection(a, b, c, d, tree.depth, lca);
        cout << (result.vertices ? 'Y' : 'N') << '\n';
    }
    return 0;
}
