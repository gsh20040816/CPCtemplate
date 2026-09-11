#include "../src/compact/exlucas.hpp"
#include "../src/classic/exlucas.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <climits>
#include <iostream>
#include <random>
using boost::multiprecision::cpp_int;
using ull = unsigned long long;

cpp_int binomial(ull n, unsigned k)
{
    cpp_int value = 1;
    for (unsigned i = 1; i <= k; i++)
    {
        value *= cpp_int(n) - k + i;
        value /= i;
    }
    return value;
}

int main()
{
    static Ex_Lucas<1000000> classic;
    for (int mod = 1; mod <= 300; mod++)
    {
        ExLucas g(mod);
        classic.Init(mod);
        assert(classic.used <= mod + 1);
        std::vector<int> row(102);
        row[0] = 1 % mod;
        for (unsigned n = 0; n <= 100; n++)
        {
            for (unsigned k = 0; k <= n + 1; k++)
            {
                assert(g.choose(n, k) == row[k]);
                assert(classic.Choose(n, k) == row[k]);
            }
            for (unsigned k = n + 1; k; k--)
                row[k] = (row[k] + row[k - 1]) % mod;
        }
    }
    std::mt19937_64 rng(4720);
    for (int mod : {2, 3, 4, 8, 16, 27, 72, 243, 625, 1024, 360360, 999983, 1000000})
    {
        ExLucas g(mod);
        classic.Init(mod);
        assert(classic.used <= mod + 1);
        for (int i = 0; i < 150; i++)
        {
            ull n = i == 0 ? ULLONG_MAX : rng();
            unsigned k = rng() % 150;
            int want = (binomial(n, k) % mod).convert_to<int>();
            assert(g.choose(n, k) == want);
            assert(classic.Choose(n, k) == want);
            assert(g.choose(n, n - k) == want);
            assert(classic.Choose(n, n - k) == want);
        }
        assert(g.choose(ULLONG_MAX, ULLONG_MAX) == 1 % mod);
        assert(classic.Choose(ULLONG_MAX, ULLONG_MAX) == 1 % mod);
        assert(g.choose(0, ULLONG_MAX) == 0);
        assert(classic.Choose(0, ULLONG_MAX) == 0);
    }
    // Independent prime-modulus Lucas via small Pascal tables: both indices huge.
    for (int p : {2, 3, 5, 7, 11, 97})
    {
        std::vector<std::vector<int>> c(p, std::vector<int>(p));
        for (int i = 0; i < p; i++)
        {
            c[i][0] = 1;
            for (int j = 1; j <= i; j++)
                c[i][j] = (c[i - 1][j] + c[i - 1][j - 1]) % p;
        }
        ExLucas g(p);
        classic.Init(p);
        for (int it = 0; it < 1000; it++)
        {
            ull n = rng(), k = rng();
            if (k > n)
                std::swap(n, k);
            ull a = n, b = k;
            int want = 1;
            while (a || b)
            {
                want = want * c[a % p][b % p] % p;
                a /= p;
                b /= p;
            }
            assert(g.choose(n, k) == want);
            assert(classic.Choose(n, k) == want);
        }
    }
    // Full middle coefficients, checked as exact integers rather than only identities.
    for (int mod : {16, 81, 125, 72, 2310})
    {
        ExLucas g(mod);
        classic.Init(mod);
        for (unsigned n : {1000, 2048, 5000})
        {
            int want = (binomial(n, n / 2) % mod).convert_to<int>();
            assert(g.choose(n, n / 2) == want);
            assert(classic.Choose(n, n / 2) == want);
        }
    }
    std::cout << "exLucas dual Pascal, exact big integers, uint64 extremes and prime Lucas oracle PASS\n";
}
