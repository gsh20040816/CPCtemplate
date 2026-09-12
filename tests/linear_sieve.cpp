#include "../src/compact/number_theory.hpp"
#include "../src/classic/number_theory.hpp"
#include <cassert>
#include <iostream>
using namespace std;

void check(int n)
{
    LinearSieve a(n);
    Linear_Sieve b(n);
    assert(a.prime == b.Prime && a.lp == b.lp && a.phi == b.phi && a.mu == b.mu);
    assert(a.lp.size() == (size_t)n + 1);
    assert(a.lp[0] == 0 && a.phi[0] == 0 && a.mu[0] == 0);
    vector<long long> sum_phi(n + 1), sum_mu(n + 1);
    for (int d = 1; d <= n; d++)
        for (int x = d; x <= n; x += d)
        {
            sum_phi[x] += a.phi[d];
            sum_mu[x] += a.mu[d];
        }
    vector<int> expected;
    for (int x = 1; x <= n; x++)
    {
        assert(sum_phi[x] == x);
        assert(sum_mu[x] == (x == 1));
        if (x == 1)
        {
            assert(a.lp[x] == 0 && a.phi[x] == 1 && a.mu[x] == 1);
            continue;
        }
        int value = x;
        int previous = 0;
        while (value > 1)
        {
            int p = a.lp[value];
            assert(p >= 2 && value % p == 0 && p >= previous);
            assert(a.lp[p] == p);
            previous = p;
            value /= p;
        }
        if (x <= 20000)
        {
            int p = 2;
            while (p <= x / p && x % p)
                p++;
            int least = p <= x / p ? p : x;
            assert(a.lp[x] == least);
        }
        if (a.lp[x] == x)
            expected.push_back(x);
        if (x <= 500)
        {
            int count = 0;
            for (int k = 1; k <= x; k++)
                count += gcd(k, x) == 1;
            assert(a.phi[x] == count);
        }
    }
    assert(a.prime == expected);
}

int main()
{
    for (int n = 0; n <= 150; n++)
        check(n);
    check(10000000);
    cout << "Linear sieve dual prefixes, least-prime trial oracle, factor reconstruction and ten-million-entry divisor certificates PASS\n";
}
