#include <bits/stdc++.h>
#include <cassert>
#include "fixtures/wida_mod_reduction/07D.cpp"
#include "../src/compact/primitive_root.hpp"
#include "../src/compact/modular_sqrt.hpp"
using namespace std;
long long checks = 0;
void require(bool ok)
{
    if (!ok)
        throw runtime_error("07D helper mismatch");
    checks++;
}
template <uint32_t P> void check_prime()
{
    using Old = MontgomeryModInt32<P>;
    uint32_t g = Old::get_pr();
    vector<bool> seen(P);
    uint64_t x = 1;
    for (uint32_t i = 1; i < P; i++)
    {
        require(!seen[x]);
        seen[x] = true;
        x = x * g % P;
    }
    require(x == 1 && g == uint32_t(PrimitiveRoot(P).minimum()));
    vector<vector<long long>> roots(P);
    for (uint64_t a = 0; a < P; a++)
        roots[a * a % P].push_back(a);
    for (uint32_t a = 0; a < P; a++)
    {
        auto r = sqrt(Old(a)).get();
        require(roots[a].empty() ? r == 0 : uint64_t(r) * r % P == a);
        require(mod_sqrt(a, P) == roots[a]);
    }
}
int main()
{
    check_prime<3>();
    check_prime<5>();
    check_prime<7>();
    check_prime<17>();
    check_prime<41>();
    check_prime<97>();
    check_prime<257>();
    check_prime<1009>();
    for (int k = 0; k <= 63; k++)
    {
        uint64_t n = uint64_t(1) << k;
        require(get_len(n) == n);
        if (n > 2)
            require(get_len(n - 1) == n);
        if (k < 63)
            require(get_len(n + 1) == 2 * n);
    }
    // Original says n=0 is invalid; upper overflow is a separate bound.
    require(get_len((uint64_t(1) << 63) + 1) == 0);
    cout << checks << " source-helper checks; overflow above 2^63 confirmed\n";
}
