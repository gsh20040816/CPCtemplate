#include "../../src/compact/partitions.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    Partitions part(n, 998244353);
    for (int i = 0; i <= n; i++) cout << part.p[i] << (i == n ? '\n' : ' ');
}
