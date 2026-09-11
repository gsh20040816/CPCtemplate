#include "../../src/classic/persistent_array.hpp"
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
    static Persistent_Array<23000000> tree;
    tree.Init(a);
    while ( m-- )
    {
        int version, op, pos;
        std::cin >> version >> op >> pos;
        if ( op == 1 )
        {
            long long value;
            std::cin >> value;
            tree.Set(version, pos, value);
        }
        else
        {
            std::cout << tree.Query(version, pos) << '\n';
            tree.Copy(version);
        }
    }
}
