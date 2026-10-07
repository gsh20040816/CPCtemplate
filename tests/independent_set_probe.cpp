#include "../src/compact/independent_set.hpp"

long long checks = 0, runs = 0;

void need(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}

int brute(int n, int m, const vector<pair<int, int>> &edges)
{
    vector<int> adj(n);
    for (auto [u, v] : edges) adj[u - 1] |= 1 << (v - 1);
    int best = 0;
    for (int mask = 0; mask < (1 << (n + m)); mask++)
    {
        bool ok = true;
        for (int u = 0; u < n; u++)
        {
            if ((mask >> u & 1) && (adj[u] & (mask >> n))) ok = false;
        }
        if (ok) best = max(best, __builtin_popcount((unsigned)mask));
    }
    return best;
}

void check(BipartiteMatching &g, const vector<pair<int, int>> &edges, int want)
{
    runs++;
    auto [a, b] = independent_set(g);
    need((int)(a.size() + b.size()) == want);
    need(is_sorted(a.begin(), a.end()) && is_sorted(b.begin(), b.end()));
    vector<int> x(g.n + 1), y(g.m + 1);
    for (int u : a)
    {
        need(1 <= u && u <= g.n);
        need(!x[u]++);
    }
    for (int v : b)
    {
        need(1 <= v && v <= g.m);
        need(!y[v]++);
    }
    for (auto [u, v] : edges) need(!x[u] || !y[v]);
    auto [c, d] = g.cover();
    need((int)(c.size() + d.size()) == g.n + g.m - want);
    for (int u : c)
    {
        need(1 <= u && u <= g.n);
        need(!x[u]++);
    }
    for (int v : d)
    {
        need(1 <= v && v <= g.m);
        need(!y[v]++);
    }
    for (int u = 1; u <= g.n; u++) need(x[u] == 1);
    for (int v = 1; v <= g.m; v++) need(y[v] == 1);
    int size = 0;
    for (int u = 1; u <= g.n; u++)
        if (g.l[u])
        {
            int v = g.l[u];
            need(1 <= v && v <= g.m && g.r[v] == u);
            need(find(g.g[u].begin(), g.g[u].end(), v) != g.g[u].end());
            size++;
        }
    for (int v = 1; v <= g.m; v++)
    {
        if (g.r[v]) need(1 <= g.r[v] && g.r[v] <= g.n && g.l[g.r[v]] == v);
    }
    need(size == g.n + g.m - want);
}

int main(int argc, char **)
{
    try
    {
        for (int n = 0; n <= 4; n++)
            for (int m = 0; m <= 4; m++)
                for (int mask = 0; mask < (1 << (n * m)); mask++)
                {
                    BipartiteMatching g(n, m);
                    vector<pair<int, int>> edges;
                    for (int u = 1; u <= n; u++)
                        for (int v = 1; v <= m; v++)
                            if (mask >> ((u - 1) * m + v - 1) & 1)
                            {
                                g.add(u, v);
                                edges.push_back({u, v});
                            }
                    int want = brute(n, m, edges);
                    check(g, edges, want);
                    check(g, edges, want);
                }
        mt19937 rng(3355310);
        for (int tc = 0; tc < 300; tc++)
        {
            int n = 1 + rng() % 6, m = 1 + rng() % 6;
            BipartiteMatching g(n, m);
            vector<pair<int, int>> edges;
            for (int step = 0; step < 12; step++)
            {
                int u = 1 + rng() % n, v = 1 + rng() % m;
                auto old = g;
                auto old_edges = edges;
                g.add(u, v);
                edges.push_back({u, v});
                int want = brute(n, m, edges);
                check(g, edges, want);
                check(g, edges, want);
                check(old, old_edges, brute(n, m, old_edges));
                need(old.g != g.g);
            }
        }
        if (argc == 1)
        {
            int n = 100000;
            BipartiteMatching g(n, n);
            vector<pair<int, int>> e;
            for (int u = 1; u < n; u++)
            {
                g.add(u, u + 1);
                e.push_back({u, u + 1});
            }
            check(g, e, n + 1);
            for (int u = 1; u <= n; u++)
            {
                g.add(u, u);
                e.push_back({u, u});
            }
            check(g, e, n);
            check(g, e, n);
            BipartiteMatching empty(0, n);
            check(empty, {}, n);
        }
        cout << "PASS " << runs << " runs " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
