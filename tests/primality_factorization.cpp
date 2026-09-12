#include "../src/compact/number_theory.hpp"
#include "../src/classic/number_theory.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <cassert>
#include <iostream>
using boost::multiprecision::cpp_int;
using ull = unsigned long long;

bool trial(ull n)
{
    if (n < 2)
        return false;
    for (ull d = 2; d <= n / d; d++)
        if (n % d == 0)
            return false;
    return true;
}

void factor_case(vector<ull> factors)
{
    sort(factors.begin(), factors.end());
    cpp_int product = 1;
    for (ull p : factors)
    {
        assert(p <= 4294967295ULL && trial(p));
        product *= p;
    }
    assert(product <= cpp_int(ULLONG_MAX));
    ull n = product.convert_to<ull>();
    assert(NumberTheory::prime(n) == (factors.size() == 1));
    assert(Number_Theory::Prime(n) == (factors.size() == 1));
    for (ull seed : {0ULL, 1ULL, 712367821ULL})
    {
        PollardRho a(seed);
        Pollard_Rho b(seed);
        assert(a.factor(n) == factors);
        assert(b.Factor(n) == factors);
    }
}

int main()
{
    const int n = 1000000;
    vector<bool> composite(n + 1);
    composite[0] = composite[1] = true;
    for (int p = 2; p <= n / p; p++)
        if (!composite[p])
            for (int j = p * p; j <= n; j += p)
                composite[j] = true;
    for (int x = 0; x <= n; x++)
    {
        assert(NumberTheory::prime(x) == !composite[x]);
        assert(Number_Theory::Prime(x) == !composite[x]);
    }
    mt19937_64 rng(4718);
    for (int i = 0; i < 1000; i++)
    {
        ull a = rng(), b = rng(), m = rng() | 1;
        ull product = (cpp_int(a) * b % m).convert_to<ull>();
        ull power = boost::multiprecision::powm(cpp_int(a), cpp_int(b), cpp_int(m)).convert_to<ull>();
        assert(NumberTheory::mul(a,b,m) == product);
        assert(Number_Theory::Mul(a,b,m) == product);
        assert(NumberTheory::power(a,b,m) == power);
        assert(Number_Theory::Power(a,b,m) == power);
    }
    factor_case({});
    for (int x = 2; x <= 10000; x++)
    {
        int v = x;
        vector<ull> factors;
        for (int d = 2; d <= v / d; d++)
            while (v % d == 0)
            {
                factors.push_back(d);
                v /= d;
            }
        if (v > 1)
            factors.push_back(v);
        factor_case(factors);
    }
    vector<ull> primes = {1000000007ULL, 1000000009ULL, 2147483647ULL, 4294967291ULL};
    for (ull p : primes)
        for (ull q : primes)
            if (p <= q)
                factor_case({p,q});
    factor_case(vector<ull>(63,2));
    factor_case(vector<ull>(40,3));
    factor_case({151,751,28351});
    factor_case({10670053,32010157});
    factor_case({149491,747451,34233211});
    factor_case({3,5,17,257,641,65537,6700417});
    // Lucas primality certificate for 2^61-1: complete trial-verified factorization of p-1.
    ull p = (1ULL << 61) - 1;
    vector<ull> fs = {2,3,3,5,5,7,11,13,31,41,61,151,331,1321};
    cpp_int product = 1;
    for (ull q : fs)
    {
        assert(trial(q));
        product *= q;
    }
    assert(product == p - 1);
    bool certified = false;
    for (ull a = 2; a < 100; a++)
    {
        if (boost::multiprecision::powm(cpp_int(a), cpp_int(p-1), cpp_int(p)) != 1)
            continue;
        bool ok = true;
        for (ull q : fs)
            if (boost::multiprecision::powm(cpp_int(a), cpp_int((p-1)/q), cpp_int(p)) == 1)
                ok = false;
        if (ok)
        {
            certified = true;
            break;
        }
    }
    assert(certified);
    assert(NumberTheory::prime(p) && Number_Theory::Prime(p));
    assert(PollardRho().factor(p) == vector<ull>{p});
    assert(Pollard_Rho().Factor(p) == vector<ull>{p});
    cout << "Primality/factorization dual sieve, cpp_int arithmetic, trial-certified factors, pseudoprimes, uint64 bounds and Lucas certificate PASS\n";
}
