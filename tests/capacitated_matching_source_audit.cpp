// The runner inserts Dinic and the exact Markdown example before this probe.
namespace source
{
#include "fixtures/matching_sources/kuangbin-capacity.inc"
}
long long checks = 0, cases = 0;
void need(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}
int optimum(int n, const vector<long long> &cap,
            const vector<pair<int, int>> &edges)
{
    vector<int> adj(cap.size());
    for (auto [u, v] : edges)
        adj[v] |= 1 << u;
    vector<bool> dp(1 << n);
    dp[0] = true;
    for (int v = 0; v < (int)cap.size(); v++)
    {
        auto next = dp;
        for (int mask = 0; mask < (1 << n); mask++)
            if (dp[mask])
            {
                int avail = adj[v] & ~mask;
                for (int sub = avail; sub; sub = (sub - 1) & avail)
                    if (__builtin_popcount((unsigned)sub) <= cap[v])
                        next[mask | sub] = true;
            }
        dp.swap(next);
    }
    int best = 0;
    for (int mask = 0; mask < (1 << n); mask++)
        if (dp[mask])
            best = max(best, __builtin_popcount((unsigned)mask));
    return best;
}
void certificate(int n, const vector<long long> &cap,
                 const vector<pair<int, int>> &edges,
                 const vector<pair<int, int>> &ans, int expected)
{
    need((int)ans.size() == expected);
    vector<bool> used(n);
    vector<int> count(cap.size());
    set<pair<int, int>> present(edges.begin(), edges.end());
    for (auto [u, v] : ans)
    {
        need(0 <= u && u < n);
        need(0 <= v && v < (int)cap.size());
        need(!used[u] && present.count({u, v}));
        used[u] = true;
        need(++count[v] <= cap[v]);
    }
}
void test(int n, const vector<long long> &cap,
          const vector<pair<int, int>> &edges, int expected = -1,
          bool upstream = true)
{
    cases++;
    int m = cap.size();
    if (expected == -1) expected = optimum(n, cap, edges);
    for (int repeat = 0; repeat < 2; repeat++)
        certificate(n, cap, edges, capacity_matching(n, cap, edges), expected);
    if (!upstream) return;
    source::uN = n;
    source::vN = m;
    for (int u = 0; u < n; u++)
        fill(source::g[u], source::g[u] + m, 0);
    for (auto [u, v] : edges)
        source::g[u][v] = 1;
    for (int v = 0; v < m; v++)
        source::num[v] = cap[v];
    for (int repeat = 0; repeat < 2; repeat++)
    {
        need(source::hungary() == expected);
        vector<pair<int, int>> ans;
        for (int v = 0; v < m; v++)
        {
            need(0 <= source::linker[v][0]);
            need(source::linker[v][0] <= min<long long>(n, cap[v]));
            for (int i = 1; i <= source::linker[v][0]; i++)
                ans.push_back({source::linker[v][i], v});
        }
        certificate(n, cap, edges, ans, expected);
    }
}
void exhaustive()
{
    for (int n = 0; n <= 3; n++)
        for (int m = 0; m <= 3; m++)
        {
            int configs = 1;
            for (int v = 0; v < m; v++) configs *= n + 2;
            for (int mask = 0; mask < (1 << (n * m)); mask++)
            {
                vector<pair<int, int>> edges;
                for (int u = 0; u < n; u++)
                    for (int v = 0; v < m; v++)
                        if (mask >> (u * m + v) & 1)
                            edges.push_back({u, v});
                for (int code = 0; code < configs; code++)
                {
                    int x = code;
                    vector<long long> cap(m);
                    for (auto &c : cap)
                    {
                        c = x % (n + 2);
                        x /= n + 2;
                    }
                    test(n, cap, edges);
                }
            }
        }
}
void increment()
{
    Dinic g(6);
    g.add(5, 1, 1);
    g.add(5, 2, 1);
    g.add(3, 6, 1);
    g.add(4, 6, 1);
    int a = g.add(1, 4, 1);
    need(g.flow(5, 6) == 1);
    int b = g.add(1, 3, 1);
    int c = g.add(2, 4, 1);
    need(g.flow(5, 6) == 1);
    need(g.used(a) == 0 && g.used(b) == 1 && g.used(c) == 1);
    need(g.flow(5, 6) == 0);
    test(2, {1, 1}, {{0, 1}, {0, 0}, {1, 1}}, 2);
}
int main(int argc, char **argv)
{
    if (argc > 1 && string(argv[1]) == "source-overflow")
    {
        source::uN = 1010;
        source::vN = 1;
        source::num[0] = 1010;
        for (int u = 0; u < 1010; u++) source::g[u][0] = 1;
        cout << source::hungary() << '\n';
        return 0;
    }
    try
    {
        increment();
        test(3, {3}, {{0, 0}, {1, 0}, {2, 0}}, 3);
        test(3, {0}, {{0, 0}, {1, 0}, {2, 0}}, 0);
        test(2, {2}, {{0, 0}, {0, 0}, {1, 0}}, 2);
        test(3, {LLONG_MAX, LLONG_MAX}, {{0, 0}, {1, 0}, {2, 1}}, 3, false);
        if (argc > 1)
        {
            cout << "MUTANT_SURVIVED\n";
            return 0;
        }
        exhaustive();
        mt19937 rng(20261008);
        for (int i = 0; i < 300; i++)
        {
            int n = 1 + rng() % 8;
            int m = 1 + rng() % 6;
            vector<long long> cap(m);
            for (auto &c : cap) c = rng() % (n + 3);
            vector<pair<int, int>> edges;
            for (int j = 0; j < i % 40; j++)
                edges.push_back({rng() % n, rng() % m});
            test(n, cap, edges);
        }
        vector<pair<int, int>> full, star;
        for (int u = 0; u < 1009; u++)
        {
            star.push_back({u, 0});
            for (int v = 0; v < 510; v++) full.push_back({u, v});
        }
        test(1009, {INT_MAX}, star, 1009);
        test(1009, vector<long long>(510, 2), full, 1009);
        star.push_back({1009, 0});
        test(1010, {1010}, star, 1010, false);
        // Edges force a long residual augmenting path; recursion is retained.
        int n = 50000;
        vector<pair<int, int>> chain;
        for (int u = 0; u + 1 < n; u++)
        {
            chain.push_back({u, u});
            chain.push_back({u, u + 1});
        }
        chain.push_back({n - 1, 0});
        test(n, vector<long long>(n, 1), chain, n, false);
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
