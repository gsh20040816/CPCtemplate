#pragma once
#include <cassert>
#include <vector>
using namespace std;

// BEGIN Partitions
struct Partitions
{
    int mod;
    vector<int> p;

    Partitions(int n, int mod) : mod(mod), p(n + 1)
    {
        assert(n >= 0 && mod >= 1);
        p[0] = 1 % mod;
        for (int i = 1; i <= n; i++)
        {
            long long value = 0;
            for (long long j = 1; j * (3 * j - 1) / 2 <= i; j++)
            {
                long long a = j * (3 * j - 1) / 2;
                long long b = j * (3 * j + 1) / 2;
                int sign = j % 2 ? 1 : -1;
                value += 1LL * sign * p[i - a];
                if (b <= i)
                    value += 1LL * sign * p[i - b];
            }
            p[i] = (value % mod + mod) % mod;
        }
    }

    int limited(int n, int k) const
    {
        assert(0 <= n && n < (int)p.size() && k >= 0);
        long long step = 1LL + k;
        long long value = p[n];
        for (long long j = 1; j * (3 * j - 1) / 2 <= n / step; j++)
        {
            long long a = step * (j * (3 * j - 1) / 2);
            long long b = step * (j * (3 * j + 1) / 2);
            int sign = j % 2 ? -1 : 1;
            value += 1LL * sign * p[n - a];
            if (b <= n)
                value += 1LL * sign * p[n - b];
        }
        return (value % mod + mod) % mod;
    }
};

// END Partitions
