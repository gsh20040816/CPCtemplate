#include <bits/stdc++.h>
#include <cassert>
#include <boost/multiprecision/cpp_int.hpp>
#include "../src/compact/fraction.hpp"
using namespace std;
using boost::multiprecision::cpp_int;
using F = Rational<>;
using B = Rational<cpp_int, cpp_int>;
namespace raw
{
#include "fixtures/wida_fraction/Frac.cpp"
}

int main()
{
    mt19937_64 rng(1572);
    long long checks = 0;
    for (int i = 0; i < 100000; i++)
    {
        long long an = (long long)(rng() % 2000001) - 1000000;
        long long ad = 1 + rng() % 1000;
        long long bn = (long long)(rng() % 2000001) - 1000000;
        long long bd = 1 + rng() % 1000;
        F a(an, ad), b(bn, bd);
        raw::Frac<long long> x(an, ad), y(bn, bd);
        auto check = [&](F r, raw::Frac<long long> s)
        {
            assert((__int128)r.num * s.den == (__int128)s.num * r.den);
            assert(r.den > 0);
            assert(gcd(r.num, r.den) == 1);
            checks += 3;
        };
        check(a + b, x + y);
        check(a - b, x - y);
        check(a * b, x * y);
        if (bn)
            check(a / b, x / y);
        F c = a;
        c += c;
        assert(c == a + a);
        c = a;
        c -= c;
        assert(c.num == 0 && c.den == 1);
        c = a;
        c *= c;
        assert(c == a * a);
        if (an)
        {
            c = a;
            c /= c;
            assert(c == 1);
        }
        assert((a < b) == (x < y));
        assert((a == b) == (x == y));
        assert((a != b) == (x != y));
        assert((a > b) == (x > y));
        assert((a <= b) == (x <= y));
        assert((a >= b) == (x >= y));
        assert(1 + a == a + 1);
        assert(1 - a == -(a - 1));
        assert(1 * a == a);
        assert((0 < a) == (a > 0));
        checks += 14;
    }
    long long lo = LLONG_MIN, hi = LLONG_MAX;
    assert(F(lo, lo) == 1);
    assert(F(0, lo) == 0);
    assert(F(lo, 2) == F(lo / 2));
    assert(F(lo, hi) < -1);
    assert(F(lo) + F(hi) == -1);
    assert(F(lo) - F(lo) == 0);
    assert(F(hi, hi - 1) * F(hi - 1, hi) == 1);
    assert(F(lo) / F(lo) == 1);
    assert(F(hi, 2) + F(hi, 2) == hi);
    assert(F(lo, 3) + F(1, 3) == F(lo + 1, 3));
    B big(cpp_int(1) << 4096, 3);
    B copy = big;
    copy /= copy;
    assert(copy == B(1));
    assert(big - big == B(0));
    assert((big * B(3)).den == 1);
    assert((big * B(3)).num == cpp_int(1) << 4096);
    assert(double(F(1, 2)) == 0.5);
    ostringstream out;
    out << F(-4, -6) << ' ' << F(0, -7) << ' ' << F(6, 3);
    assert(out.str() == "2/3 0 2");
    cout << checks << " source/arithmetic/self-alias/comparison checks; signed boundaries and 4096-bit cases PASS\n";
}
