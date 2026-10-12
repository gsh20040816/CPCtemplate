#include <bits/stdc++.h>
#include <cassert>
#include "../src/compact/barrett32.hpp"
namespace original
{
using u32 = uint32_t;
using u64 = uint64_t;
using u128 = __uint128_t;
using i64 = int64_t;
#include "fixtures/wida_mod_reduction/07E.cpp"
}
using namespace std;

int main()
{
    mt19937_64 rng(716968);
    long long checks = 0, corrected = 0;
    optional<array<uint32_t, 5>> source_mismatch;
    auto check = [&](uint32_t m, uint32_t a, uint32_t b)
    {
        Barrett32 reducer(m);
        uint32_t expected = uint64_t(a) * b % m;
        uint32_t actual = reducer.mul(a, b);
        if (actual != expected)
            throw runtime_error("Barrett mismatch");
        uint64_t z = uint64_t(a) * b;
        uint64_t q = (__uint128_t(z) * reducer.reciprocal) >> 64;
        corrected += z < q * m;
        original::Barrett ref(m);
        uint32_t old = ref.mul(a, b);
        if (m <= INT_MAX && old != expected)
            throw runtime_error("Original int-domain mismatch");
        if (old != expected && !source_mismatch)
            source_mismatch = array<uint32_t, 5>{m, a, b, old, expected};
        checks++;
    };
    for (uint32_t m = 1; m <= 150; m++)
        for (uint32_t a = 0; a < m; a++)
            for (uint32_t b = 0; b < m; b++)
                check(m, a, b);
    vector<uint32_t> mods{1, 2, 3, 7, 998244353, 2147483647,
                          2147483648U, 3000000000U, 4294967291U, UINT32_MAX};
    for (uint32_t m : mods)
    {
        vector<uint32_t> values{0, 1 % m, m / 2, m - 1};
        if (m > 1)
            values.push_back(m - 2);
        for (auto a : values)
            for (auto b : values)
                check(m, a, b);
        for (int t = 0; t < 100000; t++)
            check(m, rng() % m, rng() % m);
    }
    for (int t = 0; t < 1000000; t++)
    {
        uint32_t m = rng();
        if (m == 0)
            m = 1;
        check(m, rng() % m, rng() % m);
    }
    if (!corrected || !source_mismatch)
        throw runtime_error("Missing correction or source-domain counterexample");
    cout << checks << " checks; " << corrected << " quotient corrections PASS\n";
    cout << "source uint32-domain mismatch:";
    for (auto x : *source_mismatch)
        cout << ' ' << x;
    cout << '\n';
}
