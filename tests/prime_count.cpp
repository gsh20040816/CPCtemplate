#include "../src/compact/prime_count.hpp"

int main()
{
    int n = 1000000;
    vector<bool> composite(n + 1);
    vector<int> count(n + 1);
    for (int p = 2; p <= n; p++)
    {
        if (!composite[p])
            for (int k = 2 * p; k <= n; k += p) composite[k] = true;
        count[p] = count[p - 1] + !composite[p];
    }
    for (int x = 0; x <= 10000; x++) assert(prime_count(x) == count[x]);
    mt19937 rng(388);
    for (int t = 0; t < 1000; t++)
    {
        int x = rng() % (n + 1);
        assert(prime_count(x) == count[x]);
    }
    for (int s : {31, 32, 63, 64, 127, 128, 997, 1000})
        for (int d = -1; d <= 1; d++)
        {
            int x = s * s + d;
            if (x <= n) assert(prime_count(x) == count[x]);
        }
    assert(prime_count(1000000000) == 50847534);
    cout << "prime_count: independent sieve through 1e6, all n<=10000, 1000 random "
            "queries, square boundaries, pi(1e9) PASS\n";
}
