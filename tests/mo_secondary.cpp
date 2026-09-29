#include "../src/compact/mo_secondary.hpp"
#include <iostream>
#include <random>

vector<long long>
brute(const vector<int> &a, const vector<pair<int, int>> &queries, int k)
{
    vector<long long> result;
    for (auto [l, r] : queries)
    {
        long long value = 0;
        for (int i = l; i < r; i++)
            for (int j = i + 1; j < r; j++)
            {
                int x = a[i] ^ a[j], ones = 0;
                while (x)
                {
                    ones += x & 1;
                    x >>= 1;
                }
                value += ones == k;
            }
        result.push_back(value);
    }
    return result;
}

int main()
{
    mt19937 rng(4887);
    for (int n = 0; n <= 6; n++)
        for (int code = 0; code < (1 << (2 * n)); code++)
        {
            vector<int> a(n);
            for (int i = 0; i < n; i++) a[i] = (code >> (2 * i)) & 3;
            vector<pair<int, int>> queries;
            for (int l = 0; l <= n; l++)
                for (int r = l; r <= n; r++) queries.push_back({l, r});
            shuffle(queries.begin(), queries.end(), rng);
            for (int k = -1; k <= 3; k++)
                assert(xor_hamming_pairs(a, queries, k, 2) == brute(a, queries, k));
        }
    for (int t = 0; t < 1500; t++)
    {
        int bits = rng() % 9, n = rng() % 60, m = rng() % 100;
        vector<int> a(n);
        for (int &x : a) x = rng() % (1 << bits);
        vector<pair<int, int>> queries(m);
        for (auto &[l, r] : queries)
        {
            l = rng() % (n + 1);
            r = rng() % (n + 1);
            if (l > r) swap(l, r);
        }
        int k = int(rng() % (bits + 3)) - 1;
        assert(xor_hamming_pairs(a, queries, k, bits) == brute(a, queries, k));
    }
    for (int bits : {14, 20})
    {
        vector<int> a = {0, (1 << bits) - 1, 0, (1 << bits) - 1};
        vector<pair<int, int>> queries = {{0, 4}, {0, 1}, {1, 3}, {4, 4}};
        for (int k : {0, bits, bits + 1})
            assert(xor_hamming_pairs(a, queries, k, bits) == brute(a, queries, k));
    }
    int n = 100000;
    vector<int> a(n);
    vector<pair<int, int>> queries(n);
    for (int i = 0; i < n; i++)
    {
        int l = rng() % n, r = rng() % n;
        if (l > r) swap(l, r);
        queries[i] = {l, r + 1};
    }
    queries[0] = {0, n};
    auto result = xor_hamming_pairs(a, queries, 0);
    for (int i = 0; i < n; i++)
    {
        long long len = queries[i].second - queries[i].first;
        assert(result[i] == len * (len - 1) / 2);
    }
    for (int i = 0; i < n; i++) a[i] = i & 1 ? 127 : 0;
    result = xor_hamming_pairs(a, queries, 7);
    for (int i = 0; i < n; i++)
    {
        auto [l, r] = queries[i];
        long long odd = r / 2 - l / 2;
        assert(result[i] == odd * (r - l - odd));
    }
    assert(xor_hamming_pairs(a, {}, 7).empty());
    cout << "mo_secondary: exhaustive, 1500 random, 100000-scale k=0/7 passed\n";
}
