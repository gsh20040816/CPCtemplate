#include <bits/stdc++.h>
using namespace std;
using i64 = long long;
#include "fixtures/wida_qpow/main.cpp"

static i64 ref_mul(i64 a, i64 b, i64 p)
{
    return i64(__int128(a) * b % p);
}

static i64 ref_pow(i64 a, i64 b, i64 p)
{
    i64 res = p == 1 ? 0 : 1;
    a %= p;
    if (a < 0) a += p;
    while (b)
    {
        if (b & 1) res = ref_mul(res, a, p);
        a = ref_mul(a, a, p);
        b >>= 1;
    }
    return res;
}

int main()
{
    mt19937_64 rng(11);
    int small = 0, mul_bad = 0, pow_bad = 0;
    i64 bad_a = 0, bad_b = 0, bad_p = 0, bad_got = 0, bad_expect = 0;
    for (int a = 0; a < 20; a++)
        for (int b = 0; b < 20; b++)
            for (int p : {1, 2, 3, 7, 97, 1000000007})
            {
                int got = power(a, (i64)b, p);
                int expect = (int)ref_pow(a, b, p);
                if (got != expect) small++;
            }
    for (int i = 0; i < 20000; i++)
    {
        i64 p = (rng() % 1000000000000LL) + 2;
        i64 a = rng() % p;
        i64 b = rng() % p;
        i64 got = mul(a, b, p);
        i64 expect = ref_mul(a, b, p);
        if (got != expect)
        {
            if (!mul_bad)
            {
                bad_a = a;
                bad_b = b;
                bad_p = p;
                bad_got = got;
                bad_expect = expect;
            }
            mul_bad++;
        }
        if (i < 200)
        {
            i64 e = rng() % 30;
            if (power(a, e, p) != ref_pow(a, e, p)) pow_bad++;
        }
    }
    cout << small << ' ' << mul_bad << ' ' << pow_bad << '\n';
    cout << bad_a << ' ' << bad_b << ' ' << bad_p << ' ' << bad_got << ' ' << bad_expect << '\n';
    cout << power(5, (i64)0, 1) << ' ' << power((i64)5, (i64)0, (i64)1) << '\n';
}
