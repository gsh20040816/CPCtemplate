#include "../src/compact/lucas.hpp"
#include "../src/classic/lucas.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <climits>
#include <iostream>
#include <random>
using boost::multiprecision::cpp_int;

int main()
{
    static Lucas_Theorem<100000> classic;
    Lucas compact(2);
    mt19937_64 rng(3807);
    for (int p : {2, 3, 5, 7, 11, 97, 2, 99991})
    {
        compact = Lucas(p);
        classic.Init(p);
        auto check = [&](unsigned long long n, unsigned long long k, int want)
        {
            assert(compact.choose(n, k) == want);
            assert(classic.Choose(n, k) == want);
        };
        vector<int> row(302);
        row[0] = 1;
        for (int n = 0; n <= 300; n++)
        {
            for (int k = 0; k <= n + 1; k++)
                check(n, k, row[k]);
            for (int k = n + 1; k; k--)
                row[k] = (row[k] + row[k - 1]) % p;
        }
        for (int it = 0; it < 400; it++)
        {
            unsigned long long n = rng(), k = rng() % 80;
            cpp_int exact = 1;
            for (unsigned long long j = 1; j <= k; j++)
                exact = exact * (cpp_int(n) - j + 1) / j;
            int want = (exact % p).convert_to<int>();
            check(n, k, want);
            check(n, n - k, want);
        }
        check(ULLONG_MAX, ULLONG_MAX, 1);
        check(ULLONG_MAX, 1, ULLONG_MAX % p);
        check(ULLONG_MAX - 1, ULLONG_MAX, 0);
        check(0, 0, 1);
        // (1+x)^(p^a) = 1+x^(p^a) in the field.
        unsigned long long power = p;
        while (power <= ULLONG_MAX / p)
            power *= p;
        check(power, power / p, 0);
        check(power - 1, power / p, (power / p) % 2 && p != 2 ? p - 1 : 1);
    }
    for (int it = 0; it < 10000; it++)
    {
        auto n = rng(), k = rng();
        Lucas binary(2);
        assert(binary.choose(n, k) == ((k & ~n) == 0));
    }
    cout << "Lucas dual Pascal oracle, exact big integers, uint64 extremes, prime-power identities and modulus reset PASS\n";
}
