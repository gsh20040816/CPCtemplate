#include "../src/compact/dense_dijkstra.hpp"
#include "../src/compact/graph.hpp"
#include <iostream>
#include <random>
#include <stdexcept>
namespace kd
{
#include "fixtures/dijkstra_sources/kuangbin-dense.inc"
#undef typec
int cost[MAXN][MAXN], d[MAXN];
}
namespace kh
{
#include "fixtures/dijkstra_sources/kuangbin-heap.inc"
}
using I = __int128_t;
using Edge = tuple<int, int, long long>;
long long runs = 0, checks = 0;

void need(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}

vector<long long> wida(int n, const vector<Edge> &edges, int s, int t = 0)
{
    vector<vector<pair<long long, long long>>> ver(n + 1);
    for (auto [u, v, w] : edges) ver[u].push_back({v, w});
#define int long long
#include "fixtures/dijkstra_sources/wida-heap.inc"
#undef int
    djikstra(s);
    if (t) djikstra(t);
    return dis;
}

vector<I> oracle(int n, const vector<Edge> &edges, int s)
{
    vector<I> d(n + 1, DenseDijkstra::inf);
    d[s] = 0;
    for (int step = 1; step < n; step++)
    {
        auto next = d;
        for (auto [u, v, w] : edges)
            if (d[u] != DenseDijkstra::inf)
            {
                next[v] = min(next[v], d[u] + w);
            }
        d = next;
    }
    return d;
}

void path_check(int n, const vector<Edge> &e, int s, int t, const vector<int> &p, I want)
{
    if (want == DenseDijkstra::inf)
    {
        need(p.empty());
        return;
    }
    need(!p.empty() && p.front() == s && p.back() == t && p.size() <= size_t(n));
    vector<bool> seen(n + 1);
    I sum = 0;
    for (int i = 0; i < int(p.size()); i++)
    {
        need(1 <= p[i] && p[i] <= n && !seen[p[i]]);
        seen[p[i]] = true;
        if (!i) continue;
        long long w = -1;
        for (auto [u, v, x] : e)
        {
            if (u == p[i-1] && v == p[i] && (w == -1 || x < w)) w = x;
        }
        need(w >= 0);
        sum += w;
    }
    need(sum == want);
}

void check(DenseDijkstra &g, const vector<Edge> &edges, int s, bool sources)
{
    runs++;
    auto want = oracle(g.n, edges, s);
    g.run(s);
    need(g.valid && g.root == s && g.dis == want);
    for (int v = 1; v <= g.n; v++)
    {
        auto p = g.path(v);
        if (want[v] == DenseDijkstra::inf)
        {
            need(p.empty() && g.pre[v] == -1);
            continue;
        }
        need(!p.empty() && p.front() == s && p.back() == v);
        need(p.size() <= size_t(g.n));
        vector<bool> seen(g.n + 1);
        I sum = 0;
        for (int i = 0; i < int(p.size()); i++)
        {
            int u = p[i];
            need(1 <= u && u <= g.n && !seen[u]);
            seen[u] = true;
            if (!i)
            {
                need(g.pre[u] == -1);
                continue;
            }
            long long best = -1;
            for (auto [a, b, w] : edges)
                if (a == p[i - 1] && b == u && (best == -1 || w < best)) best = w;
            need(best >= 0 && g.pre[u] == p[i - 1]);
            sum += best;
        }
        need(sum == want[v]);
    }
    if (!sources) return;
    Dijkstra heap(g.n);
    for (int u = 1; u <= g.n; u++)
    {
        kh::E[u].clear();
        for (int v = 1; v <= g.n; v++) kd::cost[u - 1][v - 1] = kd::INF;
    }
    for (auto [u, v, w] : edges)
    {
        heap.add(u, v, w);
        kh::addedge(u, v, w);
        kd::cost[u - 1][v - 1] = min(kd::cost[u - 1][v - 1], int(w));
    }
    kd::Dijkstra(kd::cost, kd::d, g.n, s - 1);
    kh::Dijkstra(g.n, s);
    heap.run(s);
    auto wd = wida(g.n, edges, s);
    for (int v = 1; v <= g.n; v++)
    {
        bool unreachable = want[v] == DenseDijkstra::inf;
        need(kd::d[v - 1] == (unreachable ? kd::INF : want[v]));
        need(kh::dist[v] == (unreachable ? kh::INF : want[v]));
        need(wd[v] == (unreachable ? I(1000000000000000000LL) : want[v]));
        need(heap.dis[v] == (unreachable ? I(LLONG_MAX) : want[v]));
        path_check(g.n, edges, s, v, heap.path(v), want[v]);
        vector<int> p;
        if (!unreachable)
        {
            for (int u = v - 1; u != -1 && p.size() <= size_t(g.n); u = kd::pre[u])
            {
                need(0 <= u && u < g.n);
                p.push_back(u + 1);
            }
            reverse(p.begin(), p.end());
        }
        path_check(g.n, edges, s, v, p, want[v]);
    }
}

