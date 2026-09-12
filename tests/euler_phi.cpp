#include "../src/compact/euler_phi.hpp"
#include "../src/classic/euler_phi.hpp"
#include <cassert>
#include <iostream>
using ull = unsigned long long;

int main()
{
    PollardRho a;
    Pollard_Rho b;
    LinearSieve sieve(20000);
    for (int n = 1; n <= 20000; n++)
    {
        ull expected = sieve.phi[n];
        if (n <= 500)
        {
            ull count = 0;
            for (int k = 1; k <= n; k++)
                count += gcd(k,n) == 1;
            assert(expected == count);
        }
        assert(euler_phi(n) == expected);
        assert(Euler_Phi(n) == expected);
        assert(euler_phi(n,a) == expected);
        assert(Euler_Phi(n,b) == expected);
    }
    vector<vector<ull>> lists = {{2,2,2,3,3,5}, vector<ull>(63,2), vector<ull>(40,3),
        {3,5,17,257,641,65537,6700417}, {4294967291ULL,4294967291ULL},
        {1000000007,1000000009}, {2147483647}, {1000003,1000033}};
    for (auto fs : lists)
    {
        sort(fs.begin(),fs.end());
        __uint128_t n = 1;
        ull expected = 1;
        for (int i = 0; i < (int)fs.size(); i++)
        {
            ull p = fs[i];
            for (ull d = 2; d <= p / d; d++)
                assert(p % d);
            n *= p;
            expected *= i && p == fs[i-1] ? p : p-1;
        }
        assert(n <= ULLONG_MAX);
        assert(euler_phi((ull)n,a) == expected);
        assert(Euler_Phi((ull)n,b) == expected);
        if (fs.back() <= 6700417 || fs.size() == 1)
        {
            assert(euler_phi((ull)n) == expected);
            assert(Euler_Phi((ull)n) == expected);
        }
    }
    ull p = (1ULL << 61) - 1;
    assert(euler_phi(p,a) == p-1);
    assert(Euler_Phi(p,b) == p-1);
    cout << "Euler phi dual trial/rho paths, gcd/sieve oracles, repeated primes, uint64 composites and large prime PASS\n";
}
