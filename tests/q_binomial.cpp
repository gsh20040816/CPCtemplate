#include <bits/stdc++.h>
#include <cassert>
#include "../src/compact/q_binomial.hpp"
using namespace std;
namespace raw
{
#include "fixtures/wida_q_binomial/13B.cpp"
}
int main()
{
    long long checks = 0;
    for (int p : {2, 3, 5, 7, 11, 17, 31, 43})
        for (int q = 0; q < p; q++)
        {
            vector<int> dp(62);
            dp[0] = 1;
            for (int n = 0; n <= 60; n++)
            {
                for (int k = 0; k <= n + 1; k++)
                {
                    int want = k <= n ? dp[k] : 0;
                    assert(q_binomial(n, k, q, p) == want);
                    assert(q_binomial(n, k, q - p, p) == want);
                    if (k <= n)
                    {
                        int got = raw::qBinomial(n, k, q, p);
                        assert((got % p + p) % p == want);
                        checks++;
                    }
                    checks += 2;
                }
                int power = 1;
                for (int k = n + 1; k >= 1; k--)
                {
                    dp[k] = (dp[k] + 1LL * power * dp[k - 1]) % p;
                    power = 1LL * power * q % p;
                }
            }
        }
    for (int p : {2, 3, 97, 998244353, 2147483647})
        for (int q : {INT_MIN, -1, 0, 1, 2, INT_MAX})
        {
            auto n = ULLONG_MAX;
            assert(q_binomial(n, 0, q, p) == 1);
            assert(q_binomial(n, n, q, p) == 1);
            assert(q_binomial(0, n, q, p) == 0);
            checks += 3;
        }
    cout << checks << " recurrence/source/boundary checks PASS\n";
}
