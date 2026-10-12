#pragma once
#include <vector>
using namespace std;

struct XorAffine64
{
    using U = unsigned long long;
    vector<U> col;
    U bias = 0;

    XorAffine64(bool identity = false) : col(64)
    {
        if (identity)
            for (int i = 0; i < 64; i++)
                col[i] = 1ULL << i;
    }

    U linear(U x) const
    {
        U result = 0;
        while (x)
        {
            int bit = __builtin_ctzll(x);
            result ^= col[bit];
            x &= x - 1;
        }
        return result;
    }

    U apply(U x) const
    {
        return linear(x) ^ bias;
    }

    XorAffine64 then(const XorAffine64 &g) const
    {
        XorAffine64 result;
        for (int i = 0; i < 64; i++)
            result.col[i] = g.linear(col[i]);
        result.bias = g.apply(bias);
        return result;
    }

    XorAffine64 power(U exponent) const
    {
        XorAffine64 result(true), base = *this;
        while (exponent)
        {
            if (exponent & 1)
                result = result.then(base);
            base = base.then(base);
            exponent >>= 1;
        }
        return result;
    }
};
