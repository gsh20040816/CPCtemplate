#include "../../src/classic/odd_cycle_vertices.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while ( cin >> n >> m && (n || m) )
    {
        vector<vector<bool>> hate(n + 1, vector<bool>(n + 1));
        while ( m-- )
        {
            int u, v;
            cin >> u >> v;
            hate[u][v] = true;
            hate[v][u] = true;
        }
        static Biconnected_Graph<1000> graph;
        graph.Init(n);
        for ( int u = 1; u <= n; u++ )
            for ( int v = u + 1; v <= n; v++ )
                if ( !hate[u][v] )
                    graph.Insert(u, v);
        graph.Run();
        auto odd = Odd_Cycle_Vertices(graph);
        int answer = 0;
        for ( int u = 1; u <= n; u++ )
            answer += !odd[u];
        cout << answer << '\n';
    }
    return 0;
}
