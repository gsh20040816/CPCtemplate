#include <bits/stdc++.h>
#include <cassert>
using namespace std;
struct LinearSieve
{
    vector<int> prime, lp, phi, mu;

    LinearSieve(int n) : lp(n + 1), phi(n + 1), mu(n + 1)
    {
        if (n) phi[1] = mu[1] = 1;
        for (int i = 2; i <= n; i++)
        {
            if (!lp[i])
            {
                lp[i] = i;
                prime.push_back(i);
                phi[i] = i - 1;
                mu[i] = -1;
            }
            for (int p : prime)
            {
                if (p > n / i) break;
                int j = i * p;
                lp[j] = p;
                if (i % p == 0)
                {
                    phi[j] = phi[i] * p;
                    mu[j] = 0;
                    break;
                }
                phi[j] = phi[i] * (p - 1);
                mu[j] = -mu[i];
            }
        }
    }
};

struct CoprimePairs
{
    vector<int> sum;

    CoprimePairs(int n) : sum(LinearSieve(n).mu)
    {
        for (int i = 1; i <= n; i++) sum[i] += sum[i - 1];
    }

    long long count(int a, int b) const
    {
        assert(a >= 0 && b >= 0 && min(a, b) < (int)sum.size());
        __int128_t answer = 0;
        for (int l = 1, r; l <= min(a, b); l = r + 1)
        {
            int x = a / l;
            int y = b / l;
            r = min(a / x, b / y);
            answer += __int128_t(sum[r] - sum[l - 1]) * x * y;
        }
        return (long long)answer;
    }

    long long rectangle(int a, int b, int c, int d, int k) const
    {
        assert(1 <= a && a <= b && 1 <= c && c <= d && k >= 1);
        return count(b / k, d / k) - count((a - 1) / k, d / k) -
               count(b / k, (c - 1) / k) + count((a - 1) / k, (c - 1) / k);
    }
};

int main()
{
    CoprimePairs solver(50000);
    int t;
    scanf("%d", &t);
    while (t--)
    {
        int a, b, c, d, k;
        scanf("%d%d%d%d%d", &a, &b, &c, &d, &k);
        printf("%lld\n", solver.rectangle(a, b, c, d, k));
    }
    return 0;
}
