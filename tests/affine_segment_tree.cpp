#include "../src/compact/affine_segment_tree.hpp"
#include "../src/classic/affine_segment_tree.hpp"
#include <iostream>
#include <limits>
#include <random>

int main()
{
    using ll = long long;
    using I = __int128_t;
    std::mt19937_64 rng(618255);
    static Affine_Segment_Tree<64> b;
    for (int mod : {1, 2, 6, 998244353, std::numeric_limits<int>::max()})
    {
        auto norm = [&](I x)
        {
            x %= mod;
            if (x < 0)
                x += mod;
            return (ll)x;
        };
        for (int trial = 0; trial < 80; trial++)
        {
            int n = 1 + rng() % 64;
            std::vector<ll> values(n);
            for (ll &x : values)
                x = (ll)(rng() >> 1) * (rng() % 2 ? 1 : -1);
            values[0] = std::numeric_limits<ll>::min();
            AffineSegTree a(values, mod);
            b.Init(values, mod);
            for (ll &x : values)
                x = norm(x);
            for (int step = 0; step < 600; step++)
            {
                int l = 1 + rng() % n, r = 1 + rng() % n;
                if (l > r)
                    std::swap(l, r);
                ll mul = (ll)(rng() >> 1), add = -(ll)(rng() >> 1);
                if (step % 3 == 0)
                    mul = 0;
                if (step % 5 == 0)
                    add = std::numeric_limits<ll>::min();
                if (step % 7 == 0)
                    mul = std::numeric_limits<ll>::max();
                a.update(l, r, mul, add);
                b.Update(l, r, mul, add);
                for (int i = l - 1; i < r; i++)
                    values[i] = norm(I(values[i]) * mul + add);
                l = 1 + rng() % n;
                r = 1 + rng() % n;
                if (l > r)
                    std::swap(l, r);
                I sum = 0;
                for (int i = l - 1; i < r; i++)
                    sum += values[i];
                assert(a.query(l, r) == norm(sum));
                assert(b.Query(l, r) == norm(sum));
                if (step % 40 == 0)
                {
                    for (int i = 0; i < n; i++)
                    {
                        assert(a.query(i + 1, i + 1) == values[i]);
                        assert(b.Query(i + 1, i + 1) == values[i]);
                    }
                }
            }
        }
    }
    const int n = 200000, mod = 2147483647;
    std::vector<ll> values(n, mod - 1);
    AffineSegTree a(values, mod);
    static Affine_Segment_Tree<n> large;
    large.Init(values, mod);
    a.update(1, n, mod - 1, mod - 1);
    large.Update(1, n, mod - 1, mod - 1);
    assert(a.query(1, n) == 0 && large.Query(1, n) == 0);
    a.update(1, n, 0, 7);
    large.Update(1, n, 0, 7);
    a.update(2, n, 3, 1);
    large.Update(2, n, 3, 1);
    ll expected = (7LL + 22LL * (n - 1)) % mod;
    assert(a.query(1, n) == expected && large.Query(1, n) == expected);
    std::cout << "Affine segment tree int128 oracle, composition, modulus one and large range PASS\n";
}
