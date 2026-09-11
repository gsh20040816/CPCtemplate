#include "../../src/classic/offline_lca.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, root;
    cin >> n >> m >> root;
    static Offline_LCA<500000> graph;
    graph.Init(n);
    for ( int i = 1; i < n; i++ )
    {
        int u, v;
        cin >> u >> v;
        graph.Insert(u, v);
    }
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        cin >> u >> v;
        graph.Add_Query(u, v);
    }
    graph.Run(root);
    for ( int u : graph.answer )
        cout << u << '\n';
    return 0;
}
