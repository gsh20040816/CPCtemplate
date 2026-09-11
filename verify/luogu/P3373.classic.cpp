#include "../../src/classic/affine_segment_tree.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, q, mod;
    std::cin >> n >> q >> mod;
    std::vector<long long> a(n);
    for ( auto &x : a )
        std::cin >> x;
    static Affine_Segment_Tree<100000> tree;
    tree.Init(a, mod);
    while ( q-- )
    {
        int op, l, r;
        std::cin >> op >> l >> r;
        if ( op == 3 )
            std::cout << tree.Query(l, r) << '\n';
        else
        {
            long long k;
            std::cin >> k;
            if ( op == 1 )
                tree.Update(l, r, k, 0);
            else
                tree.Update(l, r, 1, k);
        }
    }
}
