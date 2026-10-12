#include <bits/stdc++.h>
#include <cassert>
namespace original
{
#include "fixtures/wida_montgomery_poly/12C.cpp"
}
#include "../src/compact/ntt_convolution.hpp"
using namespace std;
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        abort();
    checks++;
}

template <int P> void run()
{
    using Z = original::MontgomeryModInt32<P>;
    using N = NttConvolution<P>;
    mt19937 rng(P);
    for (int n : {9, 17, 31, 32, 33, 65, 129, 9})
    {
        int m = n + 2;
        vector<Z> a(n), b(m);
        typename N::Poly c(n), d(m);
        vector<long long> want(n + m - 1);
        for (int i = 0; i < n; i++)
        {
            int x = rng() % P;
            a[i] = Z(x);
            c[i] = x;
        }
        for (int i = 0; i < m; i++)
        {
            int x = rng() % P;
            b[i] = Z(x);
            d[i] = x;
        }
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
                want[i + j] = (want[i + j] + 1LL * c[i].v * d[j].v) % P;
        auto old = original::mul(a, b);
        auto now = N::multiply(c, d);
        for (int i = 0; i < (int)want.size(); i++)
        {
            check(old[i].get() == want[i]);
            check(now[i].v == want[i]);
        }
    }
    int n = (1 << 20) + 1, m = 1 << 20;
    auto product = original::mul(vector<Z>(n, Z(1)), vector<Z>(m, Z(1)));
    check(product.size() == (1 << 21));
    for (int i = 0; i < n + m - 1; i++)
        check(product[i].get() == min({i + 1, n, m, n + m - 1 - i}));
    n = 1 << 21;
    vector<Z> a(n);
    a[0] = Z(1);
    a[1] = Z(P - 1);
    auto inverse = original::inv(a);
    for (auto x : inverse)
        check(x.get() == 1);
    for (int i = 0; i < n; i++)
        a[i] = Z(i + 1);
    auto root_inverse = original::sqrtinv(a);
    for (int i = 0; i < n; i++)
        check(root_inverse[i].get() == (i == 0 ? 1 : (i == 1 ? P - 1 : 0)));
    cout << P << " original 2^21 convolution/inverse/first inverse-root PASS\n";
}

int main()
{
    using Z = original::MontgomeryModInt32<97>;
    auto bad = original::mul(vector<Z>(9, Z(1)), vector<Z>(9, Z(1)));
    auto good = NttConvolution<97, 5>::multiply(vector<ModInt<97>>(9, 1), vector<ModInt<97>>(9, 1));
    int mismatches = 0;
    for (int i = 0; i < 17; i++)
    {
        int expected = min(i + 1, 17 - i);
        check(good[i].v == expected);
        mismatches += bad[i].get() != expected;
    }
    check(mismatches > 0);
    cout << "mod97 original convolution:";
    for (auto x : bad)
        cout << ' ' << x.get();
    cout << "; mismatches " << mismatches << '\n';
    run<998244353>();
    run<167772161>();
    run<469762049>();
    cout << checks << " capacity/other-prime checks PASS\n";
}
