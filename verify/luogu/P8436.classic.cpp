#include "../../src/classic/biconnected.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    static Biconnected_Graph<500000> graph;
    graph.Init(n);
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        std::cin >> u >> v;
        graph.Insert(u, v);
    }
    graph.Run();
    std::vector<std::vector<int>> blocks(graph.cnt);
    for ( int u = 1; u <= n; u++ )
        blocks[graph.bel[u] - 1].push_back(u);
    std::cout << blocks.size() << '\n';
    for ( const auto &block : blocks )
    {
        std::cout << block.size();
        for ( int u : block )
            std::cout << ' ' << u;
        std::cout << '\n';
    }
}
