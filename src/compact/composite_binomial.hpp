#pragma once
#include <cassert>
#include <climits>
#include <utility>
#include <vector>
using namespace std;

// BEGIN CompositeBinomial
struct CompositeBinomial
{
    struct Factor
    {
        int p, q, crt;
        vector<int> fac, ifac, exponent, powers;
    };

    int limit, mod;
    vector<Factor> factors;

    static long long power(long long a, int e, int m)
    {
        long long result = 1;
        while (e)
        {
            if (e & 1)
                result = result * a % m;
            a = a * a % m;
            e >>= 1;
        }
        return result;
    }

    CompositeBinomial(int n, int m) : limit(n), mod(m)
    {
        assert(n >= 0 && n < INT_MAX && m >= 1);
        int rest = m;
        for (int p = 2; p <= rest / p; p++)
        {
            if (rest % p != 0)
                continue;
            int q = 1;
            do
            {
                rest /= p;
                q *= p;
            } while (rest % p == 0);
            add_factor(p, q);
        }
        if (rest > 1)
            add_factor(rest, rest);
    }

    void add_factor(int p, int q)
    {
        int phi = q - q / p;
        int crt = (mod / q) * power(mod / q % q, phi - 1, q) % mod;
        Factor f{p, q, crt, vector<int>(limit + 1, 1),
                 vector<int>(limit + 1, 1), vector<int>(limit + 1), {}};
        for (long long x = 1; x < q; x *= p)
            f.powers.push_back(x);
        for (int i = 1; i <= limit; i++)
        {
            int x = i;
            f.exponent[i] = f.exponent[i - 1];
            while (x % p == 0)
            {
                x /= p;
                f.exponent[i]++;
            }
            f.fac[i] = 1LL * f.fac[i - 1] * x % q;
        }
        f.ifac[limit] = power(f.fac[limit], phi - 1, q);
        for (int i = limit; i >= 1; i--)
        {
            int x = i;
            while (x % p == 0)
                x /= p;
            f.ifac[i - 1] = 1LL * f.ifac[i] * x % q;
        }
        factors.push_back(move(f));
    }

    int choose(int n, int k) const
    {
        if (n < 0 || k < 0 || k > n)
            return 0;
        assert(n <= limit);
        long long answer = 0;
        for (const auto &f : factors)
        {
            int e = f.exponent[n] - f.exponent[k] - f.exponent[n - k];
            if (e >= int(f.powers.size()))
                continue;
            long long residue = 1LL * f.fac[n] * f.ifac[k] % f.q;
            residue = residue * f.ifac[n - k] % f.q;
            residue = residue * f.powers[e] % f.q;
            answer = (answer + residue * f.crt) % mod;
        }
        return answer;
    }
};
// END CompositeBinomial
