#include "../../src/classic/optimization.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    std::vector<long long> a(n);
    for ( auto &x : a )
        std::cin >> x;
    Persistent_Kth tree(a);
    while ( m-- )
    {
        int l, r, k;
        std::cin >> l >> r >> k;
        std::cout << tree.Kth(l, r, k) << '\n';
    }
}
