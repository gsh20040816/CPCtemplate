#include "../../src/compact/garner.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<long long> moduli(n), b(n);
    long long product = 1;
    for (int i = 0; i < n; i++)
    {
        cin >> moduli[i] >> b[i];
        product *= moduli[i];
    }
    cout << garner(b, moduli, product) << '\n';
    return 0;
}
