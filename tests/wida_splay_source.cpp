#include <bits/stdc++.h>
#include <cassert>
using namespace std;
using i64 = long long;
namespace source
{
#include "fixtures/wida_splay_sources/original.inc"
}

long long certificates = 0;
void check(source::Tree *root, const vector<int> &ids, const vector<int> &values)
{
    vector<int> seen, sorted;
    auto dfs = [&](auto &&self, source::Tree *p, source::Tree *parent) -> void
    {
        if (!p)
            return;
        assert(p->p == parent);
        source::push(p);
        self(self, p->ch[0], p);
        seen.push_back(p->id);
        sorted.push_back(p->val);
        assert(values[p->id] == p->val);
        self(self, p->ch[1], p);
    };
    dfs(dfs, root, nullptr);
    assert(is_sorted(sorted.begin(), sorted.end()));
    sort(seen.begin(), seen.end());
    auto expected = ids;
    sort(expected.begin(), expected.end());
    assert(seen == expected);
    certificates++;
}

int main()
{
    mt19937 rng(38901676);
    for (int trial = 0; trial < 1000; trial++)
    {
        source::Tree *root = nullptr;
        vector<source::Tree *> nodes;
        vector<int> values, ids;
        for (int i = 0; i < 60; i++)
        {
            auto p = new source::Tree;
            p->id = i;
            p->val = int(rng() % 101) - 50;
            nodes.push_back(p);
            values.push_back(p->val);
            ids.push_back(i);
            source::insert(root, p);
            // insert itself does not splay; the caller must perform the access.
            source::splay(p);
            root = p;
        }
        for (int step = 0; step < 60; step++)
        {
            int key = int(rng() % 121) - 60;
            auto [left, right] = source::split(root, key);
            vector<int> lo, hi;
            for (int i : ids)
                (values[i] < key ? lo : hi).push_back(i);
            int delta = rng() % 6;
            if (left)
                source::add(left, -delta);
            if (right)
                source::add(right, delta);
            for (int i : lo)
                values[i] -= delta;
            for (int i : hi)
                values[i] += delta;
            // Read by identity before a traversal can clear the pending tags.
            if (!lo.empty())
            {
                auto p = nodes[lo[rng() % lo.size()]];
                source::splay(p);
                left = p;
                assert(p->val == values[p->id]);
            }
            if (!hi.empty())
            {
                auto p = nodes[hi[rng() % hi.size()]];
                source::splay(p);
                right = p;
                assert(p->val == values[p->id]);
            }
            root = source::merge(left, right);
            check(root, ids, values);
        }
        for (auto p : nodes)
            delete p;
    }
    long long persistent_checks = 0;
    for (int trial = 0; trial < 500; trial++)
    {
        int n = 1 + rng() % 40;
        vector<source::Node *> roots(1);
        vector<vector<pair<int, i64>>> truth(1, vector<pair<int, i64>>(n));
        vector<int> parents(1, -1);
        for (int step = 0; step < 100; step++)
        {
            int before = rng() % roots.size();
            int p = rng() % n, w = int(rng() % 2001) - 1000;
            roots.push_back(source::add(roots[before], 0, n, p, w));
            auto next = truth[before];
            next[p].first++;
            next[p].second += w;
            truth.push_back(next);
            parents.push_back(before);
            int after = roots.size() - 1;
            for (int query = 0; query < 10; query++)
            {
                int v = rng() % roots.size();
                int l = rng() % (n + 1), r = rng() % (n + 1);
                if (l > r)
                    swap(l, r);
                pair<int, i64> expected{};
                for (int i = l; i < r; i++)
                {
                    expected.first += truth[v][i].first;
                    expected.second += truth[v][i].second;
                }
                assert(source::get(roots[v], 0, n, l, r) == expected);
                before = after;
                int steps = rng() % 10;
                while (steps-- && parents[before] != -1)
                    before = parents[before];
                int key = int(rng() % (n + 4)) - 2;
                int expected_pos = -1;
                for (int i = max(0, key); i < n; i++)
                    if (truth[after][i].first > truth[before][i].first)
                    {
                        expected_pos = i;
                        break;
                    }
                assert(source::find(roots[before], roots[after], 0, n, key) == expected_pos);
                persistent_checks++;
            }
        }
        set<source::Node *> allocated;
        auto collect = [&](auto &&self, source::Node *p) -> void
        {
            if (!p || !allocated.insert(p).second)
                return;
            self(self, p->l);
            self(self, p->r);
        };
        for (auto p : roots)
            collect(collect, p);
        for (auto p : allocated)
            delete p;
    }
    cout << certificates << " source Splay certificates; "
         << persistent_checks << " source persistent query pairs PASS\n";
}
