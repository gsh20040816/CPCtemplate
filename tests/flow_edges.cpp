#include "../src/compact/flow.hpp"

long long cut_oracle(int n, const vector<tuple<int, int, long long>> &edges)
{
    long long ans = LLONG_MAX;
    for (int mask = 0; mask < (1 << n); mask++)
    {
        if (!(mask & 1) || (mask >> (n - 1) & 1)) continue;
        long long sum = 0;
        for (auto [u, v, c] : edges)
            if ((mask >> (u - 1) & 1) && !(mask >> (v - 1) & 1)) sum += c;
        ans = min(ans, sum);
    }
    return ans;
}

void certificate(Dinic &g, long long flow)
{
    vector<__int128> balance(g.n + 1);
    for (int id = 0; id < int(g.e.size()); id += 2)
    {
        auto [u, v, c, f] = g.get_edge(id);
        assert(0 <= f && f <= c);
        assert(g.e[id].cap == c - f);
        assert(g.e[id ^ 1].cap == f);
        assert(g.used(id) == f);
        balance[u] -= f;
        balance[v] += f;
    }
    assert(balance[1] == -(__int128)flow);
    assert(balance[g.n] == flow);
    for (int u = 2; u < g.n; u++) assert(balance[u] == 0);
}

int main()
{
    mt19937 rng(76135);
    for (int n = 2; n <= 7; n++)
        for (int trial = 0; trial < 1000; trial++)
        {
            Dinic g(n);
            vector<tuple<int, int, long long>> edges;
            for (int i = 0; i < 20; i++)
            {
                int u = rng() % n + 1, v = rng() % n + 1;
                long long c = rng() % 10;
                int id = g.add(u, v, c);
                edges.push_back({u, v, c});
                assert(g.get_edge(id) == make_tuple(u, v, c, 0LL));
            }
            long long f = g.flow(1, n, rng() % 10);
            certificate(g, f);
            // Keeping each current flow while raising capacities preserves feasibility.
            for (int id = 0; id < int(edges.size()); id++)
            {
                auto &[u, v, c] = edges[id];
                c += rng() % 10;
                g.change_edge(2 * id, c, g.used(2 * id));
            }
            f += g.flow(1, n);
            assert(f == cut_oracle(n, edges));
            certificate(g, f);
            auto reachable = g.cut(1);
            long long cap = 0;
            for (auto [u, v, c] : edges)
                if (find(reachable.begin(), reachable.end(), u) != reachable.end() &&
                    find(reachable.begin(), reachable.end(), v) == reachable.end())
                    cap += c;
            assert(cap == f);
            // Reset every edge together, then shrink capacities and solve afresh.
            for (int id = 0; id < int(edges.size()); id++)
            {
                auto &[u, v, c] = edges[id];
                c = rng() % 4;
                g.change_edge(2 * id, c, 0);
            }
            f = g.flow(1, n);
            assert(f == cut_oracle(n, edges));
            certificate(g, f);
        }
    Dinic g(4);
    for (auto [u, v] : vector<pair<int, int>>{{1, 2}, {2, 4}, {2, 3}, {3, 2}, {3, 3}})
    {
        int id = g.add(u, v, 10);
        g.change_edge(id, 10, u == 1 || v == 4 ? 2 : 3);
    }
    certificate(g, 2); // Feasible initial path flow plus cycle and self-loop.
    assert(g.flow(1, 4) == 8);
    certificate(g, 10);
    Dinic big(2);
    int id = big.add(1, 2, LLONG_MAX);
    big.change_edge(id, LLONG_MAX, LLONG_MAX - 1);
    assert(big.flow(1, 2) == 1);
    certificate(big, LLONG_MAX);
    big.change_edge(id, 0, 0);
    assert(big.flow(1, 2) == 0);
    cout << "Dinic edge API: exhaustive-cut oracle after capacity edits, "
            "residual/conservation certificates and int64 limits PASS\n";
}
