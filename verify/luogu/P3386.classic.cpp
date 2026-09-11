#include "../../src/classic/graph.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m, e;
    std::cin >> n >> m >> e;
    static Bipartite_Matching<500, 500> graph;
    graph.Init(n, m);
    while ( e-- )
    {
        int u, v;
        std::cin >> u >> v;
        graph.Insert(u, v);
    }
    std::cout << graph.Solve() << '\n';
}
