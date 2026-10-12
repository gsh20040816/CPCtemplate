#include "../src/compact/weighted_blossom.hpp"

using I = __int128;
using ll = long long;
long long checks = 0;

void verify(WeightedBlossom &g, bool cardinality)
{
    int n = g.n;
    vector<pair<int, I>> dp(n <= 12 ? 1 << n : 1);
    auto better = [&](pair<int, I> a, pair<int, I> b)
    {
        if (cardinality) return a > b;
        return a.second > b.second;
    };
    for (int mask = 1; mask < (int)dp.size(); mask++)
    {
        int u = countr_zero(unsigned(mask));
        int rest = mask ^ (1 << u);
        dp[mask] = dp[rest];
        for (int v = u + 1; v < n; v++)
            if ((rest >> v & 1) && g.weight[u + 1][v + 1] != -g.INF)
            {
                auto next = dp[rest ^ (1 << v)];
                next.first++;
                next.second += g.weight[u + 1][v + 1];
                if (better(next, dp[mask])) dp[mask] = next;
            }
    }
    auto r = g.solve(cardinality);
    if (n <= 12)
    {
        assert(r.weight == dp.back().second);
        if (cardinality) assert(r.pairs == dp.back().first);
    }
    assert(r.mate.size() == size_t(n + 1) && r.mate[0] == 0);
    int pairs = 0;
    I total = 0;
    for (int u = 1; u <= n; u++)
    {
        int v = r.mate[u];
        if (!v) continue;
        assert(1 <= v && v <= n && v != u && r.mate[v] == u);
        assert(g.weight[u][v] != -g.INF);
        if (!cardinality) assert(g.weight[u][v] > 0);
        if (u < v)
        {
            pairs++;
            total += g.weight[u][v];
        }
    }
    assert(pairs == r.pairs && total == r.weight);
    // A separate LP dual certificate checks optimality independently of the DP.
    vector<vector<int>> members(2 * n + 1, vector<int>(n + 1));
    function<void(int, int)> collect = [&](int x, int b)
    {
        if (x <= n) members[b][x] = 1;
        else for (int v : g.flower[x]) collect(v, b);
    };
    I dual = 0;
    for (int u = 1; u <= n; u++)
    {
        assert(g.label[u] >= 0);
        if (!r.mate[u]) assert(g.label[u] == 0);
        dual += g.label[u];
    }
    for (int b = n + 1; b <= g.top; b++)
        if (g.base[b])
        {
            collect(b, b);
            int count = accumulate(members[b].begin(), members[b].end(), 0);
            assert(count % 2 == 1 && count >= 3 && g.label[b] >= 0);
            dual += I(count / 2) * g.label[b];
            int inside = 0;
            for (int u = 1; u <= n; u++)
                if (members[b][u] && r.mate[u] > u && members[b][r.mate[u]]) inside++;
            if (g.label[b]) assert(inside == count / 2);
        }
    I bound = 0;
    for (int u = 1; u <= n; u++)
        for (int v = u + 1; v <= n; v++)
            if (g.weight[u][v] != -g.INF)
                bound = max(bound, max(g.weight[u][v], -g.weight[u][v]));
    I bonus = cardinality ? n * bound + 1 : 0;
    assert(dual == 2 * (r.weight + r.pairs * bonus));
    for (int u = 1; u <= n; u++)
        for (int v = u + 1; v <= n; v++)
            if (g.weight[u][v] != -g.INF && g.weight[u][v] + bonus > 0)
            {
                I cover = g.label[u] + g.label[v];
                for (int b = n + 1; b <= g.top; b++)
                    if (g.base[b] && members[b][u] && members[b][v]) cover += g.label[b];
                assert(cover >= 2 * (g.weight[u][v] + bonus));
                if (r.mate[u] == v) assert(cover == 2 * (g.weight[u][v] + bonus));
            }
    checks++;
}

int main()
{
    // Test assertions must stay active even when the implementation has NDEBUG.
    for (int n = 0; n <= 4; n++)
    {
        vector<pair<int, int>> edges;
        for (int u = 1; u <= n; u++)
            for (int v = u + 1; v <= n; v++) edges.push_back({u, v});
        int possibilities = 1 << (2 * edges.size());
        for (int mask = 0; mask < possibilities; mask++)
        {
            WeightedBlossom g(n);
            int code = mask;
            for (auto [u, v] : edges)
            {
                int t = code % 4;
                code /= 4;
                if (t) g.add_edge(u, v, array<ll, 4>{0, -2, 0, 3}[t]);
            }
            verify(g, false);
            verify(g, true);
            verify(g, false);
        }
    }
    for (int mask = 0; mask < (1 << 10); mask++)
    {
        WeightedBlossom g(5);
        int k = 0;
        for (int u = 1; u <= 5; u++)
            for (int v = u + 1; v <= 5; v++)
                if (mask >> k++ & 1) g.add_edge(u, v, 1);
        verify(g, false);
        verify(g, true);
    }
    mt19937_64 rng(981267);
    for (int test = 0; test < 3500; test++)
    {
        int n = 1 + rng() % 12;
        WeightedBlossom g(n);
        for (int u = 1; u <= n; u++)
            for (int v = u; v <= n; v++)
                if (rng() % 3)
                {
                    ll w = ll(rng() % 51) - 20;
                    if (test % 5 == 0) w = ll(rng() % 5) - 2;
                    if (test % 7 == 0) w = array<ll, 4>{LLONG_MIN, LLONG_MAX, -1, 0}[rng() % 4];
                    g.add_edge(u, v, w);
                    if (w != LLONG_MIN) g.add_edge(u, v, w - 1);
                }
        verify(g, false);
        verify(g, true);
        // Addition after a solve must rebuild contractions, labels and matching.
        g.add_edge(1, n, ll(rng() % 100));
        verify(g, true);
        verify(g, false);
    }
    cout << checks << " independent optimum and witness checks PASS\n";
    return 0;
}
