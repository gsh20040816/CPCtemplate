#include "../src/compact/hlpp.hpp"
#include <random>

using Edge = tuple<int, int, long long>;
long long cut_value(int n, int s, int t, const vector<Edge> &edges)
{
    long long best = LLONG_MAX;
    for (int mask = 0; mask < (1 << n); mask++)
    {
        if (!(mask >> (s - 1) & 1) || (mask >> (t - 1) & 1)) continue;
        long long val = 0;
        for (auto [u, v, c] : edges)
            if ((mask >> (u - 1) & 1) && !(mask >> (v - 1) & 1)) val += c;
        best = min(best, val);
    }
    return best;
}
void verify(HLPP &a, int s, int t, long long want)
{
    long long got = a.flow(s, t);
    if (got != want) abort();
    auto cut = a.min_cut();
    if (!cut[s] || cut[t]) abort();
    vector<__int128_t> net(a.n + 1);
    __int128_t cut_cap = 0;
    for (int id = 0; id < int(a.e.size()); id += 2)
    {
        auto edge = a.e[id];
        long long f = a.used(id);
        if (f < 0 || f > edge.initial || a.e[id ^ 1].cap != f) abort();
        net[edge.from] -= f;
        net[edge.to] += f;
        if (cut[edge.from] && !cut[edge.to]) cut_cap += edge.initial;
    }
    if (cut_cap != want) abort();
    for (int u = 1; u <= a.n; u++)
        if (net[u] != (u == s ? -__int128_t(want) : u == t ? want : 0)) abort();
}
void check(int n, int s, int t, const vector<Edge> &edges)
{
    HLPP a(n);
    for (auto [u, v, c] : edges) a.add(u, v, c);
    long long want = cut_value(n, s, t, edges);
    verify(a, s, t, want);
    auto b = a;
    verify(b, s, t, want);
    verify(a, t, s, cut_value(n, t, s, edges));
    verify(a, s, t, want);
}
int main()
{
    int exhaustive = 0;
    for (int mask = 0; mask < 19683; mask++)
    {
        int value = mask;
        vector<Edge> edges;
        for (int u = 1; u <= 3; u++)
            for (int v = 1; v <= 3; v++)
            {
                int cap = value % 3;
                value /= 3;
                if (cap) edges.push_back({u, v, cap});
            }
        check(3, 1, 3, edges);
        exhaustive++;
    }
    mt19937_64 rng(4722);
    for (int trial = 0; trial < 5000; trial++)
    {
        int n = 2 + rng() % 7;
        vector<Edge> edges;
        int m = rng() % 65;
        for (int i = 0; i < m; i++)
            edges.push_back({1 + rng() % n, 1 + rng() % n, rng() % 10000});
        int s = 1 + rng() % n;
        int t = 1 + rng() % n;
        if (s == t) t = t % n + 1;
        check(n, s, t, edges);
        shuffle(edges.begin(), edges.end(), rng);
        check(n, s, t, edges);
    }
    check(2, 1, 2, {{1, 2, LLONG_MAX}});
    check(4, 1, 4, {{1, 2, LLONG_MAX / 2}, {2, 3, LLONG_MAX / 4}, {1, 4, 1}});
    check(5, 1, 5, {{1, 2, 100}, {2, 3, 100}, {3, 4, 100}, {4, 2, 100}, {1, 5, 1}});
    HLPP a(4);
    a.add(1, 2, 10);
    a.add(2, 4, 2);
    verify(a, 1, 4, 2);
    a.add(2, 3, 5);
    a.add(3, 4, 7);
    verify(a, 1, 4, 7);
    cout << "PASS: " << exhaustive << " ternary directed graphs, 5000 random multigraphs and shuffled copies; capacity/conservation/cut/recompute/terminal-change/64-bit checks\n";
}
