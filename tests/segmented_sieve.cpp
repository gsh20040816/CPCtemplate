#include "../src/compact/segmented_sieve.hpp"
#include "../src/classic/segmented_sieve.hpp"
#include "../src/compact/number_theory.hpp"
#include <climits>
#include <iostream>
#include <random>

bool trial(int n)
{
    if (n < 2)
        return false;
    for (int d = 2; d <= n / d; d++)
        if (n % d == 0)
            return false;
    return true;
}

void check(int l, int r, bool use_trial)
{
    vector<int> expected;
    for (long long x = l; x <= r; x++)
        if (use_trial ? trial(x) : NumberTheory::prime(x))
            expected.push_back(x);
    assert(segmented_primes(l, r) == expected);
    assert(Segmented_Primes(l, r) == expected);
}

int main()
{
    for (int l = 0; l <= 150; l++)
        for (int r = l; r <= 150; r++)
            check(l, r, true);
    for (int p : {2, 3, 5, 7, 31, 997, 46337, 46340})
    {
        int square = p * p;
        check(square - 2, square + 2, true);
    }
    check(INT_MAX, INT_MAX, true);
    check(0, 1000000, false);
    check(INT_MAX - 1000000, INT_MAX, false);
    mt19937 rng(2689);
    for (int t = 0; t < 300; t++)
    {
        int l = rng() % (INT_MAX - 1000);
        check(l, l + rng() % 1000, true);
    }
    cout << "Segmented sieve dual trial/Miller-Rabin oracles, prime squares, singleton and million-wide int32 boundary PASS\n";
}
