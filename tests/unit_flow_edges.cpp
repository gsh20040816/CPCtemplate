#include "../src/compact/unit_flow_edges.hpp"
#include <iostream>
#include <random>
using namespace std;

int main()
{
    mt19937 rng(214);
    for (int trial = 0; trial < 5000; trial++)
    {
        int n = rng() % 4 + 2, m = rng() % 8;
        vector<array<int, 3>> edges;
        Dinic g(n);
        vector<int> ids, indices;
        for (int i = 0; i < m; i++)
        {
            int u = rng() % n + 1, v = rng() % n + 1, cap = rng() % 3;
            edges.push_back({u, v, cap});
            int id = g.add(u, v, cap);
            if (cap == 1) ids.push_back(id), indices.push_back(i);
        }
        int best = -1;
        vector<int> balance(n + 1), flow(m);
        vector<array<bool, 2>> want(ids.size());
        auto dfs = [&](auto &&self, int i) -> void
        {
            if (i == m)
            {
                for (int u = 2; u < n; u++)
                    if (balance[u]) return;
                if (balance[1] < best) return;
                if (balance[1] > best)
                {
                    best = balance[1];
                    for (auto &x : want) x = {false, true};
                }
                for (int j = 0; j < (int)ids.size(); j++)
                {
                    want[j][0] |= flow[indices[j]] == 1;
                    want[j][1] &= flow[indices[j]] == 1;
                }
                return;
            }
            auto [u, v, cap] = edges[i];
            for (int f = 0; f <= cap; f++)
            {
                flow[i] = f;
                balance[u] += f;
                balance[v] -= f;
                self(self, i + 1);
                balance[u] -= f;
                balance[v] += f;
            }
        };
        dfs(dfs, 0);
        assert(g.flow(1, n) == best);
        assert(unit_flow_edges(g, ids) == want);
        reverse(ids.begin(), ids.end());
        reverse(want.begin(), want.end());
        assert(unit_flow_edges(g, ids) == want);
    }
    Dinic g(2);
    int loop = g.add(1, 1, 1);
    int path = g.add(1, 2, 1);
    assert(g.flow(1, 2) == 1);
    auto a = unit_flow_edges(g, {loop, path, loop});
    assert(a[0][0] && !a[0][1] && a[1][0] && a[1][1] && a[2] == a[0]);
    const int n = 100000;
    Dinic chain(n);
    vector<int> ids;
    for (int u = 1; u < n; u++) ids.push_back(chain.add(u, u + 1, 1));
    chain.add(1, n, 0);
    assert(chain.flow(1, n) == 1);
    for (auto x : unit_flow_edges(chain, ids)) assert(x[0] && x[1]);
    cout << "Unit flow edges: 5000 exhaustive integral maximum-flow union/intersection "
            "oracles, zero capacities, cycles, unit self-loop, repeated/reordered ids "
            "PASS\n";
}
