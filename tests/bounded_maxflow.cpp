#include "../src/compact/bounded_maxflow.hpp"
#include <iostream>
#include <random>
using namespace std;

void check(int n, int s, int t, const vector<array<int, 4>> &edges)
{
    optional<long long> best;
    vector<long long> balance(n + 1);
    auto dfs = [&](auto &&self, int i) -> void
    {
        if (i == (int)edges.size())
        {
            for (int u = 1; u <= n; u++)
                if (u != s && u != t && balance[u]) return;
            if (!best || balance[s] > *best) best = balance[s];
            return;
        }
        auto [u, v, lo, hi] = edges[i];
        for (int f = lo; f <= hi; f++)
        {
            balance[u] += f;
            balance[v] -= f;
            self(self, i + 1);
            balance[u] -= f;
            balance[v] += f;
        }
    };
    dfs(dfs, 0);
    BoundedMaxFlow f(n);
    for (auto [u, v, lo, hi] : edges) f.add(u, v, lo, hi);
    assert(f.solve(s, t) == best);
    if (!best) return;
    fill(balance.begin(), balance.end(), 0);
    for (int i = 0; i < (int)edges.size(); i++)
    {
        auto [u, v, lo, hi] = edges[i];
        auto x = f.used(i);
        assert(lo <= x && x <= hi);
        balance[u] += x;
        balance[v] -= x;
    }
    assert(balance[s] == *best && balance[t] == -*best);
    for (int u = 1; u <= n; u++)
        if (u != s && u != t) assert(!balance[u]);
}

int main()
{
    mt19937 rng(115);
    for (int trial = 0; trial < 6000; trial++)
    {
        int n = rng() % 4 + 2;
        vector<array<int, 4>> edges;
        for (int i = 0, m = rng() % 8; i < m; i++)
        {
            int lo = rng() % 3, hi = lo + rng() % 3;
            edges.push_back({int(rng() % n + 1), int(rng() % n + 1), lo, hi});
        }
        check(n, 1, n, edges);
    }
    check(3, 1, 3, {{3, 1, 2, 4}});
    check(3, 1, 3, {{1, 2, 2, 2}});
    for (bool reverse : {false, true})
    {
        BoundedMaxFlow f(2);
        f.add(reverse ? 2 : 1, reverse ? 1 : 2, LLONG_MAX, LLONG_MAX);
        assert(f.solve(1, 2) == (reverse ? -LLONG_MAX : LLONG_MAX));
        assert(f.used(0) == LLONG_MAX);
    }
    BoundedMaxFlow wide(2);
    wide.add(1, 2, 0, LLONG_MAX);
    assert(wide.solve(1, 2) == LLONG_MAX && wide.used(0) == LLONG_MAX);
    cout << "BoundedMaxFlow: 6000 independent edge-flow enumerations, signed net flow, "
            "infeasibility, loops/parallel edges, solution certificates and LLONG_MAX "
            "boundaries PASS\n";
}
