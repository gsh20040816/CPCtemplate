#include <bits/stdc++.h>
#include <cassert>
#include "../src/compact/composite_binomial.hpp"
namespace original
{
using i64 = long long;
#include "fixtures/wida_composite_binomial/13C.cpp"
}
using namespace std;

int main()
{
    long long checks = 0;
    vector<int> mods;
    for (int m = 1; m <= 256; m++)
        mods.push_back(m);
    for (int m : {65536, 1000003, 1000000007, 1073741824,
                  1162261467, 1220703125, 2000000000, INT_MAX, 223092870})
        mods.push_back(m);
    for (int m : mods)
    {
        CompositeBinomial comb(100, m);
        unique_ptr<original::Binomial> ref;
        if (m <= 256)
            ref = make_unique<original::Binomial>(m);
        vector<int> row(101);
        row[0] = 1 % m;
        for (int n = 0; n <= 100; n++)
        {
            for (int k = -1; k <= n + 1; k++)
            {
                int expected = k < 0 || k > n ? 0 : row[k];
                if (comb.choose(n, k) != expected)
                    throw runtime_error("Pascal mismatch");
                if (ref && (*ref)(n, k) != expected)
                    throw runtime_error("Original small-domain mismatch");
                checks++;
            }
            if (n < 100)
                for (int k = n + 1; k >= 1; k--)
                    row[k] = (1LL * row[k] + row[k - 1]) % m;
        }
        if (comb.choose(-1, 0) != 0)
            throw runtime_error("Negative upper bound");
        CompositeBinomial empty(0, m);
        if (empty.choose(0, 0) != 1 % m)
            throw runtime_error("Empty table");
    }
    for (int m : {1, 223092870, INT_MAX, 2000000000, 1073741824})
    {
        CompositeBinomial comb(100000, m);
        for (int i = 0; i < 200000; i++)
        {
            int k = i % 100001;
            if (comb.choose(100000, k) != comb.choose(100000, 100000 - k))
                throw runtime_error("Stress symmetry mismatch");
        }
    }
    cout << checks << " Pascal/source checks; five 100000-bound stress tables PASS\n";
}
