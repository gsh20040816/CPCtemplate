#include "../src/compact/sequence_max_treap.hpp"
#include <iostream>
#include <numeric>
using ll = long long;
int check(const SequenceMaxTreap &tree, int p, vector<int> &order)
{
    if (!p)
        return 0;
    auto node = tree.t[p];
    int left = check(tree, node.left, order);
    order.push_back(p);
    int right = check(tree, node.right, order);
    assert(node.size == left + right + 1);
    ll maximum = node.value;
    for (int child : {node.left, node.right})
        if (child)
        {
            assert(node.priority >= tree.t[child].priority);
            maximum = max(maximum, tree.t[child].maximum);
        }
    assert(node.maximum == maximum);
    return node.size;
}
int main()
{
    mt19937_64 rng(380008);
    long long certificates = 0;
    for (int trial = 0; trial < 150; trial++)
    {
        SequenceMaxTreap tree(trial);
        vector<int> roots{0};
        vector<vector<int>> lists(1);
        vector<ll> values{0};
        for (int step = 0; step < 350; step++)
        {
            int r = rng() % roots.size();
            int op = rng() % 5;
            if (op < 3)
            {
                int pos = rng() % (lists[r].size() + 1);
                ll value = ll(rng() % 21) - 10;
                if (step % 19 == 0)
                    value = LLONG_MIN;
                if (step % 23 == 0)
                    value = LLONG_MAX;
                int id = tree.insert(roots[r], pos, value);
                assert(id == (int)values.size());
                values.push_back(value);
                lists[r].insert(lists[r].begin() + pos, id);
            }
            else if (op == 3)
            {
                int pos = rng() % (lists[r].size() + 1);
                auto [a, b] = tree.split(roots[r], pos);
                roots[r] = a;
                roots.push_back(b);
                vector<int> suffix(lists[r].begin() + pos, lists[r].end());
                lists[r].resize(pos);
                lists.push_back(suffix);
            }
            else
            {
                int s = rng() % roots.size();
                if (r != s)
                {
                    roots[r] = tree.merge(roots[r], roots[s]);
                    roots[s] = 0;
                    lists[r].insert(lists[r].end(), lists[s].begin(), lists[s].end());
                    lists[s].clear();
                }
            }
            vector<int> all;
            for (int slot = 0; slot < (int)roots.size(); slot++)
            {
                vector<int> order;
                check(tree, roots[slot], order);
                assert(order == lists[slot] && tree.ids(roots[slot]) == order);
                all.insert(all.end(), order.begin(), order.end());
                for (ll value : {LLONG_MIN, LLONG_MAX, ll(rng() % 25) - 12})
                {
                    int expected = -1;
                    for (int i = 0; i < (int)order.size(); i++)
                    {
                        assert(tree.t[order[i]].value == values[order[i]]);
                        if (values[order[i]] > value)
                            expected = i;
                    }
                    assert(tree.last_greater(roots[slot], value) == expected);
                    certificates++;
                }
            }
            sort(all.begin(), all.end());
            assert(all.size() + 1 == values.size());
            for (int i = 0; i < (int)all.size(); i++)
                assert(all[i] == i + 1);
        }
    }
    SequenceMaxTreap tree;
    int root = 0;
    for (int i = 0; i < 200000; i++)
        tree.insert(root, i, 7);
    for (int i = 0; i < 200000; i++)
    {
        assert(tree.last_greater(root, 7) == -1);
        assert(tree.last_greater(root, 6) == 199999);
    }
    auto [a, b] = tree.split(root, 100000);
    root = tree.merge(b, a);
    auto order = tree.ids(root);
    assert(order.front() == 100001 && order.back() == 100000);
    cout << certificates << " forest threshold certificates; 200000 equal-value pressure PASS\n";
}
