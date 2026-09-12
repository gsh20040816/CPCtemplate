#pragma once
#include "number_theory.hpp"

// BEGIN root_factors
inline vector<tuple<long long, int, long long>> root_factors(long long mod,
                                                             PollardRho &rho)
{
    assert(mod >= 1 && mod <= 1000000000000LL);
    auto primes = rho.factor(mod);
    vector<tuple<long long, int, long long>> answer;
    for (int i = 0; i < (int)primes.size();)
    {
        long long p = primes[i], power = 1;
        int e = 0;
        while (i < (int)primes.size() && primes[i] == (unsigned long long)p)
        {
            power *= p;
            ++e;
            ++i;
        }
        long long g = 0;
        if (p != 2)
        {
            long long phi = power / p * (p - 1);
            auto factors = rho.factor(phi);
            factors.erase(unique(factors.begin(), factors.end()), factors.end());
            auto primitive = [&](long long candidate)
            {
                if (candidate % p == 0)
                    return false;
                for (auto q : factors)
                    if (NumberTheory::power(candidate, phi / q, power) == 1)
                        return false;
                return true;
            };
            g = 2;
            while (!primitive(g))
                ++g;
        }
        answer.push_back({p, e, g});
    }
    return answer;
}

// END root_factors
