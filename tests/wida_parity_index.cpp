#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include "fixtures/wida_parity_index/08A.cpp"
using namespace std;

void remember(Node *p, set<Node *> &seen)
{
    if (!p || !seen.insert(p).second)
        return;
    remember(p->l, seen);
    remember(p->r, seen);
}

int main()
{
    mt19937 rng(63246177);
    int checked = 0;
    for (int trial = 0; trial < 100; trial++)
    {
        int n = 1 + rng() % 50;
        vector<Node *> roots{nullptr};
        vector<vector<int>> counts(1, vector<int>(n));
        for (int step = 0; step < 100; step++)
        {
            int v = rng() % roots.size();
            int x = rng() % n;
            int delta = int(rng() % 7) - 3;
            delta = max(delta, -counts[v][x]);
            auto next = counts[v];
            next[x] += delta;
            roots.push_back(add(roots[v], 0, n, x, delta));
            counts.push_back(next);
            for (int repeat = 0; repeat < 10; repeat++)
            {
                int before = rng() % roots.size();
                int after = rng() % roots.size();
                bool valid = true;
                for (int i = 0; i < n; i++)
                    valid &= counts[before][i] <= counts[after][i];
                if (!valid)
                    before = 0;
                vector<int> all, odd;
                for (int i = n - 1; i >= 0; i--)
                {
                    int c = counts[after][i] - counts[before][i];
                    all.insert(all.end(), c, i);
                    if (i % 2)
                        odd.insert(odd.end(), c, i);
                }
                int k = rng() % (all.size() + 5);
                int first = 0;
                if (!odd.empty())
                    first = odd[0];
                if (k < int(all.size()))
                    first = max(first, all[k]);
                assert(query1(roots[after], roots[before], 0, n, k) == first);
                array<int, 3> second{0, 0, k - int(odd.size())};
                if (k < int(odd.size()))
                {
                    int pos = odd[k];
                    int count = std::count(odd.begin(), odd.end(), pos);
                    int larger = std::count_if(odd.begin(), odd.end(), [&](int a)
                    {
                        return a > pos;
                    });
                    second = {pos, count, k - larger};
                }
                assert(query2(roots[after], roots[before], 0, n, k) == second);
                checked++;
            }
        }
        set<Node *> nodes;
        for (Node *p : roots)
            remember(p, nodes);
        for (Node *p : nodes)
            delete p;
    }
    cout << checked << " original parity-query semantic certificates PASS\n";
}
