#pragma once
#include "number_theory.hpp"

// BEGIN Euler_Phi
inline unsigned long long Euler_Phi(unsigned long long n)
{
    assert(n >= 1);
    unsigned long long answer = n;
    for ( unsigned long long p = 2; p <= n / p; p++ )
        if ( n % p == 0 )
        {
            answer = answer / p * (p - 1);
            while ( n % p == 0 )
                n /= p;
        }
    if ( n > 1 )
        answer = answer / n * (n - 1);
    return answer;
}

inline unsigned long long Euler_Phi(unsigned long long n, Pollard_Rho &solver)
{
    assert(n >= 1);
    auto factors = solver.Factor(n);
    unsigned long long answer = n;
    unsigned long long previous = 0;
    for ( auto p : factors )
        if ( p != previous )
        {
            answer = answer / p * (p - 1);
            previous = p;
        }
    return answer;
}

// END Euler_Phi
