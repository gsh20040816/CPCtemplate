#pragma once
#include "number_theory.hpp"

// BEGIN Batch_Inverse
inline optional<vector<long long>> Batch_Inverse(vector<long long> a, long long mod)
{
    assert(mod > 0);
    int n = a.size();
    vector<long long> prefix(n + 1, 1 % mod);
    for ( int i = 0; i < n; i++ )
    {
        a[i] %= mod;
        if ( a[i] < 0 )
            a[i] += mod;
        prefix[i + 1] = __int128_t(prefix[i]) * a[i] % mod;
    }
    long long inverse = Number_Theory::Inverse(prefix[n], mod);
    if ( inverse == -1 )
        return nullopt;
    for ( int i = n - 1; i >= 0; i-- )
    {
        long long value = a[i];
        a[i] = __int128_t(inverse) * prefix[i] % mod;
        inverse = __int128_t(inverse) * value % mod;
    }
    return a;
}

// END Batch_Inverse
