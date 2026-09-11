#pragma once
#include "data_structure.hpp"

// BEGIN Basis_Intersection
inline Xor_Basis Basis_Intersection(const Xor_Basis &a, const Xor_Basis &b)
{
    using U = unsigned long long;
    U pivot[64], from_b[64]{};
    copy(a.base, a.base + 64, pivot);
    Xor_Basis result;
    for ( U value : b.base )
    {
        U x = value, part = value;
        for ( int i = 63; i >= 0 && x; i-- )
            if ( x >> i & 1 )
            {
                if ( !pivot[i] )
                {
                    pivot[i] = x;
                    from_b[i] = part;
                    break;
                }
                x ^= pivot[i];
                part ^= from_b[i];
            }
        if ( !x && part )
            result.Insert(part);
    }
    return result;
}

// END Basis_Intersection

// BEGIN Basis_Sum_Intersection
// Return independent generators of (sum space, intersection space).
inline pair<Xor_Basis, Xor_Basis> Basis_Sum_Intersection(const Xor_Basis &a,
                                                         const Xor_Basis &b)
{
    using W = __uint128_t;
    W pivot[128]{};
    auto insert = [&](W x)
    {
        for ( int i = 127; i >= 0 && x; i-- )
            if ( x >> i & 1 )
            {
                if ( !pivot[i] )
                {
                    pivot[i] = x;
                    return;
                }
                x ^= pivot[i];
            }
    };
    for ( auto x : a.base )
        insert((W(x) << 64) | x);
    for ( auto x : b.base )
        insert(W(x) << 64);
    Xor_Basis sum, intersection;
    for ( int i = 0; i < 128; i++ )
        if ( pivot[i] )
        {
            if ( i < 64 )
                intersection.Insert((unsigned long long)pivot[i]);
            else
                sum.Insert((unsigned long long)(pivot[i] >> 64));
        }
    return {sum, intersection};
}

// END Basis_Sum_Intersection
