#include "../src/compact/prim.hpp"
#include <bits/stdc++.h>
using I = __int128_t;
struct E
{
    int u, v;
    long long w;
};
namespace kb
{
#include "fixtures/prim_sources/kuangbin.inc"
}
namespace wd
{
#define ms(a, b) memset(a, b, sizeof(a))
#define main source_main
#include "fixtures/prim_sources/wida.inc"
#undef main
#undef ms
}
long long checks = 0, runs = 0;
void check(bool x)
{
    checks++;
    if (!x) throw runtime_error("oracle rejection");
}
vector<vector<bool>> reach(int n, const vector<E> &e)
{
    vector<vector<bool>> a(n, vector<bool>(n));
    for (int i = 0; i < n; i++) a[i][i] = true;
    for (auto [u, v, w] : e) a[u][v] = a[v][u] = true;
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                a[i][j] = a[i][j] || (a[i][k] && a[k][j]);
    return a;
}
pair<int, I> oracle(int n, const vector<E> &e)
{
    auto a = reach(n, e);
    int c = 0;
    for (int i = 0; i < n; i++)
    {
        bool first = true;
        for (int j = 0; j < i; j++) if (a[i][j]) first = false;
        c += first;
    }
    I best = I(1) << 126;
    for (unsigned mask = 0; mask < (1U << e.size()); mask++)
    {
        if (popcount(mask) != n - c) continue;
        vector<E> f;
        I weight = 0;
        for (int i = 0; i < int(e.size()); i++)
            if ((mask >> i) & 1)
            {
                f.push_back(e[i]);
                weight += I(e[i].w);
            }
        if (reach(n, f) == a) best = min(best, weight);
    }
    check(best != (I(1) << 126));
    return {c, best};
}
void certificate(Prim &g, const vector<E> &e, pair<int, I> answer)
{
    auto old = g.cost;
    int c = g.run();
    runs++;
    check(c == answer.first && g.weight == answer.second);
    check(g.cost == old && int(g.pre.size()) == g.n);
    vector<E> f;
    I weight = 0;
    int roots = 0;
    for (int v = 0; v < g.n; v++)
    {
        int u = g.pre[v];
        if (u == -1)
        {
            roots++;
            continue;
        }
        check(0 <= u && u < g.n && u != v);
        check(g.cost[u][v] != Prim::inf);
        f.push_back({u, v, (long long)g.cost[u][v]});
        weight += g.cost[u][v];
        vector<bool> seen(g.n);
        for (int x = v; x != -1; x = g.pre[x])
        {
            check(0 <= x && x < g.n && !seen[x]);
            seen[x] = true;
        }
    }
    check(roots == c && int(f.size()) == g.n - c);
    check(weight == g.weight && reach(g.n, f) == reach(g.n, e));
}
void small(int n, const vector<E> &e)
{
    auto expected = oracle(n, e);
    Prim g(n);
    for (auto [u, v, w] : e) g.add(u, v, w);
    certificate(g, e, expected);
    auto pre = g.pre;
    certificate(g, e, expected);
    check(pre == g.pre);
    auto copy = g;
    if (n)
    {
        copy.add(0, 0, LLONG_MIN);
        certificate(copy, e, expected);
        check(g.cost[0][0] != LLONG_MIN || copy.cost == g.cost);
    }
    if (n && n <= 6 && e.size() <= 20)
    {
        bool safe = true;
        for (auto x : e) safe &= -10 <= x.w && x.w <= 10;
        if (safe)
        {
            static int cost[kb::MAXN][kb::MAXN];
            memset(cost, 0x3f, sizeof(cost));
            memset(wd::g, 0x3f, sizeof(wd::g));
            memset(wd::v, 0, sizeof(wd::v));
            wd::n = n;
            for (auto [u, v, w] : e)
            {
                cost[u][v] = cost[v][u] = min(cost[u][v], int(w));
                wd::g[u + 1][v + 1] = wd::g[v + 1][u + 1] = cost[u][v];
            }
            check(kb::Prim(cost, n) == (expected.first == 1 ? int(expected.second) : -1));
            check(kb::Prim(cost, n) == (expected.first == 1 ? int(expected.second) : -1));
            check(wd::prim() == (expected.first == 1 ? int(expected.second) : wd::INF));
        }
    }
}
int main(int argc, char **)
{
    try
    {
        small(0, {});
        small(1, {{0, 0, LLONG_MIN}});
        small(3, {{0, 1, 3}, {0, 1, -1}, {1, 2, 0}, {0, 2, 1}, {2, 2, -9}});
        small(4, {{0, 1, LLONG_MIN}, {1, 2, LLONG_MIN}, {0, 2, LLONG_MAX}});
        small(3, {{0, 1, LLONG_MAX}, {1, 2, LLONG_MAX}});
        for (int n = 1; n <= 4; n++)
        {
            vector<pair<int, int>> pairs;
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++) pairs.push_back({i, j});
            int total = 1;
            for (auto p : pairs) total *= 5;
            for (int mask = 0; mask < total; mask++)
            {
                int state = mask;
                vector<E> e;
                for (auto [u, v] : pairs)
                {
                    int c = state % 5;
                    state /= 5;
                    if (c) e.push_back({u, v, array<int, 5>{0, -2, -1, 0, 3}[c]});
                }
                small(n, e);
            }
        }
        mt19937 rng(314315);
        for (int it = 0; it < 200; it++)
        {
            int n = 1 + rng() % 6;
            vector<E> e;
            Prim g(n);
            for (int j = 0; j < 12; j++)
            {
                E x{int(rng() % n), int(rng() % n), int(rng() % 21) - 10};
                e.push_back(x);
                g.add(x.u, x.v, x.w);
                certificate(g, e, oracle(n, e));
            }
            small(n, e);
        }
        if (argc == 1)
        {
            int n = 2000;
            Prim g(n);
            for (int i = n - 1; i; i--) g.add(i, i - 1, LLONG_MIN);
            for (int i = 0; i < n; i++) g.add(i, i, LLONG_MIN);
            g.add(0, n - 1, LLONG_MAX);
            check(g.run() == 1);
            check(g.weight == I(n - 1) * LLONG_MIN);
            check(g.pre[0] == -1);
            for (int i = 1; i < n; i++) check(g.pre[i] == i - 1);
            check(g.run() == 1 && g.weight == I(n - 1) * LLONG_MIN);
            Prim isolated(n);
            check(isolated.run() == n && isolated.weight == 0);
            for (int p : isolated.pre) check(p == -1);
        }
        cout << "PASS " << runs << " runs " << checks << " checks\n";
    }
    catch (const exception &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
