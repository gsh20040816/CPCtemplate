#include "../src/compact/persistent_weighted_index.hpp"
#include <iostream>
#include <numeric>
#include <random>
using ll = long long;
int main()
{
    mt19937 rng(38901675);
    long long checks = 0;
    for (int run = 0; run < 500; run++)
    {
        int n = 1 + rng() % 40;
        PersistentWeightedIndex tree(n);
        vector<vector<pair<int, ll>>> versions(1, vector<pair<int, ll>>(n));
        vector<int> parent(1, -1);
        for (int step = 0; step < 150; step++)
        {
            int from = rng() % versions.size();
            int pos = rng() % n;
            ll weight = int(rng() % 2001) - 1000;
            auto next = versions[from];
            next[pos].first++;
            next[pos].second += weight;
            int v = tree.add(from, pos, weight);
            assert(v == (int)versions.size());
            versions.push_back(next);
            parent.push_back(from);
            for (int trial = 0; trial < 8; trial++)
            {
                int version = rng() % versions.size();
                int l = rng() % (n + 1), r = rng() % (n + 1);
                if (l > r)
                    swap(l, r);
                pair<int, ll> expected{};
                for (int x = l; x < r; x++)
                {
                    expected.first += versions[version][x].first;
                    expected.second += versions[version][x].second;
                }
                assert(tree.query(version, l, r) == expected);
                int before = v;
                int steps = rng() % 10;
                while (steps-- && parent[before] != -1)
                    before = parent[before];
                int key = int(rng() % (n + 5)) - 2;
                int answer = -1;
                for (int x = max(0, key); x < n; x++)
                    if (versions[v][x].first > versions[before][x].first)
                    {
                        answer = x;
                        break;
                    }
                auto size = tree.t.size();
                assert(tree.first(before, v, key) == answer);
                assert(tree.t.size() == size);
                checks++;
            }
        }
    }
    PersistentWeightedIndex big(INT_MAX);
    int v = big.add(0, INT_MAX - 1, LLONG_MIN);
    assert(big.first(0, v, INT_MIN) == INT_MAX - 1);
    assert(big.first(0, v, INT_MAX) == -1);
    assert(big.query(v, 0, INT_MAX).second == LLONG_MIN);
    assert(big.query(0, 0, INT_MAX).first == 0);
    PersistentWeightedIndex pressure(200000);
    for (int i = 0; i < 200000; i++)
        pressure.add(i, i, i);
    for (int i = 0; i < 200000; i++)
    {
        auto result = pressure.query(i + 1, 0, 200000);
        assert(result.first == i + 1);
        assert(result.second == (ll)i * (i + 1) / 2);
        assert(pressure.first(i, i + 1, 0) == i);
    }
    cout << checks << " branched-version checks; 200000 prefix versions; signed boundaries PASS\n";
}
