#include "../src/compact/montgomery_modint.hpp"
#include "fixtures/wida_mod_reduction/07D.cpp"
using U = uint64_t;
long long checks = 0;
void require(bool ok)
{
    if (!ok)
        throw runtime_error("Montgomery mismatch at " + to_string(checks));
    checks++;
}
U power(U a, U n, U p)
{
    U r = 1;
    while (n)
    {
        if (n & 1)
            r = r * a % p;
        a = a * a % p;
        n >>= 1;
    }
    return r;
}
template <uint32_t P> void run()
{
    using Z = Montgomery<P>;
    mt19937_64 rng(P);
    require(uint32_t(Z::neg_inv * P) == UINT32_MAX);
    for (long long x : {LLONG_MIN, LLONG_MIN + 1, -1LL, 0LL, 1LL, LLONG_MAX})
    {
        long long y = x % P;
        if (y < 0)
            y += P;
        require(Z(x).get() == y);
    }
    require(Z().get() == 0);
    auto check = [&](U a, U b)
    {
        Z x(a), y(b);
        require(x.v < P && y.v < P);
        require(x.get() == a && y.get() == b);
        require((x + y).get() == (a + b) % P);
        require((x - y).get() == (a + P - b) % P);
        require((x * y).get() == a * b % P);
        require((-x).get() == (P - a) % P);
        require((x == y) == (a == b));
        Z copy = x;
        copy += copy;
        require(copy.get() == 2 * a % P);
        copy = x;
        copy -= copy;
        require(copy.get() == 0);
        copy = x;
        copy *= copy;
        require(copy.get() == a * a % P);
        // Original core multiplication is valid in this domain.
        using Old = MontgomeryModInt32<P>;
        require((Old(a) * Old(b)).get() == a * b % P);
    };
    if constexpr (P < 200)
        for (U a = 0; a < P; a++)
            for (U b = 0; b < P; b++)
                check(a, b);
    for (int i = 0; i < 20000; i++)
    {
        U a = rng() % P, b = rng() % P;
        check(a, b);
        U k = rng();
        require(Z(a).pow(k).get() == power(a, k, P));
        auto inv = Z(a).try_inv();
        require(bool(inv) == (gcd(a, U(P)) == 1));
        if (inv)
        {
            require(a * inv->get() % P == 1);
            require((Z(b) / Z(a) * Z(a)).get() == b);
            Z x(a);
            x /= x;
            require(x.get() == 1);
        }
        // Cover the full documented reducer input bound, not just products.
        U z = rng() % (U(P) << 32);
        U y = Z::reduce(z);
        require(y < P && y * ((U(1) << 32) % P) % P == z % P);
    }
    for (U a : {U(0), U(1), U(P - 1)})
        for (U k : {U(0), U(P - 1), U(1) << 63, UINT64_MAX})
            require(Z(a).pow(k).get() == power(a, k, P));
}
int main()
{
    run<3>();
    run<5>();
    run<9>();
    run<15>();
    run<97>();
    run<101>();
    run<998244353>();
    run<1000000007>();
    run<1073741823>();
    require(MontgomeryModInt32<7>(0).pow(6).get() == 1);
    require(Montgomery<7>(0).pow(6).get() == 0);
    require(MontgomeryModInt32<9>(2).inv().get() == 2);
    require(Montgomery<9>(2).inv().get() == 5);
    cout << checks << " checks; original zero-power and composite-inverse counterexamples confirmed\n";
}
