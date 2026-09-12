#include "../src/compact/carmichael.hpp"
#include "../src/classic/carmichael.hpp"
#include <cassert>
#include <climits>
#include <iostream>
#include <random>
#include <vector>
using namespace std;

int cycle(int a, int n)
{
    long long x = 1;
    for (int d = 1; d <= n; d++)
    {
        x = x * a % n;
        if (x == 1)
            return d;
    }
    assert(false);
    return 0;
}

long long power(long long a, int e, int n)
{
    long long result = 1;
    while (e)
    {
        if (e & 1)
            result = result * a % n;
        a = a * a % n;
        e /= 2;
    }
    return result;
}

int main()
{
    assert(carmichael(1) == 1 && Carmichael(1) == 1);
    for (int n = 2; n <= 800; n++)
    {
        int expected = 1;
        for (int a = 1; a < n; a++)
            if (gcd(a, n) == 1)
                expected = lcm(expected, cycle(a, n));
        assert(carmichael(n) == expected && Carmichael(n) == expected);
    }
    for (int n : {561, 1105, 1729, 2465, 2821, 6601})
    {
        assert((n - 1) % carmichael(n) == 0);
        for (int a = 1; a < n; a++)
            if (gcd(a, n) == 1)
                assert(power(a, n - 1, n) == 1);
    }
    assert(carmichael(1 << 30) == (1 << 28));
    assert(carmichael(1162261467) == 774840978);
    assert(carmichael(INT_MAX) == INT_MAX - 1);
    mt19937 rng(562);
    for (int it = 0; it < 2500; it++)
    {
        int n = 2 + rng() % (INT_MAX - 1);
        int exponent = carmichael(n);
        assert(exponent > 0 && exponent < n);
        assert(exponent == Carmichael(n));
        for (int j = 0; j < 20; j++)
        {
            int a = 1 + rng() % (n - 1);
            if (gcd(a, n) == 1)
                assert(power(a, exponent, n) == 1);
        }
    }
    // CRT gives an independent composition property, including shared factors.
    for (int a = 1; a <= 100; a++)
        for (int b = 1; b <= 100; b++)
            assert(carmichael(lcm(a, b)) == lcm(carmichael(a), carmichael(b)));
    cout << "Carmichael dual exhaustive unit-order LCM, prime powers, int32 bounds, exponent certificates and composition PASS\n";
}
