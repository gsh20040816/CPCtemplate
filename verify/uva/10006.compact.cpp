#include "../../src/compact/carmichael.hpp"
#include "../../src/compact/prime64.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    while (cin >> n && n)
    {
        bool special = !Prime64::prime(n) && (n - 1) % carmichael(n) == 0;
        if (special)
            cout << "The number " << n << " is a Carmichael number.\n";
        else
            cout << n << " is normal.\n";
    }
    return 0;
}
