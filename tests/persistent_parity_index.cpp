#include "../src/compact/persistent_parity_index.hpp"
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include "fixtures/wida_parity_index/08A.cpp"
using namespace std;

void remember(Node *p, set<Node *> &seen)
{
    if (!p || !seen.insert(p).second)
        return;
    remember(p->l, seen);
    remember(p->r, seen);
}

void certificate(const PersistentParityIndex &tree, int p, int l, int r,
                 const vector<int> &values)
{
    long long count = 0, odd = 0;
    for (int i = l; i < r; i++)
    {
        count += values[i];
        odd += (i % 2) * values[i];
    }
    assert(tree.t[p].count == count && tree.t[p].odd == odd);
    if (r - l == 1)
        return;
    int m = l + (r - l) / 2;
    certificate(tree, tree.t[p].left, l, m, values);
    certificate(tree, tree.t[p].right, m, r, values);
}

int main()
{
    mt19937 rng(20261012);
    long long checked = 0;
    for (int trial = 0; trial < 100; trial++)
    {
        int n = 1 + rng() % 60;
        PersistentParityIndex tree(n);
        vector<Node *> roots{nullptr};
        vector<vector<int>> counts(1, vector<int>(n));
        for (int step = 0; step < 300; step++)
        {
            int version = rng() % roots.size();
            int pos = rng() % n;
            int delta = max(int(rng() % 11) - 5, -counts[version][pos]);
            auto values = counts[version];
            values[pos] += delta;
            counts.push_back(values);
            roots.push_back(add(roots[version], 0, n, pos, delta));
            assert(tree.add(version, pos, delta) == step + 1);
            certificate(tree, tree.roots.back(), 0, n, values);
            for (int repeat = 0; repeat < 10; repeat++)
            {
                int before = rng() % roots.size();
                int after = rng() % roots.size();
                bool valid = true;
                for (int x = 0; x < n; x++)
                    valid &= counts[before][x] <= counts[after][x];
                if (!valid)
                    before = 0;
                certificate(tree, tree.roots[after], 0, n, counts[after]);
                vector<int> all, odd;
                for (int x = n - 1; x >= 0; x--)
                {
                    int cnt = counts[after][x] - counts[before][x];
                    all.insert(all.end(), cnt, x);
                    if (x % 2)
                        odd.insert(odd.end(), cnt, x);
                }
                int k = rng() % (all.size() + 10);
                int deleted = 0;
                while (deleted < k && deleted < int(all.size()) && all[deleted] % 2 == 0)
                    deleted++;
                int expected = deleted == int(all.size()) ? -1 : all[deleted];
                assert(tree.stop(before, after, k) == expected);
                assert(query1(roots[after], roots[before], 0, n, k) == max(0, expected));
                array<long long, 3> answer{-1, 0, k - (long long)odd.size()};
                if (k < int(odd.size()))
                {
                    int value = odd[k];
                    int count = std::count(odd.begin(), odd.end(), value);
                    int first = find(odd.begin(), odd.end(), value) - odd.begin();
                    answer = {value, count, k - first};
                }
                auto allocated = tree.t.size();
                assert(tree.odd_kth(before, after, k) == answer);
                auto original = query2(roots[after], roots[before], 0, n, k);
                assert(original[0] == max(0LL, answer[0]));
                assert(original[1] == answer[1] && original[2] == answer[2]);
                assert(tree.t.size() == allocated);
                auto totals = tree.difference(before, after);
                assert(totals[0] == (long long)all.size() && totals[1] == (long long)odd.size());
                checked++;
            }
        }
        set<Node *> nodes;
        for (Node *p : roots)
            remember(p, nodes);
        for (Node *p : nodes)
            delete p;
    }
    PersistentParityIndex huge(INT_MAX);
    int a = huge.add(0, INT_MAX - 2, LLONG_MAX);
    assert(huge.stop(0, a, LLONG_MAX) == INT_MAX - 2);
    assert((huge.odd_kth(0, a, LLONG_MAX - 1) == array<long long, 3>{INT_MAX - 2, LLONG_MAX, LLONG_MAX - 1}));
    assert((huge.odd_kth(0, a, LLONG_MAX) == array<long long, 3>{-1, 0, 0}));
    int b = huge.add(a, INT_MAX - 2, -LLONG_MAX);
    assert((huge.difference(a, b) == array<long long, 2>{-LLONG_MAX, -LLONG_MAX}));
    int c = huge.add(b, INT_MAX - 1, LLONG_MAX);
    assert(huge.stop(b, c, LLONG_MAX - 1) == INT_MAX - 1);
    assert(huge.stop(b, c, LLONG_MAX) == -1);
    assert(huge.stop(0, b, 0) == -1);
    int d = huge.add(0, 0, 1);
    assert(huge.stop(0, d, 0) == 0);
    assert(huge.stop(0, d, 1) == -1);
    cout << checked << " branched signed-update parity comparisons; signed64 extremes PASS\n";
}
