#include "../../src/compact/dsu_on_tree.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    std::cin >> n;
    std::vector<int> colors(n + 1);
    for (int u = 1; u <= n; u++) std::cin >> colors[u];
    SubtreeColors tree(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        std::cin >> u >> v;
        tree.add(u, v);
    }
    tree.run(colors);
    for (int u = 1; u <= n; u++) std::cout << tree.answer[u] << (u == n ? '\n' : ' ');
}
