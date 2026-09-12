#pragma once
#include "number_theory.hpp"

// BEGIN Coprime_Pairs
struct Coprime_Pairs
{
    vector<int> sum;

    Coprime_Pairs(int n) : sum(Linear_Sieve(n).mu)
    {
        for ( int i = 1; i <= n; i++ )
            sum[i] += sum[i - 1];
    }

    long long Count(int a, int b) const
    {
        assert(a >= 0 && b >= 0 && min(a, b) < (int)sum.size());
        __int128_t answer = 0;
        for ( int l = 1, r; l <= min(a, b); l = r + 1 )
        {
            int x = a / l;
            int y = b / l;
            r = min(a / x, b / y);
            answer += __int128_t(sum[r] - sum[l - 1]) * x * y;
        }
        return (long long)answer;
    }

    long long Rectangle(int a, int b, int c, int d, int k) const
    {
        assert(1 <= a && a <= b && 1 <= c && c <= d && k >= 1);
        return Count(b / k, d / k) - Count((a - 1) / k, d / k) -
               Count(b / k, (c - 1) / k) + Count((a - 1) / k, (c - 1) / k);
    }
};

// END Coprime_Pairs
