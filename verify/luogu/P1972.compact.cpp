#include "../../src/compact/persistent_distinct.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    std::cin >> n;
    std::vector<long long> a(n);
    for (auto &x : a) std::cin >> x;
    PersistentDistinct tree(a);
    int m;
    std::cin >> m;
    while (m--)
    {
        int l, r;
        std::cin >> l >> r;
        std::cout << tree.query(l, r) << '\n';
    }
}
