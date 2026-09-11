#include "../src/compact/recurrence.hpp"
#include "../src/classic/recurrence.hpp"
#include <algorithm>
#include <iostream>
#include <random>

bool fits(const std::vector<int> &s, const std::vector<int> &c, int p)
{
    for (int i = c.size(); i < (int)s.size(); i++)
    {
        long long v = 0;
        for (int j = 0; j < (int)c.size(); j++)
            v = (v + 1LL * c[j] * s[i - j - 1]) % p;
        if (v != s[i])
            return false;
    }
    return true;
}

int minimum_order(const std::vector<int> &s, int p)
{
    int possibilities = 1;
    for (int k = 0; k <= (int)s.size(); k++)
    {
        for (int mask = 0; mask < possibilities; mask++)
        {
            int code = mask;
            std::vector<int> c(k);
            for (int &x : c)
            {
                x = code % p;
                code /= p;
            }
            if (fits(s, c, p))
                return k;
        }
        possibilities *= p;
    }
    std::abort();
}

using Matrix = std::vector<std::vector<int>>;
Matrix mul(const Matrix &a, const Matrix &b, int p)
{
    int n = a.size();
    Matrix c(n, std::vector<int>(n));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            for (int k = 0; k < n; k++)
                c[i][j] = (c[i][j] + 1LL * a[i][k] * b[k][j]) % p;
    return c;
}

int matrix_nth(const std::vector<int> &s, const std::vector<int> &c,
               unsigned long long index, int p)
{
    int n = c.size();
    if (index < s.size())
        return s[index];
    Matrix a(n, std::vector<int>(n)), r = a;
    a[0] = c;
    for (int i = 1; i < n; i++)
        a[i][i - 1] = 1;
    for (int i = 0; i < n; i++)
        r[i][i] = 1;
    index -= n - 1;
    while (index)
    {
        if (index & 1)
            r = mul(r, a, p);
        a = mul(a, a, p);
        index >>= 1;
    }
    long long answer = 0;
    for (int i = 0; i < n; i++)
        answer = (answer + 1LL * r[0][i] * s[n - 1 - i]) % p;
    return answer;
}

int main()
{
    for (int p : {2, 3})
    {
        int possibilities = 1;
        for (int n = 0; n <= 8; n++)
        {
            for (int mask = 0; mask < possibilities; mask++)
            {
                int code = mask;
                std::vector<int> s(n);
                for (int &x : s)
                {
                    x = code % p;
                    code /= p;
                }
                auto a = berlekamp_massey(s, p);
                auto b = Berlekamp_Massey(s, p);
                int k = minimum_order(s, p);
                assert((int)a.size() == k && (int)b.size() == k);
                assert(fits(s, a, p) && fits(s, b, p));
            }
            possibilities *= p;
        }
    }
    std::mt19937_64 rng(867813);
    for (int p : {2, 3, 998244353, 2147483647})
    {
        for (int trial = 0; trial < 200; trial++)
        {
            int k = 1 + rng() % 12;
            std::vector<int> c(k), s(k);
            for (int &x : c)
                x = rng() % p;
            for (int &x : s)
                x = rng() % p;
            for (int i = k; i < 100; i++)
            {
                long long v = 0;
                for (int j = 0; j < k; j++)
                    v = (v + 1LL * c[j] * s[i - j - 1]) % p;
                s.push_back(v);
            }
            std::vector<int> prefix(s.begin(), s.begin() + 2 * k);
            auto a = berlekamp_massey(prefix, p);
            auto b = Berlekamp_Massey(prefix, p);
            assert(fits(s, a, p) && fits(s, b, p));
            std::vector<int> ia(s.begin(), s.begin() + a.size());
            std::vector<int> ib(s.begin(), s.begin() + b.size());
            for (int index = 0; index < 100; index++)
            {
                assert(recurrence_nth(ia, a, index, p) == s[index]);
                assert(Recurrence_Nth(ib, b, index, p) == s[index]);
            }
        }
    }
    for (int p : {2, 12, 998244353, 2147483647})
    {
        for (int trial = 0; trial < 200; trial++)
        {
            int k = 1 + rng() % 5;
            std::vector<int> c(k), s(k);
            for (int &x : c)
                x = rng() % p;
            for (int &x : s)
                x = rng() % p;
            unsigned long long index = trial % 2 ? rng() : ~0ULL;
            int expected = matrix_nth(s, c, index, p);
            assert(recurrence_nth(s, c, index, p) == expected);
            assert(Recurrence_Nth(s, c, index, p) == expected);
        }
    }
    assert(recurrence_nth({}, {}, ~0ULL) == 0);
    assert(Recurrence_Nth({}, {}, ~0ULL) == 0);
    std::cout << "BM exhaustive minimality, recurrence holdout and uint64 matrix oracle PASS\n";
}
