#include "../../src/classic/undirected_euler.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int m;
    while ( cin >> m )
    {
        static Undirected_Euler<7> graph;
        graph.Init(7);
        for ( int i = 0; i < m; i++ )
        {
            int u, v;
            cin >> u >> v;
            graph.Insert(u + 1, v + 1);
        }
        if ( !graph.Run(0, false) )
        {
            cout << "No solution\n";
            continue;
        }
        for ( int i = 0; i < m; i++ )
        {
            int id = graph.edge_ids[i];
            char direction = graph.edges[id].first == graph.vertices[i] ? '+' : '-';
            cout << id + 1 << ' ' << direction << '\n';
        }
    }
    return 0;
}
