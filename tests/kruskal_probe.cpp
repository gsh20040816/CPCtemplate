#include "../src/compact/kruskal.hpp"
using I = __int128_t;
using E = Kruskal::Edge;
namespace kb
{
#include "fixtures/kruskal_sources/kuangbin.inc"
}
// Numeric comparison only; original assertion behavior is tested separately.
#pragma push_macro("assert")
#undef assert
#define assert(x) ((void)0)
namespace wo
{
#include "fixtures/kruskal_sources/wida-online.inc"
}
namespace wp
{
#include "fixtures/kruskal_sources/wida-print.inc"
}
#pragma pop_macro("assert")
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
void certificate(Kruskal &g, pair<int, I> answer)
{
    auto old = g.e;
    int c = g.run();
    runs++;
    check(c == answer.first && g.weight == answer.second);
    check(int(g.ids.size()) == g.n - c);
    check(g.e.size() == old.size());
    for (int i = 0; i < int(old.size()); i++)
        check(tie(g.e[i].u, g.e[i].v, g.e[i].w) == tie(old[i].u, old[i].v, old[i].w));
    vector<E> f;
    set<int> ids;
    I weight = 0;
    for (int id : g.ids)
    {
        check(0 <= id && id < int(g.e.size()) && ids.insert(id).second);
        f.push_back(g.e[id]);
        weight += I(g.e[id].w);
    }
    check(weight == g.weight);
    check(reach(g.n, f) == reach(g.n, g.e));
    for (int i = 1; i < int(g.ids.size()); i++)
    {
        int u = g.ids[i - 1], v = g.ids[i];
        check(tie(g.e[u].w, u) < tie(g.e[v].w, v));
    }
}
void small(int n, const vector<E> &e)
{
    auto expected = oracle(n, e);
    Kruskal g(n);
    for (int i = 0; i < int(e.size()); i++)
        check(g.add(e[i].u, e[i].v, e[i].w) == i);
    certificate(g, expected);
    auto ids = g.ids;
    certificate(g, expected);
    check(ids == g.ids);
    auto copy = g;
    if (n)
    {
        copy.add(0, 0, LLONG_MIN);
        certificate(copy, expected);
        check(g.e.size() == e.size());
    }
    if (n && n <= 6 && e.size() <= 20)
    {
        bool safe = true;
        for (auto x : e) safe &= -10 <= x.w && x.w <= 10;
        if (safe)
        {
            kb::tol = 0;
            wo::Tree a(n);
            wp::Tree b(n);
            for (auto [u, v, w] : e)
            {
                kb::addedge(u, v, int(w));
                a.add(u + 1, v + 1, int(w));
                b.add(u + 1, v + 1, int(w));
            }
            check(kb::Kruskal(n) == (expected.first == 1 ? int(expected.second) : -1));
            check(a.kruskal() == expected.second);
            check(b.kruskal() == expected.second);
            check(a.ver.empty() && b.ver.empty());
            check(a.kruskal() == 0 && b.kruskal() == 0);
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
            Kruskal g(n);
            for (int j = 0; j < 12; j++)
            {
                E x{int(rng() % n), int(rng() % n), int(rng() % 21) - 10};
                e.push_back(x);
                g.add(x.u, x.v, x.w);
                certificate(g, oracle(n, e));
            }
            small(n, e);
        }
        if (argc == 1)
        {
            int n = 200000;
            Kruskal g(n);
            for (int i = n - 1; i; i--) g.add(i, i - 1, LLONG_MIN);
            for (int i = 0; i < n; i++) g.add(i, i, LLONG_MIN);
            g.add(0, n - 1, LLONG_MAX);
            check(g.run() == 1);
            check(g.weight == I(n - 1) * LLONG_MIN);
            check(int(g.ids.size()) == n - 1);
            for (int i = 0; i < n - 1; i++) check(g.ids[i] == i);
            check(g.run() == 1 && g.weight == I(n - 1) * LLONG_MIN);
        }
        cout << "PASS " << runs << " runs " << checks << " checks\n";
    }
    catch (const exception &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
