#include "../src/compact/negative_cost_flow.hpp"
#include <iostream>
#include <random>
using namespace std;

void check(int n, const vector<array<int, 4>> &edges, long long limit = LLONG_MAX)
{
    vector<int> balance(n + 1), value(edges.size());
    int best_flow = -1;
    long long best_cost = 0;
    auto dfs = [&](auto &&self, int i, long long cost) -> void
    {
        if (i == (int)edges.size())
        {
            for (int u = 2; u < n; u++)
                if (balance[u]) return;
            if (balance[1] > limit) return;
            if (balance[1] > best_flow || (balance[1] == best_flow && cost < best_cost))
            {
                best_flow = balance[1];
                best_cost = cost;
            }
            return;
        }
        auto [u, v, cap, w] = edges[i];
        for (int f = 0; f <= cap; f++)
        {
            balance[u] += f;
            balance[v] -= f;
            self(self, i + 1, cost + f * w);
            balance[u] -= f;
            balance[v] += f;
        }
    };
    dfs(dfs, 0, 0);
    NegativeCostFlow g(n);
    for (auto [u, v, cap, w] : edges) g.add(u, v, cap, w);
    auto [flow, cost] = g.solve(1, n, limit);
    assert(flow == best_flow && cost == best_cost);
    fill(balance.begin(), balance.end(), 0);
    long long actual = 0;
    for (int i = 0; i < (int)edges.size(); i++)
    {
        auto [u, v, cap, w] = edges[i];
        auto f = g.used(i);
        assert(0 <= f && f <= cap);
        balance[u] += f;
        balance[v] -= f;
        actual += f * w;
    }
    assert(balance[1] == flow && balance[n] == -flow && actual == cost);
    for (int u = 2; u < n; u++) assert(!balance[u]);
}

int main()
{
    mt19937 rng(7173);
    for (int trial = 0; trial < 8000; trial++)
    {
        int n = rng() % 4 + 2;
        vector<array<int, 4>> edges;
        for (int i = 0, m = rng() % 9; i < m; i++)
            edges.push_back({int(rng() % n + 1),
                             int(rng() % n + 1),
                             int(rng() % 3),
                             int(rng() % 9) - 4});
        check(n, edges);
        check(n, edges, rng() % 5);
    }
    check(4, {{1, 4, 2, 3}, {2, 3, 2, -4}, {3, 2, 1, 1}, {2, 2, 2, -3}});
    check(3, {{2, 1, 2, -4}, {1, 3, 1, 5}, {1, 2, 1, 0}});
    for (long long w : {-LLONG_MAX, LLONG_MAX})
    {
        NegativeCostFlow g(2);
        g.add(1, 2, LLONG_MAX, w);
        auto [f, c] = g.solve(1, 2);
        assert(f == LLONG_MAX && c == (__int128)LLONG_MAX * w && g.used(0) == f);
    }
    NegativeCostFlow loop(3);
    loop.add(2, 2, LLONG_MAX, -LLONG_MAX);
    auto [f, c] = loop.solve(1, 3);
    assert(f == 0 && c == -(__int128)LLONG_MAX * LLONG_MAX);
    assert(loop.used(0) == LLONG_MAX);
    cout << "NegativeCostFlow: 8000 exhaustive integral-flow oracles, "
            "limited/unlimited max-value/min-cost lexicographic optimum, certificates, "
            "disconnected "
            "negative cycles, self-loops and signed64 extremes PASS\n";
}
