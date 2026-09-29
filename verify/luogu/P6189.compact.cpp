#include "../../src/compact/partitions.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, p;
    cin >> n >> p;
    Partitions part(n, p);
    cout << part.p[n] << '\n';
}
