#include "../../src/classic/lifting_lca.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while ( tests-- )
    {
        int n;
        cin >> n;
        static Lifting_LCA<10000, 15> graph;
        graph.Init(n);
        vector<int> has_parent(n + 1);
        for ( int i = 1; i < n; i++ )
        {
            int u, v;
            cin >> u >> v;
            graph.Insert(u, v);
            has_parent[v] = 1;
        }
        int root = 1;
        while ( has_parent[root] )
            root++;
        graph.Build(root);
        int u, v;
        cin >> u >> v;
        cout << graph.Lca(u, v) << '\n';
    }
    return 0;
}
