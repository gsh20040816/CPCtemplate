#include "../src/compact/linear_equation.hpp"
#include "../src/classic/linear_equation.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <random>
using boost::multiprecision::cpp_int;
using i128 = __int128_t;

void check(long long a, long long b, long long c)
{
    i128 aa = a < 0 ? -i128(a) : i128(a);
    i128 bb = b < 0 ? -i128(b) : i128(b);
    i128 g = aa;
    i128 h = bb;
    while (h)
    {
        i128 t = g % h;
        g = h;
        h = t;
    }
    bool expected = g ? c % g == 0 : c == 0;
    i128 x, y, u, v;
    assert(NumberTheory::exgcd(aa, bb, u, v) == g);
    assert(cpp_int(aa) * cpp_int(u) + cpp_int(bb) * cpp_int(v) == cpp_int(g));
    assert(Number_Theory::Exgcd(aa, bb, u, v) == g);
    assert(cpp_int(aa) * cpp_int(u) + cpp_int(bb) * cpp_int(v) == cpp_int(g));
    assert(linear_equation(a, b, c, x, y) == expected);
    assert(Linear_Equation(a, b, c, u, v) == expected);
    assert(x == u && y == v);
    if (!expected)
    {
        assert(x == 0 && y == 0);
        return;
    }
    assert(cpp_int(a) * cpp_int(x) + cpp_int(b) * cpp_int(y) == c);
    if (g)
        for (int t : {-7, -1, 0, 1, 9})
        {
            cpp_int xx = cpp_int(x) + cpp_int(i128(b) / g) * t;
            cpp_int yy = cpp_int(y) - cpp_int(i128(a) / g) * t;
            assert(cpp_int(a) * xx + cpp_int(b) * yy == c);
        }
}

int main()
{
    for (int a = -20; a <= 20; a++)
        for (int b = -20; b <= 20; b++)
            for (int c = -20; c <= 20; c++)
                check(a, b, c);
    vector<long long> edge = {LLONG_MIN, LLONG_MIN + 1, -1, 0, 1, LLONG_MAX - 1, LLONG_MAX};
    for (auto a : edge)
        for (auto b : edge)
            for (auto c : edge)
                check(a, b, c);
    mt19937_64 rng(5656);
    for (int i = 0; i < 10000; i++)
        check(bit_cast<long long>(rng()), bit_cast<long long>(rng()), bit_cast<long long>(rng()));
    long long a = 1, b = 1;
    while (a <= LLONG_MAX - b)
    {
        check(a, b, LLONG_MIN);
        long long c = a + b;
        a = b;
        b = c;
    }
    cout << "Linear equation dual signed exhaustive cases, cpp_int Bezout certificates, int64 extremes and Fibonacci recursion PASS\n";
}
