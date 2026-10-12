// https://judge.yosupo.jp/problem/stirling_number_of_the_first_kind
#include "../../src/compact/stirling.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    auto row = stirling_first_row(n);
    for (int k = 0; k <= n; k++)
    {
        auto value = row[k];
        if ((n - k) % 2)
            value = decltype(value)(0) - value;
        cout << value.v << (k == n ? '\n' : ' ');
    }
}
