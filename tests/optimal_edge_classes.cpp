#include "../src/compact/matching_edges.hpp"
#include "../src/compact/mincut_edges.hpp"
#include <iostream>
#include <random>
using namespace std;

void check_matching(int n, int m, const vector<pair<int, int>> &edges)
{
    int best = -1;
    vector<array<bool, 2>> want(edges.size());
    vector<bool> used(m + 1), taken(edges.size());
    auto dfs = [&](auto &&self, int u, int count) -> void
    {
        if (u > n)
        {
            if (count < best) return;
            if (count > best)
            {
                best = count;
                for (auto &x : want) x = {false, true};
            }
            for (int i = 0; i < (int)edges.size(); i++)
            {
                want[i][0] |= taken[i];
                want[i][1] &= taken[i];
            }
            return;
        }
        self(self, u + 1, count);
        for (int i = 0; i < (int)edges.size(); i++)
        {
            auto [a, v] = edges[i];
            if (a != u || used[v]) continue;
            used[v] = taken[i] = true;
            self(self, u + 1, count + 1);
            used[v] = taken[i] = false;
        }
    };
    dfs(dfs, 1, 0);
    auto [size, got] = matching_edges(n, m, edges);
    assert(size == best && got == want);
}

void check_cut(int n, const vector<array<int, 3>> &edges)
{
    long long best = LLONG_MAX;
    vector<array<bool, 2>> want(edges.size());
    for (int mask = 0; mask < (1 << n); mask++)
    {
        if (!(mask & 1) || (mask >> (n - 1) & 1)) continue;
        long long cost = 0;
        vector<bool> cut(edges.size());
        for (int i = 0; i < (int)edges.size(); i++)
        {
            auto [u, v, c] = edges[i];
            cut[i] = (mask >> (u - 1) & 1) && !(mask >> (v - 1) & 1);
            if (cut[i]) cost += c;
        }
        if (cost > best) continue;
        if (cost < best)
        {
            best = cost;
            for (auto &x : want) x = {false, true};
        }
        for (int i = 0; i < (int)edges.size(); i++)
        {
            want[i][0] |= cut[i];
            want[i][1] &= cut[i];
        }
    }
    Dinic g(n);
    for (auto [u, v, c] : edges) g.add(u, v, c);
    assert(g.flow(1, n) == best);
    auto before = g.e;
    assert(mincut_edges(g, 1, n) == want);
    assert(mincut_edges(g, 1, n) == want);
    for (int i = 0; i < (int)g.e.size(); i++) assert(g.e[i].cap == before[i].cap);
}

int main()
{
    for (int n = 0; n <= 3; n++)
        for (int m = 0; m <= 3; m++)
            for (int mask = 0; mask < (1 << (n * m)); mask++)
            {
                vector<pair<int, int>> edges;
                for (int u = 1; u <= n; u++)
                    for (int v = 1; v <= m; v++)
                        if (mask >> ((u - 1) * m + v - 1) & 1) edges.push_back({u, v});
                check_matching(n, m, edges);
            }
    mt19937 rng(4126);
    for (int trial = 0; trial < 3000; trial++)
    {
        int n = rng() % 5 + 1, m = rng() % 5 + 1;
        vector<pair<int, int>> edges;
        for (int i = 0, k = rng() % 11; i < k; i++)
            edges.push_back({int(rng() % n + 1), int(rng() % m + 1)});
        check_matching(n, m, edges);
        n = rng() % 6 + 2;
        vector<array<int, 3>> arcs;
        for (int i = 0, k = rng() % 18; i < k; i++)
            arcs.push_back(
                {int(rng() % n + 1), int(rng() % n + 1), int(rng() % 5 + 1)});
        check_cut(n, arcs);
    }
    const int n = 100000;
    vector<pair<int, int>> ladder;
    for (int u = 1; u <= n; u++) ladder.push_back({u, u});
    for (int u = 1; u < n; u++) ladder.push_back({u, u + 1});
    auto [size, labels] = matching_edges(n, n, ladder);
    assert(size == n);
    for (int i = 0; i < (int)ladder.size(); i++)
        assert(labels[i][0] == (i < n) && labels[i][1] == (i < n));
    Dinic chain(n);
    for (int u = 1; u < n; u++) chain.add(u, u + 1, 1);
    assert(chain.flow(1, n) == 1);
    for (auto x : mincut_edges(chain, 1, n)) assert(x[0] && !x[1]);
    cout << "Optimal edge classes: exhaustive <=3x3 matching graphs, 3000 random "
            "multigraph matching/cut union-intersection oracles, repeated const "
            "queries; 100000-node ladder/chain PASS\n";
}
