// https://judge.yosupo.jp/problem/stirling_number_of_the_second_kind
#include "../../src/compact/stirling.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    auto row = stirling_second_row(n, n);
    for (int k = 0; k <= n; k++)
    {
        auto value = row[k];
        cout << value.v << (k == n ? '\n' : ' ');
    }
}
