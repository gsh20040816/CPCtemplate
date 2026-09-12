#pragma once
#include "number_theory.hpp"

// BEGIN Garner
// Pairwise coprime positive moduli. Digits use the input order.
inline vector<long long> Garner_Digits(const vector<long long> &b,
                                       const vector<long long> &moduli)
{
    using ll = long long;
    using i128 = __int128_t;
    int n = b.size();
    assert(moduli.size() == b.size());
    vector<ll> value(n), coefficient(n, 1), digit(n);
    for ( ll m : moduli )
        assert(m > 0);
    for ( int i = 0; i < n; i++ )
    {
        ll m = moduli[i];
        ll inverse = Number_Theory::Inverse(coefficient[i], m);
        if ( inverse == -1 )
            throw invalid_argument("Garner moduli are not coprime");
        i128 delta = (i128(b[i]) - value[i]) % m;
        if ( delta < 0 )
            delta += m;
        digit[i] = delta * inverse % m;
        for ( int j = i + 1; j < n; j++ )
        {
            value[j] = (value[j] + i128(coefficient[j]) * digit[i]) % moduli[j];
            coefficient[j] = i128(coefficient[j]) * m % moduli[j];
        }
    }
    return digit;
}

// Return the least nonnegative CRT solution modulo target, not all solutions.
inline long long
Garner(const vector<long long> &b, const vector<long long> &moduli, long long target)
{
    assert(target > 0);
    auto digit = Garner_Digits(b, moduli);
    long long answer = 0;
    for ( int i = (int)digit.size() - 1; i >= 0; i-- )
        answer = (__int128_t(answer) * moduli[i] + digit[i]) % target;
    return answer;
}

// END Garner
