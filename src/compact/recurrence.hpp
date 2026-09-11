#pragma once
#include <cassert>
#include <vector>
using namespace std;

// BEGIN berlekamp_massey
// Prime p; normalized input. s[i] = sum(c[j-1] * s[i-j]), i >= c.size().
vector<int> berlekamp_massey(const vector<int> &s, int p = 998244353)
{
    assert(p >= 2);
    vector<int> c{1}, b{1};
    int len = 0, shift = 1, last = 1;
    for (int i = 0; i < (int)s.size(); i++)
    {
        assert(0 <= s[i] && s[i] < p);
        long long d = s[i];
        for (int j = 1; j <= len; j++)
            d = (d + 1LL * c[j] * s[i - j]) % p;
        if (d == 0)
        {
            shift++;
            continue;
        }
        long long inv = 1, x = last;
        for (int e = p - 2; e; e >>= 1)
        {
            if (e & 1)
                inv = inv * x % p;
            x = x * x % p;
        }
        long long factor = d * inv % p;
        auto old = c;
        if (c.size() < b.size() + shift)
            c.resize(b.size() + shift);
        for (int j = 0; j < (int)b.size(); j++)
            c[j + shift] = (c[j + shift] - factor * b[j] % p + p) % p;
        if (2 * len <= i)
        {
            len = i + 1 - len;
            b = old;
            last = d;
            shift = 1;
        }
        else
            shift++;
    }
    c.resize(len + 1);
    c.erase(c.begin());
    for (int &x : c)
        x = x == 0 ? 0 : p - x;
    return c;
}

// END berlekamp_massey

// BEGIN recurrence_nth
// init has exactly k entries; c[j-1] multiplies a[n-j]. Modulus need not be prime.
int recurrence_nth(const vector<int> &init,
                   const vector<int> &c,
                   unsigned long long n,
                   int p = 998244353)
{
    assert(p >= 2 && init.size() == c.size());
    int k = c.size();
    if (!k)
        return 0;
    for (int x : init)
        assert(0 <= x && x < p);
    for (int x : c)
        assert(0 <= x && x < p);
    if (n < (unsigned)k)
        return init[n];
    auto multiply = [&](const vector<int> &a, const vector<int> &b)
    {
        vector<int> t(2 * k - 1);
        for (int i = 0; i < k; i++)
        {
            for (int j = 0; j < k; j++)
                t[i + j] = (t[i + j] + 1LL * a[i] * b[j]) % p;
        }
        for (int i = 2 * k - 2; i >= k; i--)
        {
            for (int j = 1; j <= k; j++)
                t[i - j] = (t[i - j] + 1LL * t[i] * c[j - 1]) % p;
        }
        t.resize(k);
        return t;
    };
    vector<int> answer(k), x(k);
    answer[0] = 1;
    if (k == 1)
        x[0] = c[0];
    else
        x[1] = 1;
    while (n)
    {
        if (n & 1)
            answer = multiply(answer, x);
        x = multiply(x, x);
        n >>= 1;
    }
    long long value = 0;
    for (int i = 0; i < k; i++)
        value = (value + 1LL * answer[i] * init[i]) % p;
    return value;
}

// END recurrence_nth
