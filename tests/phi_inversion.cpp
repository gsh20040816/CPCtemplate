#include "../src/compact/number_theory.hpp"
#include "../src/classic/number_theory.hpp"
#include <cassert>
#include <iostream>

int main()
{
    const int n = 1000000;
    LinearSieve a(n);
    Linear_Sieve b(n);
    vector<long long> inverse(n+1);
    vector<long long> subtract(n+1);
    iota(subtract.begin(),subtract.end(),0LL);
    for (int d = 1; d <= n; d++)
    {
        for (int x = d; x <= n; x += d)
            inverse[x] += 1LL * a.mu[d] * (x/d);
        // Equivalent to the reference's subtraction of all proper divisors,
        // with contributions propagated forward rather than storing divisor lists.
        for (int x = d+d; x <= n; x += d)
            subtract[x] -= subtract[d];
    }
    for (int x = 1; x <= n; x++)
    {
        assert(inverse[x] == a.phi[x]);
        assert(subtract[x] == a.phi[x]);
        assert(b.phi[x] == a.phi[x]);
        assert(b.mu[x] == a.mu[x]);
    }
    cout << "Phi inversion dual million-entry Mobius convolution and proper-divisor subtraction certificates PASS\n";
}
