#include "../src/compact/min_cycle.hpp"

#define CHECK(x) do { if (!(x)) abort(); } while (false)
using I = MinCycle::I;

optional<I> brute(const MinCycle &g)
{
    vector<vector<long long>> w(g.n, vector<long long>(g.n, -1));
    for (auto [u, v, c] : g.e)
    {
        if (u == v) continue;
        if (w[u][v] == -1 || c < w[u][v])
            w[u][v] = w[v][u] = c;
    }
    optional<I> best;
    for (int s = 0; s < g.n; s++)
    {
        auto dfs = [&](auto &&self, int u, int mask, int len, I sum) -> void
        {
            if (len >= 3 && w[u][s] != -1)
            {
                I value = sum + w[u][s];
                if (!best || value < *best) best = value;
            }
            for (int v = s + 1; v < g.n; v++)
            {
                if ((mask >> v & 1) || w[u][v] == -1) continue;
                self(self, v, mask | (1 << v), len + 1, sum + w[u][v]);
            }
        };
        dfs(dfs, s, 1 << s, 1, 0);
    }
    return best;
}

void check(const MinCycle &g, optional<I> expected)
{
    auto a = g.solve();
    auto b = g.solve();
    CHECK(a.has_value() == expected.has_value());
    CHECK(b.has_value() == expected.has_value());
    if (!a) return;
    CHECK(a->weight == *expected && b->weight == *expected);
    CHECK(a->vertices == b->vertices && a->edges == b->edges);
    int size = a->vertices.size();
    CHECK(size >= 3 && size <= g.n && (int)a->edges.size() == size);
    set<int> seen;
    I weight = 0;
    for (int i = 0; i < size; i++)
    {
        int u = a->vertices[i], v = a->vertices[(i + 1) % size];
        CHECK(0 <= u && u < g.n && seen.insert(u).second);
        int id = a->edges[i];
        CHECK(0 <= id && id < (int)g.e.size());
        auto e = g.e[id];
        CHECK((e.u == u && e.v == v) || (e.u == v && e.v == u));
        weight += e.w;
    }
    CHECK(weight == a->weight);
}

int main()
{
    check(MinCycle(0), nullopt);
    int exhaustive = 0;
    vector<pair<int, int>> edges;
    for (int i = 0; i < 5; i++)
        for (int j = i + 1; j < 5; j++)
            edges.push_back({i, j});
    for (int mask = 0; mask < 59049; mask++)
    {
        MinCycle g(5);
        int x = mask;
        for (auto [u, v] : edges)
        {
            int t = x % 3;
            x /= 3;
            if (t) g.add(u, v, t == 1 ? 0 : 7);
        }
        check(g, brute(g));
        exhaustive++;
    }
    mt19937 rng(6175);
    vector<long long> weights{0, 1, 2, 17, LLONG_MAX - 1, LLONG_MAX};
    for (int trial = 0; trial < 3000; trial++)
    {
        int n = rng() % 8 + 1;
        MinCycle g(n);
        int m = rng() % 30;
        for (int i = 0; i < m; i++)
        {
            int u = rng() % n, v = rng() % n;
            CHECK(g.add(u, v, weights[rng() % weights.size()]) == i);
        }
        check(g, brute(g));
        MinCycle copy = g;
        copy.add(rng() % n, rng() % n, rng() % 3);
        check(copy, brute(copy));
        check(g, brute(g));
    }
    MinCycle ring(200);
    for (int u = 0; u < 200; u++)
        ring.add(u, (u + 1) % 200, LLONG_MAX);
    check(ring, I(200) * LLONG_MAX);
    MinCycle dense(100);
    for (int u = 0; u < 100; u++)
        for (int v = u + 1; v < 100; v++)
            dense.add(u, v, LLONG_MAX);
    check(dense, I(3) * LLONG_MAX);
    for (int u = 0; u < 100; u++)
        dense.add(u, (u + 1) % 100, 0);
    check(dense, I(0));
    cout << "PASS " << exhaustive << " exhaustive, 3000 random/rebuild/copy, wide-weight ring/dense\n";
}
