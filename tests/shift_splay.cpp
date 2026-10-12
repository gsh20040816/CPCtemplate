#include "../src/compact/shift_splay.hpp"
#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
using ll = long long;
long long checks = 0;

void verify(ShiftSplay tree, int root, const vector<int> &ids, const vector<ll> &values)
{
    vector<int> seen;
    vector<ll> ordered;
    auto dfs = [&](auto &&self, int x, int parent) -> void
    {
        if (!x)
            return;
        assert(tree.a[x].fa == parent);
        tree.push(x);
        self(self, tree.a[x].ch[0], x);
        seen.push_back(x);
        ordered.push_back(tree.a[x].val);
        assert(tree.a[x].val == values[x]);
        self(self, tree.a[x].ch[1], x);
    };
    dfs(dfs, root, 0);
    assert(is_sorted(ordered.begin(), ordered.end()));
    auto expected = ids;
    sort(expected.begin(), expected.end());
    sort(seen.begin(), seen.end());
    assert(seen == expected);
    checks++;
}

void scenario(const vector<ll> &initial, mt19937 &rng)
{
    ShiftSplay tree;
    int root = 0;
    vector<int> ids;
    vector<ll> values(1);
    for (ll x : initial)
    {
        ids.push_back(tree.insert(root, x));
        values.push_back(x);
    }
    verify(tree, root, ids, values);
    for (int step = 0; step < 40; step++)
    {
        ll key = int(rng() % 15) - 7;
        auto [left, right] = tree.split(root, key);
        vector<int> lo, hi;
        for (int id : ids)
            (values[id] < key ? lo : hi).push_back(id);
        verify(tree, left, lo, values);
        verify(tree, right, hi, values);
        ll delta = rng() % 6;
        tree.add(left, -delta);
        tree.add(right, delta);
        for (int id : lo)
            values[id] -= delta;
        for (int id : hi)
            values[id] += delta;
        // Access a stable node under pending tags before traversing the real tree.
        if (!lo.empty())
        {
            int id = lo[rng() % lo.size()];
            assert(tree.value(left, id) == values[id]);
        }
        if (!hi.empty())
        {
            int id = hi[rng() % hi.size()];
            assert(tree.value(right, id) == values[id]);
        }
        root = tree.merge(left, right);
        verify(tree, root, ids, values);
        if (step % 10 == 0)
        {
            ll x = int(rng() % 7) - 3;
            ids.push_back(tree.insert(root, x));
            values.push_back(x);
        }
        ll shift = int(rng() % 7) - 3;
        tree.add(root, shift);
        for (int id : ids)
            values[id] += shift;
    }
    for (int id : ids)
        assert(tree.value(root, id) == values[id]);
    auto copy = tree;
    copy.add(root, 9);
    verify(tree, root, ids, values);
}

int main()
{
    mt19937 rng(38901674);
    int cases = 0;
    for (int n = 0, ways = 1; n <= 6; n++, ways *= 3)
        for (int mask = 0; mask < ways; mask++)
        {
            vector<ll> values(n);
            int code = mask;
            for (ll &v : values)
            {
                v = code % 3 - 1;
                code /= 3;
            }
            scenario(values, rng);
            cases++;
        }
    for (int trial = 0; trial < 300; trial++)
    {
        vector<ll> values(rng() % 80);
        for (ll &v : values)
            v = int(rng() % 1000) - 500;
        scenario(values, rng);
        cases++;
    }
    ShiftSplay extreme;
    int root = 0;
    int low = extreme.insert(root, LLONG_MIN);
    int high = extreme.insert(root, LLONG_MAX);
    auto [l, r] = extreme.split(root, LLONG_MAX);
    assert(extreme.value(l, low) == LLONG_MIN);
    assert(extreme.value(r, high) == LLONG_MAX);
    root = extreme.merge(l, r);
    assert(extreme.value(root, low) == LLONG_MIN);
    ShiftSplay chain;
    root = 0;
    int n = 200000;
    for (int i = 0; i < n; i++)
        chain.insert(root, i);
    chain.add(root, 17);
    assert(chain.value(root, 1) == 17);
    for (int i = 1; i <= n; i++)
        assert(chain.value(root, i) == i - 1 + 17);
    cout << cases << " scenarios; " << checks
         << " structural/value certificates; 200000-node recursive chain PASS\n";
}
