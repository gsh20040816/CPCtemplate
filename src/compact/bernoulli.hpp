#pragma once
#include "fps_inverse.hpp"

// BEGIN bernoulli
// B_0..B_n mod 998244353 from x/(e^x-1) (B_1 = -1/2). n + 1 <= 2^23. O(n log n).
vector<ModInt<998244353>> bernoulli(int n)
{
    using F = FpsInverse;
    assert(n >= 0 && n + 2 <= F::max_size);
    vector<F::Z> fac(n + 2, 1), ifac(n + 2);
    for (int i = 1; i <= n + 1; i++) fac[i] = fac[i - 1] * F::Z(i);
    ifac[n + 1] = fac[n + 1].inv();
    for (int i = n + 1; i > 0; i--) ifac[i - 1] = ifac[i] * F::Z(i);
    F::Poly d(n + 1); // (e^x - 1)/x = sum x^k/(k+1)!
    for (int k = 0; k <= n; k++) d[k] = ifac[k + 1];
    auto b = F::inverse(d, n + 1);
    for (int k = 0; k <= n; k++) b[k] = b[k] * fac[k];
    return b;
}
// END bernoulli
