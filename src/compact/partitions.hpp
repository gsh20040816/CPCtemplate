#pragma once
#include <cassert>
#include <vector>
using namespace std;
#include "fps_functions.hpp"

// BEGIN Partitions
struct Partitions
{
    int mod;
    vector<int> p;

    Partitions(int n, int mod) : mod(mod), p(n + 1)
    {
        assert(n >= 0 && mod >= 1);
        p[0] = 1 % mod;
        for (int i = 1; i <= n; i++)
        {
            long long value = 0;
            for (long long j = 1; j * (3 * j - 1) / 2 <= i; j++)
            {
                long long a = j * (3 * j - 1) / 2;
                long long b = j * (3 * j + 1) / 2;
                int sign = j % 2 ? 1 : -1;
                value += 1LL * sign * p[i - a];
                if (b <= i) value += 1LL * sign * p[i - b];
            }
            p[i] = (value % mod + mod) % mod;
        }
    }

    int limited(int n, int k) const
    {
        assert(0 <= n && n < (int)p.size() && k >= 0);
        long long step = 1LL + k;
        long long value = p[n];
        for (long long j = 1; j * (3 * j - 1) / 2 <= n / step; j++)
        {
            long long a = step * (j * (3 * j - 1) / 2);
            long long b = step * (j * (3 * j + 1) / 2);
            int sign = j % 2 ? -1 : 1;
            value += 1LL * sign * p[n - a];
            if (b <= n) value += 1LL * sign * p[n - b];
        }
        return (value % mod + mod) % mod;
    }
};

// END Partitions

// BEGIN parts_at_most
// f[s] = partitions of s into at most m parts (= parts no larger than m), 0<=s<=n.
vector<int> parts_at_most(int n, int m, int mod)
{
    assert(n >= 0 && m >= 0 && mod >= 1);
    vector<int> f(n + 1);
    f[0] = 1 % mod;
    for (int i = 1; i <= min(m, n); i++)
        for (int s = i; s <= n; s++) f[s] = (0LL + f[s] + f[s - i]) % mod;
    return f;
}
// END parts_at_most

// BEGIN parts_at_most_fps
// Same table modulo 998244353: exp(sum_{i<=m} sum_j x^{ij}/j), n+1 <= 2^22.
vector<ModInt<998244353>> parts_at_most_fps(int n, int m)
{
    using F = FpsFunctions;
    assert(n >= 0 && m >= 0 && n + 1 <= (1 << 22));
    F::Poly g(n + 1);
    vector<F::Z> inv(n + 1, 1);
    for (int j = 2; j <= n; j++) inv[j] = F::Z(F::mod - F::mod / j) * inv[F::mod % j];
    for (int i = 1; i <= min(m, n); i++)
        for (int j = 1; i * j <= n; j++) g[i * j] = g[i * j] + inv[j];
    return F::exp(g, n + 1);
}
// END parts_at_most_fps
