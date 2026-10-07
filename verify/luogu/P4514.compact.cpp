#include "../../src/compact/rectangle_fenwick.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    char op;
    int n, m;
    std::cin >> op >> n >> m;
    RectangleFenwick tree(n, m);
    int a, b, c, d;
    while (std::cin >> op >> a >> b >> c >> d)
    {
        if (op == 'L')
        {
            long long v;
            std::cin >> v;
            tree.add(a - 1, b - 1, c, d, v);
        }
        else
            std::cout << tree.sum(a - 1, b - 1, c, d) << '\n';
    }
}