int main(int argc, char **)
{
    try
    {
        for (int n = 1; n <= 4; n++)
        {
            vector<pair<int, int>> pairs;
            for (int u = 1; u <= n; u++)
                for (int v = 1; v <= n; v++)
                    if (u != v && (n < 4 || u < v)) pairs.push_back({u, v});
            for (int mask = 0; mask < (1 << (2 * pairs.size())); mask++)
            {
                DenseDijkstra g(n);
                vector<Edge> e;
                int a = mask;
                for (auto [u, v] : pairs)
                {
                    int w = a % 4;
                    a /= 4;
                    if (w)
                    {
                        g.add(u, v, w - 1);
                        e.push_back({u, v, w - 1});
                    }
                }
                for (int s = 1; s <= n; s++) check(g, e, s, true);
            }
        }
        mt19937 rng(312313);
        for (int tc = 0; tc < 300; tc++)
        {
            int n = 1 + rng() % 7;
            DenseDijkstra g(n);
            vector<Edge> e;
            for (int step = 0; step < 10; step++)
            {
                auto old = g;
                int u = 1 + rng() % n, v = 1 + rng() % n;
                long long w = rng() % 10;
                g.add(u, v, w);
                need(!g.valid);
                check(old, e, 1, true);
                e.push_back({u, v, w});
                check(g, e, 1 + rng() % n, true);
            }
        }
        DenseDijkstra g(5);
        vector<Edge> e = {{1,2,LLONG_MAX},{2,3,LLONG_MAX},{3,4,0},{4,3,0},{1,2,LLONG_MAX-1}};
        for (auto [u,v,w] : e) g.add(u,v,w);
        for (int s = 1; s <= 5; s++) check(g,e,s,false);
        // The literal WIDA closure keeps dis outside the call; changing roots is not a reset.
        auto reused = wida(2,{{1,2,1}},1,2);
        need(reused[1] == 0 && reused[2] == 0);
        need(oracle(2,{{1,2,1}},2)[1] == DenseDijkstra::inf);
        Dijkstra heap(4);
        vector<Edge> he = {{1,2,LLONG_MAX-1},{2,3,0},{1,4,LLONG_MAX-2},{4,2,0},{2,4,LLONG_MAX}};
        for (auto [u,v,w] : he) heap.add(u,v,w);
        for (int s : {1,3})
        {
            heap.run(s);
            auto d = oracle(4,he,s);
            for (int v=1;v<=4;v++)
            {
                need(heap.dis[v] == (d[v] == DenseDijkstra::inf ? I(LLONG_MAX) : d[v]));
                path_check(4,he,s,v,heap.path(v),d[v]);
            }
        }
        heap.add(3,1,0);
        he.push_back({3,1,0});
        heap.run(3);
        auto hd = oracle(4,he,3);
        for (int v=1;v<=4;v++) path_check(4,he,3,v,heap.path(v),hd[v]);
        if (argc == 1)
        {
            Dijkstra parallel(2);
            for (int w = 100000; w >= 1; w--) parallel.add(1,2,w);
            parallel.run(1);
            need(parallel.dis[2] == 1 && parallel.path(2) == vector<int>({1,2}));
            int n = 2000;
            DenseDijkstra large(n);
            vector<Edge> chain;
            for (int u = 1; u < n; u++)
            {
                large.add(u, u+1, LLONG_MAX);
                chain.push_back({u,u+1,LLONG_MAX});
            }
            // Avoid cubic certificate scanning on the large family.
            large.run(1);
            need(large.dis[n] == I(n-1)*LLONG_MAX);
            auto p = large.path(n);
            need(p.size() == size_t(n));
            for (int i=0;i<n;i++) need(p[i] == i+1);
            large.run(n);
            need(large.path(1).empty() && large.path(n) == vector<int>{n});
        }
        cout << "PASS " << runs << " runs " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
