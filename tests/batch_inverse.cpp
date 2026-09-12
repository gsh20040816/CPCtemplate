#include "../src/compact/batch_inverse.hpp"
#include "../src/classic/batch_inverse.hpp"
#include <iostream>

void check(vector<long long> a, long long mod)
{
    bool possible = true;
    for (auto v : a)
    {
        v %= mod;
        if (v < 0)
            v += mod;
        possible &= gcd(v, mod) == 1;
    }
    auto x = batch_inverse(a, mod);
    auto y = Batch_Inverse(a, mod);
    assert(x.has_value() == possible && y.has_value() == possible);
    assert(x == y);
    if (!possible)
        return;
    assert(x->size() == a.size());
    for (int i = 0; i < (int)a.size(); i++)
    {
        assert(0 <= (*x)[i] && (*x)[i] < mod);
        auto product = __int128_t((*x)[i]) * a[i] % mod;
        if (product < 0)
            product += mod;
        assert(product == 1 % mod);
    }
}

int main()
{
    for (int mod = 1; mod <= 25; mod++)
    {
        check({}, mod);
        for (int a = 0; a < mod; a++)
            for (int b = 0; b < mod; b++)
                for (int c = 0; c < mod; c++)
                    check({a - mod, b, c + mod}, mod);
    }
    mt19937_64 rng(123456);
    for (int it = 0; it < 2000; it++)
    {
        long long mod = rng() % uint64_t(LLONG_MAX) + 1;
        vector<long long> a(rng() % 60);
        for (auto &v : a)
            v = bit_cast<long long>(rng());
        check(a, mod);
    }
    for (long long m : {1LL, 2LL, 6LL, LLONG_MAX - 1, LLONG_MAX})
    {
        check({LLONG_MIN, LLONG_MAX, -1, 1}, m);
        check({0}, m);
    }
    vector<long long> a(1000000);
    iota(a.begin(), a.end(), 1);
    check(a, 1000000007);
    cout << "Batch inverse dual exhaustive unit certificates, composite rejection, signed int64 extremes, empty/modulus-one and million elements PASS\n";
}
