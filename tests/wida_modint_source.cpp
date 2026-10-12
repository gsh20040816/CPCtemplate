#include <bits/stdc++.h>
#include <cassert>
#include "../src/compact/mod64.hpp"
namespace original
{
using u32 = uint32_t;
using u64 = uint64_t;
using u128 = __uint128_t;
using i64 = int64_t;
#include "fixtures/wida_mod_reduction/07E.cpp"
}
using namespace std;
using U = uint64_t;
using I = __int128_t;
using W = __uint128_t;
long long checks = 0;
void require(bool ok)
{
    if (!ok)
        throw runtime_error("Source audit oracle mismatch");
    checks++;
}
template <U P> void floating()
{
    mt19937_64 rng(P);
    int mismatches = 0;
    array<U,4> first{};
    for (int i = 0; i < 100000; i++)
    {
        U a = i == 0 ? P - 1 : rng() % P;
        U b = i == 0 ? P - 1 : rng() % P;
        U expected = W(a) * b % P;
        require(Mod64::mul(a, b, P) == expected);
        U actual = original::mulMod<P>(a, b);
        if (actual != expected)
        {
            if (!mismatches)
                first = {a,b,actual,expected};
            mismatches++;
        }
    }
    cout << "mod " << P << " mismatches " << mismatches;
    if (mismatches)
        for (U x : first)
            cout << ' ' << x;
    cout << '\n';
}
int main()
{
    cout << "long_double_digits " << numeric_limits<long double>::digits << '\n';
    floating<1000000007ULL>();
    floating<1000000000000000003ULL>();
    floating<9223372036854775783ULL>();
    mt19937_64 rng(301874355);
    for (int i = 0; i < 100000; i++)
    {
        int64_t m = 1 + rng() % INT64_MAX;
        int64_t a = int64_t(rng());
        auto [g,x] = original::invGcd(a,m);
        I normalized = (I(a) % m + m) % m;
        require(g == gcd(uint64_t(normalized),uint64_t(m)));
        require(x >= 0 && x < m / g);
        require(normalized * x % m == g % m);
    }
    using Z = original::ModInt<uint32_t(998244353)>;
    for (int i = 0; i < 100000; i++)
    {
        U a = rng() % Z::mod(), b = rng() % Z::mod();
        require((Z(a) + Z(b)).val() == (a + b) % Z::mod());
        require((Z(a) - Z(b)).val() == (a + Z::mod() - b) % Z::mod());
        require((Z(a) * Z(b)).val() == a * b % Z::mod());
        if (b)
            require((Z(a) / Z(b) * Z(b)).val() == a);
    }
    using Big = original::ModInt64<18446744073709551557ULL>;
    constexpr U p = Big::mod();
    // Addition overflows before the source's single comparison.
    U actual = (Big(p - 1) + Big(p - 1)).val();
    require(actual != p - 2);
    cout << "full_uint64_add " << actual << " expected " << p - 2 << '\n';
    cout << checks << " oracle checks\n";
}
