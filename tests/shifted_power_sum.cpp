#include <bits/stdc++.h>
#include <cassert>
using namespace std;
using i64 = long long;
namespace original
{
#include "fixtures/wida_poly_variants/12D-mint.cpp"
}
#include "../src/compact/shifted_power_sum.hpp"
constexpr int mod = 998244353;
using Z = ModInt<mod>;
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        throw runtime_error("oracle mismatch at " + to_string(checks));
    checks++;
}
vector<Z> choose(int n)
{
    vector<Z> c(n + 1);
    c[0] = 1;
    for (int k = 1; k <= n; k++)
        for (int i = k; i > 0; i--)
            c[i] += c[i - 1];
    return c;
}
vector<Z> brute(int n, int m)
{
    auto c = choose(n);
    vector<Z> f(n + 1);
    for (int k = 1; k <= m; k++)
    {
        Z power = 1;
        for (int i = n; i >= 0; i--)
        {
            f[i] += c[i] * power;
            power *= k;
        }
    }
    return f;
}
int main(int argc, char **argv)
{
    bool large = argc > 1;
    if (large)
    {
        int n = (1 << 22) - 1;
        auto f = shifted_power_sum(n, 2);
        Z binom = 1;
        Z power = Z(2).pow(n), half = Z(2).inv();
        vector<Z> inv(n + 1);
        inv[1] = 1;
        for (int i = 2; i <= n; i++)
            inv[i] = Z(0) - Z(mod / i) * inv[mod % i];
        for (int i = 0; i <= n; i++)
        {
            check(f[i].v == (binom * (Z(1) + power)).v);
            power *= half;
            if (i < n)
                binom *= Z(n - i) * inv[i + 1];
        }
        cout << checks << " maximum-degree binomial checks PASS\n";
        return 0;
    }
    for (int n : {0, 1, 2, 3, 7, 16, 31, 64, 65, 129, 257})
        for (int m = 0; m <= 35; m++)
        {
            auto truth = brute(n, m);
            auto got = shifted_power_sum(n, m);
            auto source = original::get(n, m);
            check(got.size() == truth.size() && source.size() == truth.size());
            for (int i = 0; i <= n; i++)
            {
                check(got[i].v == truth[i].v);
                check(source[i].x == truth[i].v);
            }
        }
    mt19937_64 rng(454);
    for (int t = 0; t < 100; t++)
    {
        int n = rng() % 100;
        unsigned long long m = rng();
        auto got = shifted_power_sum(n, m);
        auto next = shifted_power_sum(n, m + 1);
        auto c = choose(n);
        Z power = 1, k = Z((m % mod + 1) % mod);
        for (int i = n; i >= 0; i--)
        {
            check((next[i] - got[i]).v == (c[i] * power).v);
            power *= k;
        }
        int small = rng() % 36;
        auto periodic = shifted_power_sum(n, (unsigned long long)mod * (rng() % 1000000000) + small);
        auto truth = brute(n, small);
        for (int i = 0; i <= n; i++)
            check(periodic[i].v == truth[i].v);
    }
    for (unsigned long long m : {0ULL, 1ULL, (unsigned long long)mod - 1, (unsigned long long)mod, ULLONG_MAX})
    {
        check(shifted_power_sum(0, m)[0].v == m % mod);
        Z x = m % mod;
        auto f = shifted_power_sum(1, m);
        check(f[0].v == (x * (x + Z(1)) / Z(2)).v);
        check(f[1].v == x.v);
    }
    cout << checks << " independent shifted-power and source checks PASS\n";
}
