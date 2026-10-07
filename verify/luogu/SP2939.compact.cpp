#include "../../src/compact/centroid_nearest.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    std::cin >> n;
    CentroidNearest tree(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        std::cin >> u >> v;
        tree.add(u - 1, v - 1);
    }
    tree.build();
    int q;
    std::cin >> q;
    while (q--)
    {
        int op, u;
        std::cin >> op >> u;
        --u;
        if (op == 0)
            tree.set(u, !tree.active[u]);
        else
        {
            auto ans = tree.query(u);
            std::cout << (ans ? ans->first : -1) << '\n';
        }
    }
}
