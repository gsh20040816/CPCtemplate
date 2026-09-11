#include "../../src/classic/directed_euler.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    static Directed_Euler<100000> graph;
    graph.Init(n);
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        cin >> u >> v;
        graph.Insert(u, v);
    }
    if ( !graph.Run() )
        cout << "No\n";
    else
    {
        for ( int u : graph.vertices )
            cout << u << ' ';
        cout << '\n';
    }
    return 0;
}
