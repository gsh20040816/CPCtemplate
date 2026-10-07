#include "../src/compact/graph.hpp"
namespace matrix_source
{
#include "fixtures/matching_sources/kuangbin-matrix.inc"
}
namespace list_source
{
#include "fixtures/matching_sources/kuangbin-list.inc"
}
namespace hk_source
{
#include "fixtures/matching_sources/kuangbin-hk.inc"
}
namespace wida_source
{
#define main unused_source_main
#include "fixtures/matching_sources/wida-hk.inc"
#undef main
}
long long checks = 0, graphs = 0;
void need(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}
int optimum(int n, int m, const vector<pair<int, int>> &e)
{
    vector<int> dp(1 << m, -1);
    dp[0] = 0;
    for (int u = 0; u < n; u++)
    {
        auto next = dp;
        for (int mask = 0; mask < (1 << m); mask++)
            if (dp[mask] >= 0)
                for (auto [x, v] : e)
                    if (x == u && !(mask >> v & 1))
                        next[mask | (1 << v)] = max(next[mask | (1 << v)], dp[mask] + 1);
        dp.swap(next);
    }
    return *max_element(dp.begin(), dp.end());
}
void certificate(int n, int m, const vector<pair<int, int>> &e,
                 const vector<int> &right, int expected)
{
    need(int(right.size()) == m);
    vector<bool> used(n);
    int count = 0;
    for (int v = 0; v < m; v++)
    {
        int u = right[v];
        if (u == -1) continue;
        need(0 <= u && u < n && !used[u]);
        need(find(e.begin(), e.end(), pair{u, v}) != e.end());
        used[u] = true;
        count++;
    }
    need(count == expected);
}
void current(BipartiteMatching &g, const vector<pair<int, int>> &e, int expected)
{
    need(g.solve() == expected);
    vector<int> right(g.m);
    for (int v = 1; v <= g.m; v++) right[v - 1] = g.r[v] - 1;
    certificate(g.n, g.m, e, right, expected);
    for (int u = 1; u <= g.n; u++)
        if (g.l[u]) need(g.r[g.l[u]] == u);
    for (int v = 1; v <= g.m; v++)
        if (g.r[v]) need(g.l[g.r[v]] == v);
    auto [left, right_cover] = g.cover();
    vector<bool> a(g.n + 1), b(g.m + 1);
    for (int u : left)
    {
        need(1 <= u && u <= g.n && !a[u]);
        a[u] = true;
    }
    for (int v : right_cover)
    {
        need(1 <= v && v <= g.m && !b[v]);
        b[v] = true;
    }
    need(int(left.size() + right_cover.size()) == expected);
    for (auto [u, v] : e) need(a[u + 1] || b[v + 1]);
}
void test(int n, int m, const vector<pair<int, int>> &e, int known = -1)
{
    graphs++;
    BipartiteMatching g(n, m);
    wida_source::HopcroftKarp w(n, m);
    matrix_source::uN = list_source::uN = hk_source::uN = n;
    matrix_source::vN = m;
    for (int u = 0; u < n; u++)
    {
        fill(matrix_source::g[u], matrix_source::g[u] + m, 0);
        hk_source::G[u].clear();
    }
    list_source::init();
    vector<pair<int, int>> prefix;
    int previous = 0;
    for (int stage = 0; stage < 2; stage++)
    {
        int end = stage ? int(e.size()) : 0;
        for (int i = int(prefix.size()); i < end; i++)
        {
            auto [u, v] = e[i];
            prefix.push_back(e[i]);
            g.add(u + 1, v + 1);
            w.add(u + 1, v + 1);
            matrix_source::g[u][v] = 1;
            list_source::addedge(u, v);
            hk_source::G[u].push_back(v);
        }
        int want = known >= 0 ? (stage ? known : 0) : optimum(n, m, prefix);
        current(g, prefix, want);
        current(g, prefix, want);
        need(matrix_source::hungary() == want);
        certificate(n, m, prefix, vector<int>(matrix_source::linker, matrix_source::linker + m), want);
        need(list_source::hungary() == want);
        certificate(n, m, prefix, vector<int>(list_source::linker, list_source::linker + m), want);
        need(hk_source::MaxMatch() == want);
        certificate(n, m, prefix, vector<int>(hk_source::My, hk_source::My + m), want);
        for (int u = 0; u < n; u++)
            if (hk_source::Mx[u] != -1) need(hk_source::My[hk_source::Mx[u]] == u);
        need(w.work() == want - previous);
        certificate(n, m, prefix, w.r, want);
        auto answer = w.answer();
        need(int(answer.size()) == want);
        for (auto [u, v] : answer)
        {
            need(0 <= u && u < n && 0 <= v && v < m);
            need(w.l[u] == v && w.r[v] == u);
        }
        need(w.work() == 0);
        certificate(n, m, prefix, w.r, want);
        previous = want;
    }
    need(matrix_source::hungary() == previous);
    need(list_source::hungary() == previous);
    need(hk_source::MaxMatch() == previous);
}
int main(int argc, char **)
{
    try
    {
        test(2, 2, {{0, 0}, {0, 1}, {1, 0}});
        for (int n = 0; n <= 4; n++)
            for (int m = 0; m <= 4; m++)
                for (int mask = 0; mask < (1 << (n * m)); mask++)
                {
                    vector<pair<int, int>> e;
                    for (int u = 0; u < n; u++)
                        for (int v = 0; v < m; v++)
                            if (mask >> (u * m + v) & 1) e.push_back({u, v});
                    test(n, m, e);
                }
        mt19937 rng(20261008);
        for (int i = 0; i < 300; i++)
        {
            int n = 1 + rng() % 8, m = 1 + rng() % 8;
            vector<pair<int, int>> e;
            for (int j = 0; j < 30; j++) e.push_back({int(rng() % n), int(rng() % m)});
            shuffle(e.begin(), e.end(), rng);
            test(n, m, e);
        }
        // Existing matching followed by an augmenting path; return total vs delta.
        BipartiteMatching a(2, 2);
        wida_source::HopcroftKarp b(2, 2);
        a.add(1, 2);
        b.add(1, 2);
        need(a.solve() == 1 && b.work() == 1);
        a.add(1, 1);
        a.add(2, 2);
        b.add(1, 1);
        b.add(2, 2);
        need(a.solve() == 2 && b.work() == 1);
        need(a.solve() == 2 && b.work() == 0);
        need(a.l[1] == 1 && a.l[2] == 2 && b.l[0] == 0 && b.l[1] == 1);
        if (argc == 1)
        {
            int n = 200;
            vector<pair<int, int>> e;
            for (int u = 0; u < n; u++)
                for (int v = 0; v < n; v++) e.push_back({u, v});
            test(n, n, e, n);
            BipartiteMatching deep(100000, 100000);
            for (int u = 1; u < 100000; u++) deep.add(u, u + 1);
            need(deep.solve() == 99999);
            for (int u = 1; u <= 100000; u++) deep.add(u, u);
            need(deep.solve() == 100000);
            for (int u = 1; u <= 100000; u++) need(deep.l[u] == u && deep.r[u] == u);
            need(deep.solve() == 100000);
        }
        cout << "PASS " << graphs << " graphs " << checks << " checks\n";
    }
    catch (const exception &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
