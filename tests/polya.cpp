#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
#include "../src/compact/polya.hpp"
using namespace std;
using boost::multiprecision::cpp_int;

void check(bool ok)
{
    if (!ok) abort();
}

int main()
{
    mt19937_64 rng(14464980);
    for (int n = 0; n <= 8; n++)
    {
        vector<int> p(n);
        iota(p.begin(), p.end(), 0);
        do
        {
            vector<int> group(n);
            iota(group.begin(), group.end(), 0);
            for (int i = 0; i < n; i++)
            {
                int a = group[i], b = group[p[i]];
                for (int &x : group)
                {
                    if (x == b) x = a;
                }
            }
            vector<int> counts(n);
            for (int x : group) counts[x]++;
            counts.erase(remove(counts.begin(), counts.end(), 0), counts.end());
            auto lengths = permutation_cycles(p);
            sort(counts.begin(), counts.end());
            sort(lengths.begin(), lengths.end());
            check(counts == lengths);
        } while (next_permutation(p.begin(), p.end()));
    }
    for (int n = 1; n <= 8; n++)
    {
        for (int c = 0; c <= 3; c++)
        {
            set<vector<int>> rotation, dihedral;
            int total = 1;
            for (int i = 0; i < n; i++) total *= c;
            for (int mask = 0; mask < total; mask++)
            {
                vector<int> a(n);
                int value = mask;
                for (int &x : a)
                {
                    x = value % c;
                    value /= c;
                }
                auto best = a;
                for (int k = 0; k < n; k++)
                {
                    rotate(a.begin(), a.begin() + 1, a.end());
                    best = min(best, a);
                }
                rotation.insert(best);
                reverse(a.begin(), a.end());
                for (int k = 0; k < n; k++)
                {
                    rotate(a.begin(), a.begin() + 1, a.end());
                    best = min(best, a);
                }
                dihedral.insert(best);
            }
            for (int mod = 1; mod <= 35; mod++)
            {
                check(necklace_colorings(n, c, mod) == (long long)rotation.size() % mod);
                check(necklace_colorings(n, c, mod, true) == (long long)dihedral.size() % mod);
            }
        }
    }
    for (int it = 0; it < 2000; it++)
    {
        long long g = 1 + rng() % 1000000000;
        long long p = 1 + rng() % (LLONG_MAX / 2 / g);
        long long value = rng() % LLONG_MAX;
        BurnsideAverage avg(g, p);
        avg.add(value, g);
        check(avg.result() == value % p);
        int k = rng() % 20;
        cpp_int exact = 1;
        for (int i = 0; i < k; i++) exact *= value;
        check(avg.power(value, k) == (exact % avg.mod).convert_to<long long>());
    }
    BurnsideAverage edge(1, LLONG_MAX / 2);
    edge.add(LLONG_MAX, LLONG_MAX);
    check(edge.result() == (cpp_int(LLONG_MAX) * LLONG_MAX % edge.mod).convert_to<long long>());
    check(necklace_colorings(INT_MAX, 1, 1000000007, true) == 1);
    check(necklace_colorings(1, LLONG_MAX, 1000000007, true) == LLONG_MAX % 1000000007);
    cout << "PASS exhaustive permutations, orbit enumeration, arbitrary-modulus division and wide arithmetic\n";
}
