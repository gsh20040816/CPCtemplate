#include "../../src/classic/blossom.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    static General_Matching<1000> graph;
    graph.Init(n);
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        std::cin >> u >> v;
        graph.Insert(u - 1, v - 1);
    }
    std::cout << graph.Solve() << '\n';
    for ( int u = 0; u < n; u++ )
        std::cout << graph.mate[u] + 1 << (u + 1 == n ? '\n' : ' ');
}
