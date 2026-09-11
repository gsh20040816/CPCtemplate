#include "../../src/classic/graph.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    while ( std::cin >> n >> m )
    {
        if ( n == 0 && m == 0 )
            break;
        Low_Link graph(n);
        for ( int i = 0; i < m; i++ )
        {
            int u, v;
            std::cin >> u >> v;
            graph.Insert(u + 1, v + 1);
        }
        graph.Run();
        int answer = 0;
        for ( int u = 1; u <= n; u++ )
            answer = std::max(answer, graph.components + graph.delta[u]);
        std::cout << answer << '\n';
    }
}
