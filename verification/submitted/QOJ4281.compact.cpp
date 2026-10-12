#include <bits/stdc++.h>
#include <cassert>
using namespace std;

int q_binomial(unsigned long long n, unsigned long long k, int q, int p)
{
    assert(p >= 2);
    if (k > n)
        return 0;
    q %= p;
    if (q < 0)
        q += p;
    if (q == 0)
        return 1;
    auto power = [&](long long a, unsigned long long e)
    {
        long long r = 1;
        while (e)
        {
            if (e & 1)
                r = r * a % p;
            a = a * a % p;
            e >>= 1;
        }
        return r;
    };

    int order = p - 1, rest = p - 1;
    for (int d = 2; d <= rest / d; d++)
        if (rest % d == 0)
        {
            while (rest % d == 0)
                rest /= d;
            while (order % d == 0 && power(q, order / d) == 1)
                order /= d;
        }
    if (rest > 1)
        while (order % rest == 0 && power(q, order / rest) == 1)
            order /= rest;

    int a = n % order, b = k % order;
    if (b > a)
        return 0;
    b = min(b, a - b);
    long long num = 1, den = 1;
    long long upper = power(q, a), lower = q, invq = power(q, p - 2);
    for (int i = 0; i < b; i++)
    {
        num = num * (upper + p - 1) % p;
        den = den * (lower + p - 1) % p;
        upper = upper * invq % p;
        lower = lower * q % p;
    }

    n /= order;
    k /= order;
    while (n || k)
    {
        int x = n % p, y = k % p;
        if (y > x)
            return 0;
        y = min(y, x - y);
        for (int i = 1; i <= y; i++)
        {
            num = num * (x - i + 1) % p;
            den = den * i % p;
        }
        n /= p;
        k /= p;
    }
    return num * power(den, p - 2) % p;
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q, p;
    unsigned long long n, k;
    cin >> q >> n >> k >> p;
    cout << q_binomial(n, k, q, p) << endl;
}
