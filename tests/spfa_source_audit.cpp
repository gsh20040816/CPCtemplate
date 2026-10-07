#include "../src/compact/spfa_flow.hpp"
namespace upstream
{
#include "fixtures/spfa_sources/kuangbin.inc"
}
using I = __int128_t;
struct Arc
{
    int u, v, cap, cost;
};
long long checks = 0, cases = 0;
void need(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("ORACLE_REJECT");
}
vector<optional<I>> enumerate(int n, const vector<Arc> &e)
{
    int upper = 0;
    for (auto a : e) upper += a.cap;
    vector<optional<I>> best(upper + 1);
    vector<int> b(n + 1);
    function<void(int, I)> visit = [&](int i, I c)
    {
        if (i == (int)e.size())
        {
            for (int u = 2; u < n; u++)
                if (b[u]) return;
            if (b[1] < 0 || b[1] != -b[n]) return;
            auto &x = best[b[1]];
            if (!x || c < *x) x = c;
            return;
        }
        auto a = e[i];
        for (int f = 0; f <= a.cap; f++)
        {
            b[a.u] += f;
            b[a.v] -= f;
            visit(i + 1, c + I(f) * a.cost);
            b[a.u] -= f;
            b[a.v] += f;
        }
    };
    visit(0, 0);
    while (!best.back()) best.pop_back();
    return best;
}
void certificate(int n, const vector<Arc> &e, const vector<long long> &f,
                 long long value, I cost)
{
    vector<I> b(n + 1);
    I c = 0;
    for (int i = 0; i < (int)e.size(); i++)
    {
        auto a = e[i];
        need(0 <= f[i] && f[i] <= a.cap);
        b[a.u] += f[i];
        b[a.v] -= f[i];
        c += I(f[i]) * a.cost;
    }
    need(b[1] == value && b[n] == -I(value) && c == cost);
    for (int u = 2; u < n; u++) need(b[u] == 0);
}
void check(int n, const vector<Arc> &e, const vector<optional<I>> &want)
{
    cases++;
    int maxf = (int)want.size() - 1;
    upstream::init(n);
    SpfaFlow g(n);
    for (auto a : e)
    {
        upstream::addedge(a.u - 1, a.v - 1, a.cap, a.cost);
        g.add(a.u, a.v, a.cap, a.cost);
    }
    int c = 123;
    int f = upstream::minCostMaxflow(0, n - 1, c);
    need(f == maxf && I(c) == *want.back());
    vector<long long> sf;
    for (int i = 0; i < (int)e.size(); i++)
    {
        sf.push_back(upstream::edge[2 * i].flow);
        need(upstream::edge[2 * i + 1].flow == -sf.back());
    }
    certificate(n, e, sf, f, c);
    c = 123;
    need(upstream::minCostMaxflow(0, n - 1, c) == 0 && c == 0);
    need(g.flow(1, n, 0) == make_pair(0LL, I(0)));
    I total = 0;
    for (int k = 1; k <= maxf; k++)
    {
        auto [more, extra] = g.flow(1, n, 1);
        total += extra;
        need(more == 1 && total == *want[k]);
        vector<long long> used;
        for (int id = 0; id < (int)g.e.size(); id += 2)
        {
            used.push_back(g.used(id));
            need(g.e[id ^ 1].cap == used.back());
        }
        certificate(n, e, used, k, total);
    }
    need(g.flow(1, n) == make_pair(0LL, I(0)));
}
void small(int n, const vector<Arc> &e)
{
    check(n, e, enumerate(n, e));
}
int main(int argc, char **argv)
{
    if (argc > 1)
    {
        upstream::init(2);
        string mode = argv[1];
        if (mode == "product-overflow") upstream::addedge(0, 1, 50000, 50000);
        if (mode == "negate-overflow") upstream::addedge(0, 1, 1, INT_MIN);
        int c;
        upstream::minCostMaxflow(0, 1, c);
        return 0;
    }
    try
    {
        for (int mask = 0; mask < 729; mask++)
        {
            int x = mask;
            vector<Arc> e;
            for (int u = 1; u <= 3; u++)
                for (int v = 1; v <= 3; v++)
                    if (u != v)
                    {
                        int digit = x % 3;
                        x /= 3;
                        if (digit) e.push_back({u, v, 1, digit - 1});
                    }
            small(3, e);
        }
        mt19937 rng(4171);
        for (int it = 0; it < 800; it++)
        {
            int n = 2 + rng() % 5;
            vector<int> h(n + 1);
            for (int u = 1; u <= n; u++) h[u] = int(rng() % 21) - 10;
            vector<Arc> e;
            for (int j = 0; j < it % 9; j++)
            {
                int u = 1 + rng() % n, v = 1 + rng() % n;
                e.push_back({u, v, int(rng() % 3), int(rng() % 4) + h[v] - h[u]});
            }
            small(n, e);
        }
        // DAGs remain negative-cycle free after negating every cost.
        for (int mask = 0; mask < 125; mask++)
        {
            int x = mask;
            vector<Arc> e;
            for (int u = 1; u <= 3; u++)
                for (int v = u + 1; v <= 3; v++)
                {
                    int z = x % 5;
                    x /= 5;
                    if (z) e.push_back({u, v, 2, z - 3});
                }
            small(3, e);
            for (auto &a : e) a.cost = -a.cost;
            small(3, e);
        }
        small(4, {{1,2,1,0},{2,3,1,-5},{3,4,1,0},{1,3,1,0},{2,4,1,0}});
        vector<Arc> chain;
        for (int u = 1; u < 10000; u++) chain.push_back({u,u+1,1,-1});
        check(10000, chain, {I(0), I(-9999)});
        vector<Arc> dense;
        for (int i = 0; i < 50000; i++) dense.push_back({1,2,0,1});
        dense.back().cap = 2;
        check(2, dense, {I(0), I(1), I(2)});
        // Source INF sentinel can reject a reachable path without overflow.
        upstream::init(2);
        upstream::addedge(0,1,1,upstream::INF);
        int c = 42;
        need(upstream::minCostMaxflow(0,1,c) == 0 && c == 0);
        SpfaFlow sentinel(2);
        sentinel.add(1,2,1,upstream::INF);
        need(sentinel.flow(1,2) == make_pair(1LL,I(upstream::INF)));
        // Disconnected negative circulation: source ignores it; current rejects.
        upstream::init(4);
        upstream::addedge(0,3,1,0);
        upstream::addedge(1,2,1,-1);
        upstream::addedge(2,1,1,0);
        need(upstream::minCostMaxflow(0,3,c) == 1 && c == 0);
        auto best = enumerate(4,{{1,4,1,0},{2,3,1,-1},{3,2,1,0}});
        need(*best.back() == -1);
        for (bool connected : {false,true})
        {
            SpfaFlow bad(4);
            bad.add(1,4,1,0);
            bad.add(2,3,1,-1);
            bad.add(3,2,1,0);
            if (connected) bad.add(1,2,1,0);
            bool caught = false;
            try { bad.flow(1,4); }
            catch (const invalid_argument &) { caught = true; }
            need(caught);
            for (int id = 0; id < (int)bad.e.size(); id += 2) need(bad.used(id) == 0);
        }
        SpfaFlow wide(3);
        wide.add(1,2,LLONG_MAX,1);
        wide.add(2,3,LLONG_MAX,1);
        need(wide.flow(1,3) == make_pair(LLONG_MAX,I(LLONG_MAX)*2));
        need(wide.flow(1,3) == make_pair(0LL,I(0)));
        SpfaFlow distance(4);
        for (int u = 1; u < 4; u++) distance.add(u,u+1,1,LLONG_MAX);
        need(distance.flow(1,4) == make_pair(1LL,I(LLONG_MAX)*3));
        cout << "PASS " << cases << " graphs " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
