#include "../src/compact/flow_unique.hpp"
namespace source
{
const int MAXN = 20;
struct Edge { int to, next; long long cap, flow; } edge[200];
int head[MAXN], end;
#include "fixtures/flow_unique_sources/kuangbin.inc"
bool multiple(const Dinic &g, int t)
{
    fill(head, head + MAXN, -1);
    for (int i = 0; i < (int)g.e.size(); i++)
    {
        auto e = g.e[i];
        edge[i] = {e.to, head[e.from], e.initial, e.initial - e.cap};
        head[e.from] = i;
    }
    end = t;
#include "fixtures/flow_unique_sources/kuangbin-call.inc"
    return flag;
}
}
long long checks = 0, cases = 0, schemes = 0;
void need(bool b)
{
    checks++;
    if (!b) throw runtime_error("oracle");
}
void test(int n, int s, int t, const vector<array<int, 3>> &edges)
{
    cases++;
    vector<int> balance(n + 1);
    vector<int> f(edges.size());
    vector<vector<int>> bests;
    int best = -1;
    auto enumerate = [&](auto &&self, int i) -> void
    {
        if (i == (int)edges.size())
        {
            for (int u = 1; u <= n; u++)
                if (u != s && u != t && balance[u]) return;
            if (balance[s] != -balance[t] || balance[s] < best) return;
            if (balance[s] > best)
            {
                best = balance[s];
                bests.clear();
            }
            bests.push_back(f);
            return;
        }
        auto [u, v, cap] = edges[i];
        for (int x = 0; x <= cap; x++)
        {
            f[i] = x;
            balance[u] += x;
            balance[v] -= x;
            self(self, i + 1);
            balance[u] -= x;
            balance[v] += x;
        }
    };
    enumerate(enumerate, 0);
    Dinic g(n);
    for (auto [u, v, c] : edges) g.add(u, v, c);
    need(g.flow(s, t) == best);
    bool unique = bests.size() == 1;
    need(flow_unique(g) == unique);
    vector<int> actual;
    for (int i = 0; i < (int)edges.size(); i++) actual.push_back(g.used(2 * i));
    need(find(bests.begin(), bests.end(), actual) != bests.end());
    for (auto &f : bests)
    {
        schemes++;
        for (int i = 0; i < (int)edges.size(); i++)
            g.change_edge(2 * i, edges[i][2], f[i]);
        need(flow_unique(g) == unique);
        need(flow_unique(g) == unique);
        for (int i = 0; i < (int)edges.size(); i++) need(g.used(2 * i) == f[i]);
        need(g.flow(s, t) == 0);
    }
}
void source_failures()
{
    Dinic parallel(3);
    parallel.add(1, 2, 1);
    parallel.add(1, 2, 1);
    parallel.add(2, 3, 1);
    need(parallel.flow(1, 3) == 1);
    need(!flow_unique(parallel) && !source::multiple(parallel, 3));
    Dinic isolated(4);
    isolated.add(1, 2, 1);
    isolated.add(3, 4, 1);
    isolated.add(4, 3, 1);
    need(isolated.flow(1, 2) == 1);
    need(!flow_unique(isolated) && !source::multiple(isolated, 2));
    Dinic cancel(3);
    cancel.add(1, 2, 2);
    cancel.add(2, 3, 1);
    need(cancel.flow(1, 3) == 1);
    need(flow_unique(cancel));
    test(3, 1, 3, {{1, 2, 1}, {1, 2, 1}, {2, 3, 1}});
    test(3, 1, 2, {{1, 2, 1}, {3, 3, 1}});
    test(3, 1, 3, {{1, 2, 2}, {2, 3, 1}});
    test(3, 1, 2, {{1, 2, 1}, {3, 3, 0}});
}
int main(int argc, char **)
{
    try
    {
        source_failures();
        if (argc > 1)
        {
            cout << "MUTANT_SURVIVED\n";
            return 0;
        }
        for (int n = 2; n <= 3; n++)
            for (int mask = 0; mask < (1 << (n * n)); mask++)
            {
                vector<array<int, 3>> e;
                for (int u = 1; u <= n; u++)
                    for (int v = 1; v <= n; v++)
                        if (mask >> ((u - 1) * n + v - 1) & 1) e.push_back({u, v, 1});
                for (int s = 1; s <= n; s++)
                    for (int t = 1; t <= n; t++)
                        if (s != t) test(n, s, t, e);
            }
        mt19937 rng(4166);
        for (int i = 0; i < 400; i++)
        {
            int n = 2 + rng() % 4;
            vector<array<int, 3>> e;
            for (int j = 0; j < i % 9; j++)
                e.push_back({1 + int(rng() % n), 1 + int(rng() % n), int(rng() % 3)});
            test(n, 1, n, e);
        }
        Dinic wide(3);
        wide.add(1, 2, LLONG_MAX);
        need(wide.flow(1, 2) == LLONG_MAX && flow_unique(wide));
        wide.add(3, 3, LLONG_MAX);
        need(!flow_unique(wide));
        int n = 100000;
        Dinic chain(n);
        for (int u = 1; u < n; u++) chain.add(u, u + 1, 2);
        chain.add(1, n, 1);
        need(chain.flow(1, n) == 3 && flow_unique(chain));
        // A feasible positive flow leaves both residual directions on a tree.
        Dinic tree(n + 1);
        for (int u = 1; u < n; u++) tree.add(u, u + 1, 2);
        tree.add(n, n + 1, 1);
        need(tree.flow(1, n + 1) == 1 && flow_unique(tree));
        tree.add(1, n, 1);
        need(tree.flow(1, n + 1) == 0 && !flow_unique(tree));
        cout << "PASS " << cases << " graphs " << schemes << " optimum schemes " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
