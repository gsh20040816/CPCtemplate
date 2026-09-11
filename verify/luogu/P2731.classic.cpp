#include "../../src/classic/undirected_euler.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int m;
    cin >> m;
    static Undirected_Euler<500> graph;
    graph.Init(500);
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        cin >> u >> v;
        graph.Insert(u, v);
    }
    if ( !graph.Run() )
        return 0;
    for ( int u : graph.vertices )
        cout << u << '\n';
    return 0;
}
