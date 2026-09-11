#include "../../src/classic/modular_sqrt.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int tests;
    std::cin >> tests;
    while ( tests-- )
    {
        long long n;
        int p;
        std::cin >> n >> p;
        auto roots = Mod_Sqrt(n, p);
        if ( roots.empty() )
            std::cout << "Hola!\n";
        else
        {
            for ( int i = 0; i < (int)roots.size(); i++ )
                std::cout << roots[i] << (i + 1 == (int)roots.size() ? '\n' : ' ');
        }
    }
}
