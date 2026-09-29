#include "../src/compact/cdq_convolution.hpp"
#include <cassert>
#include <iostream>
#include <random>

template <int mod, int root> void check()
{
    using Z = ModInt<mod>;
    using Poly = vector<Z>;
    using Ntt = NttConvolution<mod, root>;
    mt19937 rng(mod);
    assert((cdq_convolution<mod, root>({}, {}).empty()));
    int limit = 1;
    while (limit + 1 + (limit + 1) / 2 - 1 <= Ntt::max_size && limit < 200) limit++;
    for (int t = 0; t < 400; t++)
    {
        int n = 1 + rng() % limit;
        Poly g(n), b(n);
        for (int i = 0; i < n; i++)
        {
            if (i) g[i] = rng() % mod;
            b[i] = rng() % mod;
        }
        vector<long long> want(n);
        for (int i = 0; i < n; i++)
        {
            want[i] = b[i].v;
            for (int j = 0; j < i; j++)
                want[i] = (want[i] + want[j] * g[i - j].v) % mod;
        }
        auto f = cdq_convolution<mod, root>(g, b);
        for (int i = 0; i < n; i++) assert(f[i].v == want[i]);
    }
}

int main()
{
    check<2, 1>();
    check<3, 2>();
    check<17, 3>();
    check<97, 5>();
    check<998244353, 3>();
    check<2013265921, 31>();
    using Z = ModInt<998244353>;
    int n = 200000;
    vector<Z> g(n, 1), b(n);
    g[0] = 0;
    b[0] = 1;
    auto f = cdq_convolution(g, b);
    assert(f[0].v == 1);
    long long value = 1;
    for (int i = 1; i < n; i++)
    {
        assert(f[i].v == value);
        value = value * 2 % 998244353;
    }
    fill(g.begin(), g.end(), Z(0));
    g[7] = 1;
    fill(b.begin(), b.end(), Z(1));
    f = cdq_convolution(g, b);
    for (int i = 0; i < n; i++) assert(f[i].v == i / 7 + 1);
    cout << "CDQ convolution: 2400 quadratic-oracle systems over six fields, "
            "empty/singleton, small capacity limits, 200000 all-one/sparse kernels "
            "PASS\n";
}
