#include "../../src/classic/data_structure.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    std::cin >> n;
    Xor_Basis basis;
    for ( int i = 0; i < n; i++ )
    {
        unsigned long long x;
        std::cin >> x;
        basis.Insert(x);
    }
    std::cout << basis.Query() << '\n';
}
