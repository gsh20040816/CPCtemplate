#pragma once
#include "number_theory.hpp"

// BEGIN power_sum
inline pair<unsigned long long, unsigned long long>
power_sum(unsigned long long a, __uint128_t n, unsigned long long mod)
{
    assert(mod >= 1);
    if (!n) return {1 % mod, 0};
    auto [p, s] = power_sum(a, n / 2, mod);
    unsigned long long square = __uint128_t(p) * p % mod;
    unsigned long long sum = __uint128_t(s) * (p + 1) % mod;
    if (n % 2)
        return {__uint128_t(square) * a % mod, (__uint128_t(sum) + square) % mod};
    return {square, sum};
}

// END power_sum

// BEGIN divisor_sum_power
inline unsigned long long divisor_sum_power(unsigned long long a,
                                            unsigned long long b,
                                            unsigned long long mod,
                                            PollardRho &solver)
{
    assert(a >= 1 && mod >= 1);
    if (!b) return 1 % mod;
    auto factors = solver.factor(a);
    unsigned long long answer = 1 % mod;
    for (int i = 0, j; i < (int)factors.size(); i = j)
    {
        j = i + 1;
        while (j < (int)factors.size() && factors[j] == factors[i]) j++;
        __uint128_t length = __uint128_t(j - i) * b + 1;
        auto sum = power_sum(factors[i], length, mod).second;
        answer = __uint128_t(answer) * sum % mod;
    }
    return answer;
}

// END divisor_sum_power
