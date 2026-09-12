#pragma once
#include "number_theory.hpp"

// BEGIN Root_Factors
inline vector<tuple<long long, int, long long>> Root_Factors(long long mod,
                                                             Pollard_Rho &rho)
{
    assert(mod >= 1 && mod <= 1000000000000LL);
    auto primes = rho.Factor(mod);
    vector<tuple<long long, int, long long>> answer;
    for ( int i = 0; i < (int)primes.size(); )
    {
        long long p = primes[i], power = 1;
        int e = 0;
        while ( i < (int)primes.size() && primes[i] == (unsigned long long)p )
        {
            power *= p;
            ++e;
            ++i;
        }
        long long g = 0;
        if ( p != 2 )
        {
            long long phi = power / p * (p - 1);
            auto factors = rho.Factor(phi);
            factors.erase(unique(factors.begin(), factors.end()), factors.end());
            auto primitive = [&](long long candidate)
            {
                if ( candidate % p == 0 )
                    return false;
                for ( auto q : factors )
                    if ( Number_Theory::Power(candidate, phi / q, power) == 1 )
                        return false;
                return true;
            };
            g = 2;
            while ( !primitive(g) )
                ++g;
        }
        answer.push_back({p, e, g});
    }
    return answer;
}

// END Root_Factors
