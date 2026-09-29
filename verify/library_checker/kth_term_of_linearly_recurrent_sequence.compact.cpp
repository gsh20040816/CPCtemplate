#include "../../src/compact/bostan_mori.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int d;
    unsigned long long k;
    cin >> d >> k;
    using B = BostanMori<>;
    B::Poly init(d), c(d);
    for (auto &x : init)
    {
        int value;
        cin >> value;
        x = value;
    }
    for (auto &x : c)
    {
        int value;
        cin >> value;
        x = value;
    }
    cout << B::recurrence(init, c, k).v << '\n';
}
