#include "../src/compact/fps_power.hpp"
#include <iostream>
using ll = long long;
using ull = unsigned long long;
const ll p = 998244353;
using V = vector<ll>;

V mul(const V &a, const V &b, int n)
{
    V result(n);
    for (int i = 0; i < min(n, (int)a.size()); i++)
        for (int j = 0; j < (int)b.size() && i + j < n; j++)
            result[i + j] = (result[i + j] + a[i] * b[j]) % p;
    return result;
}

V naive(V a, ull k, int n)
{
    V result(n);
    if (n) result[0] = 1;
    while (k)
    {
        if (k & 1) result = mul(result, a, n);
        a = mul(a, a, n);
        k >>= 1;
    }
    return result;
}

void check(const V &a, string k, const V &want)
{
    FpsPower::Poly input(a.begin(), a.end());
    auto got = FpsPower::power(input, k, want.size());
    assert(got.size() == want.size());
    for (int i = 0; i < (int)want.size(); i++) assert(got[i].v == want[i]);
}

ll scalar(ll a, ull k)
{
    ll result = 1;
    for (; k; k >>= 1, a = a * a % p)
        if (k & 1) result = result * a % p;
    return result;
}

int main()
{
    mt19937_64 rng(5273);
    for (int trial = 0; trial < 1600; trial++)
    {
        int n = rng() % 45, len = rng() % 70;
        V a(len);
        for (auto &x : a) x = rng() % p;
        int zeros = rng() % (len + 1);
        if (trial % 3 == 0) fill(a.begin(), a.begin() + zeros, 0);
        ull k = trial % 2 ? rng() : rng() % 12;
        check(a, string(trial % 5, '0') + to_string(k), naive(a, k, n));
    }
    for (int n = 0; n <= 6; n++)
    {
        int total = 1;
        for (int i = 0; i < n; i++) total *= 3;
        for (int mask = 0; mask < total; mask++)
        {
            int code = mask;
            V a(n);
            for (auto &x : a)
            {
                int digit = code % 3;
                x = digit == 2 ? p - 1 : digit;
                code /= 3;
            }
            for (ull k = 0; k <= 5; k++) check(a, to_string(k), naive(a, k, n));
        }
    }
    for (ull k : {0ULL, 1ULL, ull(p - 1), ull(p), ull(p + 1), ull(p) * p, ULLONG_MAX})
    {
        for (const V &a : {V{}, V{0}, V{3, 6, 3}, V{0, 0, 3, 9}, V{1, p - 1}})
            check(a, to_string(k), naive(a, k, 35));
    }
    // Decimal 10^100000: independent modular exponentiation of ten, no parser.
    string huge = "1" + string(100000, '0');
    ll km = scalar(10, 100000);
    auto power_phi = [](ll a, int k)
    {
        ll result = 1, modulus = p - 1;
        for (; k; k >>= 1, a = a * a % modulus)
            if (k & 1) result = result * a % modulus;
        return result;
    };
    ll scale = scalar(3, power_phi(10, 100000));
    int n = 500000;
    V want(n);
    vector<ll> inverse(n);
    inverse[1] = 1;
    for (int i = 2; i < n; i++) inverse[i] = (p - p / i) * inverse[p % i] % p;
    want[0] = scale;
    for (int i = 1; i < n; i++)
        want[i] = want[i - 1] * ((km - i + 1 + p) % p) % p * inverse[i] % p;
    check({3, 3}, huge, want);
    check({0, 1}, huge, V(n));
    check({},
          string(100001, '0'),
          [&]
          {
              V v(n);
              v[0] = 1;
              return v;
          }());
    int degree = 200000;
    V shifted(degree);
    shifted[degree - 1] = scalar(7, degree - 1);
    check({0, 7}, to_string(degree - 1), shifted);
    check({0, 7}, to_string(degree), V(degree));
    cout << "FPS power: 6558 exhaustive ternary powers, 1600 binary-convolution "
            "oracles, ULLONG_MAX/modulus boundaries, 100001-digit exponent, "
            "500000 binomial coefficients and exact valuation cutoffs PASS\n";
}
