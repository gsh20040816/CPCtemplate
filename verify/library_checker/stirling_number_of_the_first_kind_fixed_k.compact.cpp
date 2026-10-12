// https://judge.yosupo.jp/problem/stirling_number_of_the_first_kind_fixed_k
#include "../../src/compact/stirling_column.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    cin >> n >> k;
    auto column = stirling_first_column(n, k);
    for (int i = k; i <= n; i++)
    {
        auto value = column[i];
        if ((i - k) % 2)
            value = decltype(value)(0) - value;
        cout << value.v << (i == n ? '\n' : ' ');
    }
}
