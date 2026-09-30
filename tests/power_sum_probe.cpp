#include "../src/compact/divisor_sum.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    unsigned long long a, hi, lo, mod;
    while (cin >> a >> hi >> lo >> mod)
    {
        __uint128_t n = (__uint128_t(hi) << 64) | lo;
        auto [p, s] = power_sum(a, n, mod);
        cout << p << ' ' << s << '\n';
    }
}
