#include "../src/compact/dominator_tree.hpp"
#include <iostream>
#include <queue>
#include <random>
using namespace std;

vector<int> reachable(const DominatorTree &t, int root, int removed)
{
    vector<int> seen(t.n + 1);
    queue<int> q;
    if (root != removed)
    {
        seen[root] = 1;
        q.push(root);
    }
    while (!q.empty())
    {
        int u = q.front();
        q.pop();
        for (int v : t.g[u])
            if (v != removed && !seen[v])
            {
                seen[v] = 1;
                q.push(v);
            }
    }
    return seen;
}

void check(DominatorTree &t)
{
    for (int root = 1; root <= t.n; root++)
    {
        t.build(root);
        auto seen = reachable(t, root, 0);
        vector<vector<int>> dominates(t.n + 1, vector<int>(t.n + 1));
        for (int u = 1; u <= t.n; u++)
        {
            auto without = reachable(t, root, u);
            for (int v = 1; v <= t.n; v++) dominates[u][v] = seen[v] && !without[v];
        }
        vector<int> size(t.n + 1);
        for (int i = t.timer; i >= 1; i--)
        {
            int u = t.vertex[i];
            size[u]++;
            if (u != root) size[t.idom[u]] += size[u];
        }
        for (int u = 1; u <= t.n; u++)
            assert(size[u] == accumulate(dominates[u].begin(), dominates[u].end(), 0));
        for (int v = 1; v <= t.n; v++)
        {
            if (!seen[v])
            {
                assert(t.idom[v] == 0);
                continue;
            }
            if (v == root)
            {
                assert(t.idom[v] == root);
                continue;
            }
            int expected = 0;
            for (int u = 1; u <= t.n; u++)
                if (u != v && dominates[u][v])
                {
                    bool closest = true;
                    for (int w = 1; w <= t.n; w++)
                        if (w != v && dominates[w][v] && !dominates[w][u])
                            closest = false;
                    if (closest)
                    {
                        assert(!expected);
                        expected = u;
                    }
                }
            assert(expected && t.idom[v] == expected);
        }
    }
}

int main()
{
    for (int n = 1; n <= 4; n++)
        for (int mask = 0; mask < (1 << (n * (n - 1))); mask++)
        {
            DominatorTree t(n);
            int bit = 0;
            for (int u = 1; u <= n; u++)
                for (int v = 1; v <= n; v++)
                    if (u != v && (mask >> bit++ & 1)) t.add(u, v);
            check(t);
        }
    mt19937 rng(20260914);
    for (int trial = 0; trial < 2000; trial++)
    {
        int n = rng() % 9 + 1;
        DominatorTree t(n);
        for (int i = 0, m = rng() % 45; i < m; i++) t.add(rng() % n + 1, rng() % n + 1);
        check(t);
        t.add(rng() % n + 1, rng() % n + 1);
        assert(t.idom.empty());
        check(t);
    }
    const int n = 200000;
    DominatorTree chain(n);
    for (int u = 1; u < n; u++) chain.add(u, u + 1);
    chain.build(1);
    for (int u = 2; u <= n; u++) assert(chain.idom[u] == u - 1);
    chain.add(n, 1);
    chain.build(n / 2);
    for (int u = 1; u <= n; u++)
        assert(chain.idom[u] == (u == n / 2 ? u : u == 1 ? n : u - 1));
    DominatorTree star(n);
    for (int u = 2; u <= n; u++) star.add(1, u);
    star.build(1);
    for (int u = 1; u <= n; u++) assert(star.idom[u] == 1);
    cout << "DominatorTree: exhaustive n<=4 all roots, 2000 random multigraphs with "
            "mutation, deletion-reachability oracle and 200000-node chain/cycle/star "
            "PASS\n";
}
