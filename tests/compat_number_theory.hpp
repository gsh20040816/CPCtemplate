#pragma once
// Test-only adapter; issue #21 removed the NumberTheory forwarding entry.
#include "../src/compact/number_theory.hpp"

namespace number_theory_detail
{
constexpr auto floor_sum_fn = floor_sum;
}

struct NumberTheory : Prime64
{
    using ll = long long;
    using i128 = __int128_t;

    static i128 exgcd(i128 a, i128 b, i128 &x, i128 &y)
    {
        return extended_gcd(a, b, x, y);
    }

    static ll inverse(ll a, ll m) { return mod_inverse(a, m); }

    static bool crt(ll &r, ll &m, ll b, ll n) { return crt_merge(r, m, b, n); }

    static i128 floor_sum(ll n, ll m, ll a, ll b)
    {
        return number_theory_detail::floor_sum_fn(n, m, a, b);
    }
};
