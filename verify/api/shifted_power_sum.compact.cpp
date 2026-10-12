#include "../../src/compact/shifted_power_sum.hpp"
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    unsigned long long m;
    cin >> n >> m;
    auto f = shifted_power_sum(n, m);
    for (int i = 0; i <= n; i++)
        cout << f[i].v << "\n "[i != n];
}
