#include "../src/compact/merge_split_tree.hpp"
#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <tuple>
#include "fixtures/wida_rank_split/08D.cpp"
using namespace std;

void destroy(Node *p)
{
    if (!p)
        return;
    destroy(p->l);
    destroy(p->r);
    delete p;
}

void original_values(Node *p, int l, int r, vector<long long> &a)
{
    if (!p)
        return;
    assert(p->cntnew == 0);
    if (r - l == 1)
    {
        a[l] = p->cnt;
        return;
    }
    assert(p->cnt == (p->l ? p->l->cnt : 0) + (p->r ? p->r->cnt : 0));
    int m = l + (r - l) / 2;
    original_values(p->l, l, m, a);
    original_values(p->r, m, r, a);
}

void core_values(const MergeSplitTree &tree, int p, int l, int r,
                 vector<long long> &a, set<int> &seen)
{
    if (!p)
        return;
    assert(seen.insert(p).second && tree.t[p].sum > 0);
    if (r - l == 1)
    {
        a[l] = tree.t[p].sum;
        return;
    }
    assert(tree.t[p].sum == tree.t[tree.t[p].l].sum + tree.t[tree.t[p].r].sum);
    int m = l + (r - l) / 2;
    core_values(tree, tree.t[p].l, l, m, a, seen);
    core_values(tree, tree.t[p].r, m, r, a, seen);
}

int main()
{
    mt19937 rng(63162242);
    long long checked = 0;
    for (int trial = 0; trial < 60; trial++)
    {
        int n = 1 + rng() % 30;
        MergeSplitTree tree(n);
        vector<Node *> roots{nullptr};
        vector<vector<long long>> expected(1, vector<long long>(n));
        for (int step = 0; step < 300; step++)
        {
            int s = rng() % roots.size();
            int op = rng() % 3;
            if (op == 0)
            {
                int x = rng() % n;
                roots[s] = merge(roots[s], add(0, n, x, 0), 0, n);
                tree.add(s, x, 1);
                expected[s][x]++;
            }
            else if (op == 1)
            {
                int total = accumulate(expected[s].begin(), expected[s].end(), 0);
                int k = rng() % (total + 1);
                bool reverse = rng() % 2;
                auto [take, remain] = split(roots[s], 0, n, k, reverse);
                roots[s] = remain;
                roots.push_back(take);
                assert(tree.split_rank(s, k, reverse) == int(roots.size()) - 1);
                vector<long long> taken(n);
                for (int j = 0; j < n; j++)
                {
                    int x = reverse ? n - 1 - j : j;
                    int count = min<long long>(k, expected[s][x]);
                    k -= count;
                    expected[s][x] -= count;
                    taken[x] = count;
                }
                expected.push_back(taken);
            }
            else
            {
                int other = rng() % roots.size();
                if (other == s)
                    continue;
                roots[s] = merge(roots[s], roots[other], 0, n);
                roots[other] = nullptr;
                tree.merge(s, other);
                for (int x = 0; x < n; x++)
                {
                    expected[s][x] += expected[other][x];
                    expected[other][x] = 0;
                }
            }
            set<int> seen;
            for (int id = 0; id < int(roots.size()); id++)
            {
                vector<long long> a(n), b(n);
                original_values(roots[id], 0, n, a);
                core_values(tree, tree.root[id], 0, n, b, seen);
                assert(a == expected[id] && b == expected[id]);
                checked++;
            }
            for (int p : tree.free)
            {
                assert(seen.insert(p).second);
                assert(tree.t[p].sum == 0 && tree.t[p].l == 0 && tree.t[p].r == 0);
            }
            assert(seen.size() + 1 == tree.t.size());
        }
        for (Node *p : roots)
            destroy(p);
    }
    MergeSplitTree huge(INT_MAX);
    huge.add(0, INT_MAX - 1, LLONG_MAX - 1);
    huge.add(0, 0, 1);
    int a = huge.split_rank(0, LLONG_MAX - 2, true);
    assert(huge.sum(a, 0, INT_MAX) == LLONG_MAX - 2);
    assert(huge.sum(0, 0, INT_MAX) == 2);
    huge.merge(0, a);
    int b = huge.split_rank(0, LLONG_MAX);
    assert(huge.sum(b, 0, INT_MAX) == LLONG_MAX);
    assert(huge.sum(0, 0, INT_MAX) == 0);
    // Establish only that arbitrary marked duplicate occurrences are not the source contract.
    Node *marked = merge(add(0, 1, 0, 1), add(0, 1, 0, 1), 0, 1);
    auto [left, right] = split(marked, 0, 1, 1, false);
    assert(left->cnt == 1 && left->cntnew == 2);
    assert(right->cnt == 1 && right->cntnew == 0);
    destroy(left);
    destroy(right);
    cout << checked << " forest original/core rank-split certificates; marked-domain probe PASS\n";
}
