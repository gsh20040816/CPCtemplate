#pragma once
#include "fps_inverse.hpp"

// BEGIN shifted_power_sum
vector<ModInt<998244353>> shifted_power_sum(int n, unsigned long long m)
{
    using F = FpsInverse;
    using Z = F::Z;
    assert(n >= 0 && 2LL * n + 1 <= F::max_size);
    Z count = m % F::mod;
    if (n == 0)
        return {count};
    if (count.v == 0)
        return vector<Z>(n + 1);
    vector<Z> fac(n + 2), invfac(n + 2);
    fac[0] = 1;
    for (int i = 1; i <= n + 1; i++)
        fac[i] = fac[i - 1] * i;
    invfac[n + 1] = fac[n + 1].inv();
    for (int i = n + 1; i > 0; i--)
        invfac[i - 1] = invfac[i] * i;
    if (count.v == 1)
    {
        vector<Z> result(n + 1);
        for (int i = 0; i <= n; i++)
            result[i] = fac[n] * invfac[i] * invfac[n - i];
        return result;
    }
    vector<Z> a(n + 1), b(n + 1);
    Z step = count + 1;
    Z power = 1;
    for (int i = 0; i <= n; i++)
    {
        power *= step;
        a[i] = (power - Z(1)) * invfac[i + 1];
        b[i] = invfac[i + 1];
    }
    auto sums = F::multiply(a, F::inverse(b, n + 1));
    vector<Z> result(n + 1);
    for (int i = 0; i <= n; i++)
        result[i] = fac[n] * invfac[i] * sums[n - i];
    return result;
}

// END shifted_power_sum
