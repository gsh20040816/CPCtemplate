#include "../src/compact/data_structure.hpp"
#include "../src/compact/dynamic_modint.hpp"

long long norm(__int128 x, int p)
{
    x %= p;
    return (long long)(x < 0 ? x + p : x);
}

int main()
{
    using Z = mint<>;
    for (int p = 1; p <= 150; p++)
    {
        Z::set_mod(p);
        for (int a = 0; a < p; a++)
        {
            auto inv = Z(a).try_inv();
            int found = -1;
            for (int b = 0; b < p; b++)
                if (a * b % p == 1 % p) found = b;
            assert(inv.has_value() == (found >= 0));
            if (inv) assert(inv->v == found);
            for (int b = 0; b < p; b++)
            {
                assert((Z(a) + Z(b)).v == (a + b) % p);
                assert((Z(a) - Z(b)).v == (a - b + p) % p);
                assert((Z(a) * Z(b)).v == a * b % p);
                if (auto x = Z(b).try_inv()) assert((Z(a) / Z(b)).v == a * x->v % p);
            }
        }
    }
    mt19937_64 rng(918273);
    for (int p : {1, 2, 12, 998244353, 2147483646, 2147483647})
    {
        Z::set_mod(p);
        for (int t = 0; t < 20000; t++)
        {
            long long a = t == 0 ? LLONG_MIN : t == 1 ? LLONG_MAX : (long long)rng();
            long long b = (long long)rng();
            Z x(a), y(b);
            assert(x.v == norm(a, p));
            assert((x + y).v == norm((__int128)a + b, p));
            assert((x * y).v == norm((__int128)a * b, p));
            auto inv = x.try_inv();
            assert(inv.has_value() == (gcd(x.v, p) == 1));
            if (inv) assert(norm((__int128)x.v * inv->v, p) == 1 % p);
            Z z = x;
            z += z;
            assert(z.v == norm((__int128)2 * x.v, p));
            z = x;
            z *= z;
            assert(z.v == norm((__int128)x.v * x.v, p));
            uint64_t k = t % 100;
            long long ans = 1 % p;
            for (uint64_t i = 0; i < k; i++) ans = norm((__int128)ans * x.v, p);
            assert(x.pow(k).v == ans);
        }
        Fenwick<Z> f(100);
        vector<long long> a(101);
        for (int t = 0; t < 10000; t++)
        {
            int k = rng() % 100 + 1;
            long long delta = (long long)rng();
            f.add(k, Z(delta));
            a[k] = norm((__int128)a[k] + delta, p);
            int l = rng() % 100 + 1, r = rng() % 100 + 1;
            if (l > r) swap(l, r);
            long long expected = 0;
            for (int i = l; i <= r; i++) expected = norm(expected + a[i], p);
            assert(f.query(l, r).v == expected);
        }
    }
    mint<1>::set_mod(17);
    mint<2>::set_mod(12);
    auto a = mint<1>(20);
    auto b = mint<2>(20);
    assert(a.v == 3 && b.v == 8);
    mint<2>::set_mod(7);
    assert(a.v == 3 && mint<1>::mod == 17);
    // Rebuild objects after changing the modulus; old b is deliberately not used.
    assert(mint<2>(20).v == 6);
    Z::set_mod(17);
    assert(Z(1).pow(UINT64_MAX).v == 1);
    cout << "Dynamic mint: exhaustive composite inverses, int128 arithmetic, aliases, "
            "independent tags and Fenwick composition PASS\n";
}
