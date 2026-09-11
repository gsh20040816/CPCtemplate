#include "../../src/compact/graph.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    TwoSAT sat(n);
    while (m--)
    {
        int x, a, y, b;
        std::cin >> x >> a >> y >> b;
        sat.add(x, a, y, b);
    }
    if (!sat.solve())
    {
        std::cout << "IMPOSSIBLE\n";
        return 0;
    }
    std::cout << "POSSIBLE\n";
    for (int i = 1; i <= n; i++)
        std::cout << sat.ans[i] << (i == n ? '\n' : ' ');
}
