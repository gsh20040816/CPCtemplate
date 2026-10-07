#include "../src/compact/manhattan_mst.hpp"
namespace source
{
#define main unused_source_main
#include "fixtures/manhattan_sources/kuangbin.inc"
#undef main
}
using I = __int128_t;
using Point = ManhattanMST::Point;
long long checks = 0, cases = 0, ranks = 0;
void need(bool b)
{
    checks++;
    if (!b) throw runtime_error("oracle");
}
I distance(Point a, Point b)
{
    I x = I(a.first) - b.first;
    I y = I(a.second) - b.second;
    return (x < 0 ? -x : x) + (y < 0 ? -y : y);
}
vector<I> prim(const vector<Point> &p)
{
    int n = p.size();
    vector<I> dis(n, I(1) << 126), w;
    vector<bool> used(n);
    dis[0] = 0;
    for (int i = 0; i < n; i++)
    {
        int u = -1;
        for (int v = 0; v < n; v++)
            if (!used[v] && (u == -1 || dis[v] < dis[u])) u = v;
        used[u] = true;
        if (i) w.push_back(dis[u]);
        for (int v = 0; v < n; v++)
            if (!used[v]) dis[v] = min(dis[v], distance(p[u], p[v]));
    }
    sort(w.begin(), w.end());
    return w;
}
void load(const vector<Point> &p)
{
    source::n = p.size();
    for (int i = 0; i < (int)p.size(); i++)
        source::p[i] = {int(p[i].first), int(p[i].second), i};
}
void candidate_check(const vector<Point> &p, const vector<ManhattanMST::Edge> &edges)
{
    int n = p.size();
    need(edges.size() <= 4 * (p.size() - 1));
    for (auto [w, u, v] : edges)
    {
        need(0 <= u && u < n && 0 <= v && v < n && u != v);
        need(w == distance(p[u], p[v]));
    }
    if (n > 8) return;
    for (int mask = 1; mask < (1 << n) - 1; mask++)
    {
        I full = I(1) << 126, part = full;
        for (int u = 0; u < n; u++)
            for (int v = 0; v < n; v++)
                if (((mask >> u) ^ (mask >> v)) & 1)
                    full = min(full, distance(p[u], p[v]));
        for (auto [w, u, v] : edges)
            if (((mask >> u) ^ (mask >> v)) & 1) part = min(part, w);
        need(part == full);
    }
}
void test(const vector<Point> &p, bool upstream = true, vector<I> expected = {})
{
    cases++;
    int n = p.size();
    if (expected.empty()) expected = prim(p);
    auto saved = p;
    auto result = ManhattanMST::solve(p);
    need(p == saved && result.edges.size() == p.size() - 1);
    vector<vector<int>> adj(n);
    vector<I> actual;
    for (auto [u, v] : result.edges)
    {
        need(0 <= u && u < n && 0 <= v && v < n);
        actual.push_back(distance(p[u], p[v]));
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    vector<bool> seen(n);
    vector<int> queue{0};
    seen[0] = true;
    for (int i = 0; i < (int)queue.size(); i++)
        for (int v : adj[queue[i]])
            if (!seen[v])
            {
                seen[v] = true;
                queue.push_back(v);
            }
    need(queue.size() == p.size());
    sort(actual.begin(), actual.end());
    need(actual == expected);
    need(result.weight == accumulate(expected.begin(), expected.end(), I(0)));
    candidate_check(p, ManhattanMST::candidates(p));
    if (!upstream) return;
    load(p);
    source::Manhattan_minimum_spanning_tree(n, source::p);
    vector<ManhattanMST::Edge> edges;
    for (int i = 0; i < source::tot; i++)
    {
        auto e = source::edge[i];
        edges.emplace_back(e.d, e.u, e.v);
    }
    candidate_check(p, edges);
    for (int i = 0; i < n; i++)
    {
        auto q = source::p[i];
        need(q.x == p[q.id].first && q.y == -p[q.id].second);
    }
    vector<int> queries;
    if (n <= 10)
        for (int k = 1; k < n; k++) queries.push_back(k);
    else queries = {1, n / 2, n - 1};
    for (int k : queries)
    {
        ranks++;
        load(p);
        need(source::solve(k) == expected[k - 1]);
        // Original main's solve(n-k) is the kth largest among n-1 weights.
        load(p);
        need(source::solve(n - k) == expected[n - k - 1]);
    }
}
int main(int argc, char **argv)
{
    if (argc > 1 && string(argv[1]) == "source-int-overflow")
    {
        source::Point a{INT_MIN, 0, 0}, b{1, 0, 1};
        cout << source::dist(a, b) << '\n';
        return 0;
    }
    try
    {
        vector<Point> grid;
        for (int x = -1; x <= 1; x++)
            for (int y = -1; y <= 1; y++) grid.push_back({x, y});
        for (int n = 2; n <= 5; n++)
        {
            vector<Point> p;
            auto enumerate = [&](auto &&self, int first) -> void
            {
                if ((int)p.size() == n)
                {
                    test(p);
                    reverse(p.begin(), p.end());
                    test(p);
                    reverse(p.begin(), p.end());
                    return;
                }
                for (int i = first; i < 9; i++)
                {
                    p.push_back(grid[i]);
                    self(self, i);
                    p.pop_back();
                }
            };
            enumerate(enumerate, 0);
        }
        mt19937 rng(419);
        for (int i = 0; i < 400; i++)
        {
            vector<Point> p(2 + rng() % 9);
            for (auto &[x, y] : p)
            {
                x = int(rng() % 201) - 100;
                y = int(rng() % 201) - 100;
            }
            test(p);
        }
        test({{LLONG_MIN, LLONG_MIN}, {LLONG_MAX, LLONG_MAX}, {0, 0}}, false);
        vector<Point> line;
        for (int i = 0; i < 100000; i++) line.push_back({i - 50000, 0});
        test(line, true, vector<I>(99999, 1));
        test(vector<Point>(100000, {0, 0}), true, vector<I>(99999, 0));
        cout << "PASS " << cases << " point sets " << ranks << " ranks " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
