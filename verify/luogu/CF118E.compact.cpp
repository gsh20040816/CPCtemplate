#include "../../src/compact/edge_components.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    Lowlink graph(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        std::cin >> u >> v;
        graph.add(u, v);
    }
    graph.run();
    if (graph.components != 1 ||
        std::count(graph.bridge.begin(), graph.bridge.end(), 1))
    {
        std::cout << 0 << '\n';
        return 0;
    }
    for (auto [u, v] : orient_edges(graph))
        std::cout << u << ' ' << v << '\n';
    return 0;
}
