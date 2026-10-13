#include "../../src/compact/good_number_sum.hpp"
#include <iostream>
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s, x;
    cin >> s >> x;
    auto [l, k, r] = good_number_sum(s, x);
    if (l == -1)
        cout << -1 << '\n';
    else
    {
        cout << l + 1 << ' ' << k << '\n';
        cout << k + 1 << ' ' << r << '\n';
    }
}
