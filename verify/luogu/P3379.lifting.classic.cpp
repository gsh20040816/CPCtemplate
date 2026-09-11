#include "../../src/classic/lifting_lca.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q, root;
    cin >> n >> q >> root;
    static Lifting_LCA<500000> graph;
    graph.Init(n);
    for ( int i = 1; i < n; i++ )
    {
        int u, v;
        cin >> u >> v;
        graph.Insert(u, v);
    }
    graph.Build(root);
    while ( q-- )
    {
        int u, v;
        cin >> u >> v;
        cout << graph.Lca(u, v) << '\n';
    }
    return 0;
}
