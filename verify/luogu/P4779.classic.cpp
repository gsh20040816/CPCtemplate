#include "../../src/classic/graph.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m, s;
    std::cin >> n >> m >> s;
    Shortest_Path graph(n);
    while ( m-- )
    {
        int u, v;
        long long w;
        std::cin >> u >> v >> w;
        graph.Insert(u, v, w);
    }
    graph.Run(s);
    for ( int i = 1; i <= n; i++ )
        std::cout << graph.dis[i] << (i == n ? '\n' : ' ');
}
