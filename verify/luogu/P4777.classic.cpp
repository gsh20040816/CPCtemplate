#include "../../src/classic/number_theory.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int count;
    cin >> count;
    long long r = 0, modulus = 1;
    while ( count-- )
    {
        long long m, b;
        cin >> m >> b;
        if ( !Number_Theory::Crt(r, modulus, b, m) )
        {
            cout << -1 << '\n';
            return 0;
        }
    }
    cout << r << '\n';
    return 0;
}
