#ifndef STATIC_MODINT_MINIMAL
#include "../src/compact/number_theory.hpp"
#endif
#include <array>
#include <chrono>
#include <climits>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <string>

void check(bool ok, const char *what)
{
    if (!ok) { std::cerr << what << '\n'; std::abort(); }
}

template <int M> int norm(long long x)
{
    long long r = x % M;
    return int(r < 0 ? r + M : r);
}

template <int M> void small()
{
    using Z = ModInt<M>;
    const int one = 1 % M;
    for (long long value : {LLONG_MIN, LLONG_MIN + 1, -2147483648LL, -1LL, 0LL, 1LL, 2147483647LL, LLONG_MAX - 1, LLONG_MAX})
        check(Z(value).v == norm<M>(value), "constructor boundary");
    for (int a = 0; a < M; a++)
    {
        int inverse = -1;
        for (int b = 0; b < M; b++)
            if (1LL * a * b % M == one) { check(inverse == -1, "inverse uniqueness"); inverse = b; }
        auto got = Z(a).try_inv();
        check(bool(got) == (inverse != -1), "unit existence");
        if (got) check(got->v == inverse && Z(a).inv().v == inverse, "inverse value");
        long long power = one;
        for (int e = 0; e <= 20; e++)
        {
            check(Z(a).pow(e).v == power, "power");
            power = power * a % M;
        }
        for (int b = 0; b < M; b++)
        {
            Z x = a, y = b;
            check((x + y).v == norm<M>(1LL * a + b), "addition");
            check((x - y).v == norm<M>(1LL * a - b), "subtraction");
            check((x * y).v == int(1LL * a * b % M), "multiplication");
            check(&(x += y) == &x && x.v == norm<M>(1LL * a + b), "+= reference/value");
            x = a; check(&(x -= y) == &x && x.v == norm<M>(1LL * a - b), "-= reference/value");
            x = a; check(&(x *= y) == &x && x.v == int(1LL * a * b % M), "*= reference/value");
            if (got)
            {
                x = b;
                int want = int(1LL * b * inverse % M);
                check((x / Z(a)).v == want, "division");
                check(&(x /= Z(a)) == &x && x.v == want, "/= reference/value");
            }
        }
        Z x = a;
        check(&(x += x) == &x && x.v == norm<M>(2LL * a), "+= alias");
        x = a; check(&(x -= x) == &x && x.v == 0, "-= alias");
        x = a; check(&(x *= x) == &x && x.v == int(1LL * a * a % M), "*= alias");
        if (got) { x = a; check(&(x /= x) == &x && x.v == one, "/= alias"); }
    }
    if constexpr (M < 150) small<M + 1>();
}

unsigned long long power_ref(unsigned long long a, unsigned e, unsigned m)
{
    unsigned long long r = 1 % m;
    while (e) { if (e & 1) r = r * a % m; a = a * a % m; e >>= 1; }
    return r;
}

template <int M, bool Prime> void large()
{
    using Z = ModInt<M>;
    unsigned long long state = 0x123456789abcdefULL;
    auto verify = [&](int a)
    {
        auto inverse = Z(a).try_inv();
        check(bool(inverse) == (std::gcd(a, M) == 1), "large unit existence");
        if (inverse)
        {
            check(0 <= inverse->v && inverse->v < M, "normalized inverse");
            check((unsigned long long)a * inverse->v % M == 1, "large product certificate");
            check(Z(a).inv().v == inverse->v, "large inv adapter");
            if constexpr (Prime) check(inverse->v == int(power_ref(a, M - 2, M)), "prime Fermat reference");
        }
    };
    for (int i = 0; i < 3000; i++)
    {
        state = state * 6364136223846793005ULL + 1442695040888963407ULL;
        verify(int(state % M));
    }
    for (int a : {0, 1, 2, M / 2, M - 2, M - 1}) verify(a);
    for (long long x : {LLONG_MIN, LLONG_MIN + 1, -1LL, 0LL, 1LL, LLONG_MAX - 1, LLONG_MAX})
        check(Z(x).v == norm<M>(x), "large constructor");
}

void benchmark()
{
    using Z = ModInt<998244353>;
    unsigned long long old_sum = 0, new_sum = 0;
    auto start = std::chrono::steady_clock::now();
    for (int i = 1; i <= 200000; i++) old_sum += Z(i * 1237LL).pow(998244351).v;
    auto middle = std::chrono::steady_clock::now();
    for (int i = 1; i <= 200000; i++) new_sum += Z(i * 1237LL).inv().v;
    auto finish = std::chrono::steady_clock::now();
    check(old_sum == new_sum, "prime benchmark checksum");
    std::cout << "benchmark_us " << std::chrono::duration_cast<std::chrono::microseconds>(middle - start).count()
              << ' ' << std::chrono::duration_cast<std::chrono::microseconds>(finish - middle).count()
              << " checksum " << new_sum << '\n';
}

int main(int argc, char **argv)
{
    if (argc > 1 && std::string(argv[1]) == "reject") { (void)ModInt<8>(2).inv(); return 0; }
    if (argc > 1 && std::string(argv[1]) == "benchmark") { benchmark(); return 0; }
    small<1>();
    large<1073741824, false>();
    large<2147483646, false>();
    large<2147483647, true>();
    large<998244353, true>();
    auto fibonacci = ModInt<1836311903>(1134903170).try_inv();
    check(fibonacci && 1134903170ULL * fibonacci->v % 1836311903 == 1, "long Euclid chain");
    check(ModInt<1>(0).try_inv()->v == 0 && ModInt<1>(0).inv().v == 0, "modulus one");
    check(ModInt<8>(3).inv().v == 3 && !ModInt<8>(2).try_inv(), "composite example");
    std::cout << "Static ModInt: moduli1..150 exhaustive inverse/arithmetic/division/alias oracles, 12000 large-residue unit/existence checks plus boundaries/Fibonacci, signed64 constructors, mod1 and composite rejection PASS\n";
}
