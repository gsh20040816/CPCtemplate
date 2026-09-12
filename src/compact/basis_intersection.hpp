#pragma once
#include "data_structure.hpp"

// BEGIN basis_intersection
inline XorBasis basis_intersection(const XorBasis &a, const XorBasis &b)
{
    using U = unsigned long long;
    U pivot[64], from_b[64]{};
    copy(a.a, a.a + 64, pivot);
    XorBasis result;
    for (U value : b.a)
    {
        U x = value, part = value;
        for (int i = 63; i >= 0 && x; i--)
            if (x >> i & 1)
            {
                if (!pivot[i])
                {
                    pivot[i] = x;
                    from_b[i] = part;
                    break;
                }
                x ^= pivot[i];
                part ^= from_b[i];
            }
        if (!x && part) result.insert(part);
    }
    return result;
}

// END basis_intersection

// BEGIN basis_sum_intersection
// Return independent generators of (sum space, intersection space).
inline pair<XorBasis, XorBasis> basis_sum_intersection(const XorBasis &a,
                                                       const XorBasis &b)
{
    using W = __uint128_t;
    W pivot[128]{};
    auto insert = [&](W x)
    {
        for (int i = 127; i >= 0 && x; i--)
            if (x >> i & 1)
            {
                if (!pivot[i])
                {
                    pivot[i] = x;
                    return;
                }
                x ^= pivot[i];
            }
    };
    for (auto x : a.a) insert((W(x) << 64) | x);
    for (auto x : b.a) insert(W(x) << 64);
    XorBasis sum, intersection;
    for (int i = 0; i < 128; i++)
        if (pivot[i])
        {
            if (i < 64)
                intersection.insert((unsigned long long)pivot[i]);
            else
                sum.insert((unsigned long long)(pivot[i] >> 64));
        }
    return {sum, intersection};
}

// END basis_sum_intersection
