#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include "../src/compact/persistent_weighted_index.hpp"
#include "fixtures/wida_predecessor/08B.cpp"
using namespace std;

void remember(Node *p, set<Node *> &nodes)
{
    if (!p || !nodes.insert(p).second)
        return;
    remember(p->l, nodes);
    remember(p->r, nodes);
}

int main()
{
    mt19937 rng(18640826);
    long long checked = 0;
    for (int trial = 0; trial < 100; trial++)
    {
        int n = 1 + rng() % 70;
        PersistentWeightedIndex tree(n);
        vector<Node *> roots{nullptr};
        vector<vector<int>> counts(1, vector<int>(n));
        for (int i = 0; i < 300; i++)
        {
            int v = rng() % roots.size();
            int pos = rng() % n;
            tree.add(v, pos, int(rng() % 21) - 10);
            roots.push_back(add(roots[v], 0, n, pos));
            auto next = counts[v];
            next[pos]++;
            counts.push_back(next);
            for (int repetition = 0; repetition < 20; repetition++)
            {
                int before = rng() % roots.size();
                int after = rng() % roots.size();
                bool valid = true;
                for (int x = 0; x < n; x++)
                    valid &= counts[before][x] <= counts[after][x];
                if (!valid)
                    before = 0;
                int key = int(rng() % (n + 10)) - 5;
                if (repetition == 0)
                    key = INT_MIN;
                if (repetition == 1)
                    key = INT_MAX;
                int expected = -1;
                int successor = -1;
                for (int x = 0; x < n; x++)
                {
                    if (counts[after][x] == counts[before][x])
                        continue;
                    if (x < key)
                        expected = x;
                    if (x >= key && successor == -1)
                        successor = x;
                }
                auto allocated = tree.t.size();
                assert(tree.last(before, after, key) == expected);
                assert(tree.first(before, after, key) == successor);
                assert(query(roots[before], roots[after], 0, n, key) == expected);
                assert(tree.t.size() == allocated);
                checked++;
            }
        }
        set<Node *> nodes;
        for (Node *p : roots)
            remember(p, nodes);
        for (Node *p : nodes)
            delete p;
    }
    PersistentWeightedIndex huge(INT_MAX);
    int a = huge.add(0, INT_MAX - 1, -5);
    int b = huge.add(a, 0, 5);
    assert(huge.last(0, b, INT_MAX) == INT_MAX - 1);
    assert(huge.last(0, b, INT_MAX - 1) == 0);
    assert(huge.last(a, b, INT_MAX) == 0);
    assert(huge.last(b, b, INT_MAX) == -1);
    assert(huge.first(0, b, INT_MIN) == 0);
    assert(huge.last(0, b, INT_MIN) == -1);
    cout << checked << " branched original/core histogram comparisons PASS\n";
}
