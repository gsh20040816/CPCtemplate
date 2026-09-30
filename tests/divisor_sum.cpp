#include "../src/compact/divisor_sum.hpp"
#include <array>
#include <iostream>
using ull = unsigned long long;
using u128 = __uint128_t;
using Matrix = array<array<ull, 2>, 2>;

Matrix multiply(Matrix a, Matrix b, ull mod)
{
    Matrix c{};
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 2; j++)
            for (int k = 0; k < 2; k++)
                c[i][j] = (u128(c[i][j]) + u128(a[i][k]) * b[k][j] % mod) % mod;
    return c;
}

pair<ull, ull> oracle(ull a, u128 n, ull mod)
{
    Matrix base{{{a % mod, 1 % mod}, {0, 1 % mod}}};
    Matrix result{{{1 % mod, 0}, {0, 1 % mod}}};
    while (n)
    {
        if (n & 1) result = multiply(result, base, mod);
        base = multiply(base, base, mod);
        n >>= 1;
    }
    return {result[0][0], result[0][1]};
}

int main()
{
    for (ull mod = 1; mod <= 40; mod++)
        for (ull a = 0; a <= 2 * mod; a++)
        {
            ull p = 1 % mod, s = 0;
            for (ull n = 0; n <= 100; n++)
            {
                assert(power_sum(a, n, mod) == make_pair(p, s));
                s = (s + p) % mod;
                p = p * a % mod;
            }
        }
    mt19937_64 rng(1593);
    for (int i = 0; i < 300; i++)
    {
        ull a = rng(), mod = rng() | 1;
        u128 n = (u128(rng()) << 64) | rng();
        auto expected = oracle(a, n, mod);
        assert(power_sum(a, n, mod) == expected);
    }
    for (ull mod : {1ULL, 6ULL, 9901ULL, ULLONG_MAX})
        for (ull a : {0ULL, 1ULL, ULLONG_MAX})
        {
            auto expected = oracle(a, ~u128(0), mod);
            assert(power_sum(a, ~u128(0), mod) == expected);
        }
    PollardRho a;
    for (ull x = 1; x <= 30; x++)
        for (ull exponent = 0; exponent <= 4; exponent++)
        {
            ull n = 1;
            for (ull i = 0; i < exponent; i++) n *= x;
            ull sigma = 0;
            for (ull d = 1; d <= n / d; d++)
                if (n % d == 0)
                {
                    sigma += d;
                    if (d != n / d) sigma += n / d;
                }
            for (ull mod : {1ULL, 6ULL, 9901ULL, ULLONG_MAX})
            {
                assert(divisor_sum_power(x, exponent, mod, a) == sigma % mod);
            }
        }
    for (ull mod : {1ULL, 6ULL, 9901ULL, ULLONG_MAX})
    {
        u128 length = u128(63) * ULLONG_MAX + 1;
        auto expected = oracle(2, length, mod).second;
        assert(divisor_sum_power(1ULL << 63, ULLONG_MAX, mod, a) == expected);
    }
    cout << "Divisor sum vector direct divisors, geometric iteration, uint128 matrix "
            "oracle with reduced products, composite moduli and uint128 lengths PASS\n";
}
