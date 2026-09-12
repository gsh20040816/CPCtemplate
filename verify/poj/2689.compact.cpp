#include "../../src/compact/segmented_sieve.hpp"
#include <cstdio>

int main()
{
    int l, r;
    while (scanf("%d%d", &l, &r) == 2)
    {
        auto primes = segmented_primes(l, r);
        if (primes.size() < 2)
        {
            puts("There are no adjacent primes.");
            continue;
        }
        int closest = 1;
        int distant = 1;
        for (int i = 2; i < (int)primes.size(); i++)
        {
            int gap = primes[i] - primes[i - 1];
            if (gap < primes[closest] - primes[closest - 1])
                closest = i;
            if (gap > primes[distant] - primes[distant - 1])
                distant = i;
        }
        printf("%d,%d are closest, %d,%d are most distant.\n",
               primes[closest - 1],
               primes[closest],
               primes[distant - 1],
               primes[distant]);
    }
    return 0;
}
