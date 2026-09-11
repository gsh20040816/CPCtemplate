#include "../../src/compact/xor_walk.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    XorWalk graph(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        unsigned long long w;
        std::cin >> u >> v >> w;
        graph.add(u, v, w);
    }
    graph.build(1);
    std::cout << *graph.query(1, n) << '\n';
}
