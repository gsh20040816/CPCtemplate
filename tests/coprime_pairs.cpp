#include "../src/compact/coprime_pairs.hpp"
#include <cassert>
#include <iostream>

int main()
{
    CoprimePairs s(1000000);
    for (int a = 0; a <= 100; a++)
        for (int b = 0; b <= 100; b++)
        {
            long long expected = 0;
            for (int x = 1; x <= a; x++)
                for (int y = 1; y <= b; y++)
                    expected += gcd(x,y) == 1;
            assert(s.count(a,b) == expected);
        }
    for (int a = 1; a <= 12; a++)
        for (int b = a; b <= 12; b++)
            for (int c = 1; c <= 12; c++)
                for (int d = c; d <= 12; d++)
                    for (int k = 1; k <= 15; k++)
                    {
                        long long expected = 0;
                        for (int x = a; x <= b; x++)
                            for (int y = c; y <= d; y++)
                                expected += gcd(x,y) == k;
                        assert(s.rectangle(a,b,c,d,k) == expected);
                    }
    vector<int> phi(1000001);
    iota(phi.begin(), phi.end(), 0);
    for (int p = 2; p <= 1000000; p++)
        if (phi[p] == p)
            for (int j = p; j <= 1000000; j += p)
                phi[j] -= phi[j] / p;
    long long phi_sum = accumulate(phi.begin() + 1, phi.end(), 0LL);
    assert(s.count(1000000,1000000) == 2*phi_sum-1);
    // Count a long thin rectangle by full residue periods in the short coordinate.
    for (int b = 1; b <= 100; b++)
    {
        long long expected = 0;
        for (int y = 1; y <= b; y++)
        {
            int full = INT_MAX / y;
            int rem = INT_MAX % y;
            for (int r = 1; r <= y; r++)
                if (gcd(r,y) == 1)
                    expected += full + (r <= rem);
        }
        assert(s.count(INT_MAX,b) == expected);
    }
    assert(CoprimePairs(0).count(0,INT_MAX) == 0);
    cout << "Coprime pairs independent gcd rectangle oracle, zero prefixes, million square and INT_MAX thin intervals PASS\n";
}
