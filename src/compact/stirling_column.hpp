#pragma once
#include "fps_power.hpp"

// BEGIN stirling_first_column
vector<ModInt<998244353>> stirling_first_column(int n, int k)
{
    using F = FpsPower;
    using Z = F::Z;
    assert(n >= 0 && n < F::max_size / 2 && k >= 0);
    vector<Z> answer(n + 1);
    if (k > n)
        return answer;
    if (k == 0)
    {
        answer[0] = 1;
        return answer;
    }
    vector<Z> a(n - k + 1);
    vector<Z> inv(n - k + 2);
    inv[1] = 1;
    for (int i = 2; i < (int)inv.size(); i++)
        inv[i] = Z(F::mod - F::mod / i) * inv[F::mod % i];
    for (int i = 0; i < (int)a.size(); i++)
        a[i] = inv[i + 1];
    auto power = F::power(a, to_string(k), a.size());
    Z scale = 1;
    for (int i = k; i <= n; i++)
    {
        answer[i] = power[i - k] * scale;
        scale *= i + 1;
    }
    return answer;
}
// END stirling_first_column

// BEGIN stirling_second_column
vector<ModInt<998244353>> stirling_second_column(int n, int k)
{
    using F = FpsPower;
    using Z = F::Z;
    assert(n >= 0 && n < F::max_size / 2 && k >= 0);
    vector<Z> answer(n + 1);
    if (k > n)
        return answer;
    if (k == 0)
    {
        answer[0] = 1;
        return answer;
    }
    int m = n - k + 1;
    vector<Z> inverse_fact(m + 1, 1), a(m);
    for (int i = 1; i <= m; i++)
        inverse_fact[i] = inverse_fact[i - 1] * i;
    inverse_fact[m] = inverse_fact[m].inv();
    for (int i = m; i > 0; i--)
        inverse_fact[i - 1] = inverse_fact[i] * i;
    for (int i = 0; i < m; i++)
        a[i] = inverse_fact[i + 1];
    auto power = F::power(a, to_string(k), m);
    Z scale = 1;
    for (int i = k; i <= n; i++)
    {
        answer[i] = power[i - k] * scale;
        scale *= i + 1;
    }
    return answer;
}
// END stirling_second_column
