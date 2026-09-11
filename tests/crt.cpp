#include "../src/compact/number_theory.hpp"
#include "../src/classic/number_theory.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <random>
using boost::multiprecision::cpp_int;

cpp_int norm(cpp_int a, const cpp_int &m)
{
    a %= m;
    if (a < 0)
        a += m;
    return a;
}

void check(long long r, long long m, long long b, long long n)
{
    cpp_int a = m, c = n, x = 1, y = 0;
    while (c != 0)
    {
        cpp_int q = a / c, next = a - q * c;
        a = c;
        c = next;
        next = x - q * y;
        x = y;
        y = next;
    }
    cpp_int R = norm(r, cpp_int(m)), B = norm(b, cpp_int(n));
    cpp_int diff = B - R, modulus = cpp_int(m) * (cpp_int(n) / a);
    bool exists = diff % a == 0;
    cpp_int result = 0;
    if (exists)
        result = norm(R + cpp_int(m) * norm(diff / a * x, cpp_int(n) / a), modulus);
    for (int style = 0; style < 2; style++)
    {
        long long rr = r, mm = m;
        bool overflow = false, ok = false;
        try
        {
            ok = style ? Number_Theory::Crt(rr, mm, b, n) : NumberTheory::crt(rr, mm, b, n);
        }
        catch (const overflow_error &)
        {
            overflow = true;
        }
        assert(overflow == (exists && modulus > LLONG_MAX));
        if (overflow || !exists)
            assert(mm == m && cpp_int(rr) == R);
        else
            assert(ok && cpp_int(rr) == result && cpp_int(mm) == modulus);
        if (!exists)
            assert(!ok);
    }
}

int main()
{
    for (long long m = 1; m <= 20; m++)
        for (long long n = 1; n <= 20; n++)
            for (long long r = 0; r < m; r++)
                for (long long b = 0; b < n; b++)
                {
                    long long expected = -1, period = lcm(m, n);
                    for (long long x = 0; x < period; x++)
                        if (x % m == r && x % n == b)
                        {
                            expected = x;
                            break;
                        }
                    long long rr = r - 3 * m, mm = m;
                    bool ok = NumberTheory::crt(rr, mm, b + 2 * n, n);
                    assert(ok == (expected != -1));
                    if (ok)
                        assert(rr == expected && mm == period);
                    check(r - 3 * m, m, b + 2 * n, n);
                }
    mt19937_64 rng(4777);
    for (int i = 0; i < 15000; i++)
    {
        long long m = i % 2 ? rng() % uint64_t(LLONG_MAX) + 1 : rng() % 1000000 + 1;
        long long n = i % 2 ? rng() % uint64_t(LLONG_MAX) + 1 : rng() % 1000000 + 1;
        check(bit_cast<long long>(rng()), m, bit_cast<long long>(rng()), n);
    }
    for (long long r : {LLONG_MIN, -1LL, 0LL, 1LL, LLONG_MAX})
    {
        check(r, LLONG_MAX, r, 1);
        check(r, LLONG_MAX, r, 2);
        check(r, LLONG_MAX - 1, r, 2);
        check(r, LLONG_MAX, r, LLONG_MAX);
    }
    check(0, LLONG_MAX - 1, 1, LLONG_MAX - 3);
    cout << "CRT dual exhaustive residue oracle, cpp_int reference, signed extremes, inconsistency and modulus overflow PASS\n";
}
