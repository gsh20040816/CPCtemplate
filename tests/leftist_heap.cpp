#include "../src/compact/leftist_heap.hpp"
#include <climits>
#include <functional>
#include <iostream>
#include <random>
#include <set>
using namespace std;

int main()
{
    mt19937 rng(3377);
    for (int trial = 0; trial < 100; trial++)
    {
        LeftistHeap h;
        vector<int> roots(12);
        vector<set<pair<long long, int>>> ref(12);
        for (int step = 0; step < 2000; step++)
        {
            int a = rng() % 12, b = rng() % 12;
            int op = rng() % 3;
            if (op == 0)
            {
                long long key = int(rng() % 21) - 10;
                if (step % 31 == 0) key = LLONG_MIN;
                if (step % 37 == 0) key = LLONG_MAX;
                int id = h.singleton(key);
                roots[a] = h.meld(roots[a], id);
                ref[a].insert({key, id});
            }
            else if (op == 1 && a != b)
            {
                roots[a] = h.meld(roots[a], roots[b]);
                roots[b] = 0;
                ref[a].insert(ref[b].begin(), ref[b].end());
                ref[b].clear();
            }
            else if (!ref[a].empty())
            {
                assert(make_pair(h.t[roots[a]].key, roots[a]) == *ref[a].begin());
                roots[a] = h.pop(roots[a]);
                ref[a].erase(ref[a].begin());
            }
            set<int> seen;
            for (int k = 0; k < 12; k++)
            {
                set<pair<long long, int>> got;
                function<int(int)> dfs = [&](int x)
                {
                    if (!x) return 0;
                    assert(seen.insert(x).second);
                    auto node = h.t[x];
                    got.insert({node.key, x});
                    for (int y : {node.l, node.r})
                        if (y)
                            assert(make_pair(node.key, x) <= make_pair(h.t[y].key, y));
                    int l = dfs(node.l), r = dfs(node.r);
                    assert(l >= r && node.dist == r + 1);
                    return node.dist;
                };
                dfs(roots[k]);
                assert(got == ref[k]);
            }
        }
    }
    for (bool reverse : {false, true})
    {
        LeftistHeap h;
        int root = 0;
        const int n = 200000;
        for (int i = 0; i < n; i++)
            root = h.meld(root, h.singleton(reverse ? n - i - 1 : i));
        for (int i = 0; i < n; i++)
        {
            assert(h.t[root].key == i);
            root = h.pop(root);
        }
        assert(root == 0);
    }
    cout << "LeftistHeap: independent ordered sets, heap order, leftist ranks, "
            "disjointness, ties, int64 extremes and 200000 nodes PASS\n";
}
