#include "../../src/classic/xor_walk.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    static Xor_Walk<50000> graph;
    graph.Init(n);
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        unsigned long long w;
        std::cin >> u >> v >> w;
        graph.Insert(u, v, w);
    }
    graph.Build(1);
    std::cout << *graph.Query(1, n) << '\n';
}
