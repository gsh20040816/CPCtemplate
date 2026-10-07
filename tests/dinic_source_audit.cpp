#include "../src/compact/flow.hpp"
namespace upstream
{
#include "fixtures/dinic_sources/kuangbin.inc"
}
using I = __int128_t;
using Arc = tuple<int,int,long long>;
long long checks = 0, cases = 0, source_cases = 0;
void need(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("ORACLE_REJECT");
}
long long oracle(int n, int s, int t, const vector<Arc> &e)
{
    I best = I(1) << 120;
    for (int mask = 0; mask < (1 << n); mask++)
    {
        if (!(mask >> (s-1) & 1) || (mask >> (t-1) & 1)) continue;
        I sum = 0;
        for (auto [u,v,c] : e)
            if ((mask >> (u-1) & 1) && !(mask >> (v-1) & 1)) sum += c;
        best = min(best,sum);
    }
    return (long long)best;
}
void certificate(Dinic &g, int s, int t, long long f, bool full)
{
    vector<I> b(g.n+1);
    for (int id = 0; id < (int)g.e.size(); id += 2)
    {
        auto a = g.e[id];
        auto x = g.used(id);
        need(0 <= x && x <= a.initial);
        need(g.e[id^1].cap == x);
        b[a.from] += x;
        b[a.to] -= x;
    }
    for (int u = 1; u <= g.n; u++)
        need(b[u] == (u == s ? I(f) : u == t ? -I(f) : I(0)));
    auto cut = g.cut(s);
    vector<int> seen(g.n+1);
    for (int u : cut)
    {
        need(1 <= u && u <= g.n && !seen[u]);
        seen[u] = 1;
    }
    need(seen[s]);
    I value = 0;
    for (int id = 0; id < (int)g.e.size(); id += 2)
    {
        auto a = g.e[id];
        if (seen[a.from] && !seen[a.to]) value += a.initial;
    }
    if (full) need(!seen[t] && value == f);
}
void check(int n, int s, int t, const vector<Arc> &edges, long long want)
{
    cases++;
    upstream::init();
    Dinic g(n);
    for (auto [u,v,c] : edges)
    {
        upstream::addedge(u-1,v-1,c);
        g.add(u,v,c);
    }
    need(upstream::dinic(s-1,t-1,n) == want);
    vector<I> bal(n+1);
    for (int i = 0; i < (int)edges.size(); i++)
    {
        auto [u,v,c] = edges[i];
        auto e = upstream::edge[2+2*i];
        need(0 <= e.flow && e.flow <= c);
        need(upstream::edge[3+2*i].flow == -e.flow);
        bal[u] += e.flow;
        bal[v] -= e.flow;
    }
    for (int u = 1; u <= n; u++) need(bal[u] == (u==s ? I(want) : u==t ? -I(want) : I(0)));
    need(upstream::dinic(s-1,t-1,n) == 0);
    need(g.flow(s,t,0) == 0);
    need(g.flow(s,t,want/2) == want/2);
    certificate(g,s,t,want/2,want==0);
    need(g.flow(s,t) == want-want/2);
    certificate(g,s,t,want,true);
    need(g.flow(s,t) == 0);
}
int main(int argc, char **argv)
{
    if (argc > 1)
    {
        upstream::init();
        string mode = argv[1];
        if (mode == "source-nodes") return upstream::dinic(0,1,2010);
        if (mode == "source-inf")
        {
            upstream::addedge(0,1,upstream::INF+1);
            int f = upstream::dinic(0,1,2);
            cout << f << ' ' << upstream::edge[2].flow << '\n';
            return 0;
        }
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
                        int c = x%3;
                        x /= 3;
                        if (c) e.push_back({u,v,c});
                    }
            check(3,1,3,e,oracle(3,1,3,e));
        }
        mt19937 rng(4165);
        for (int it = 0; it < 2000; it++)
        {
            int n = 2+rng()%7, s = 1+rng()%n, t = 1+rng()%n;
            if (s == t) t = t%n+1;
            vector<Arc> e;
            for (int j = 0; j < it%30; j++) e.push_back({1+rng()%n,1+rng()%n,rng()%11});
            check(n,s,t,e,oracle(n,s,t,e));
        }
        for (int w = 0; w <= 4; w++)
            for (int rw = 0; rw <= 4; rw++)
                for (bool reverse : {false,true})
                {
                    upstream::init();
                    upstream::addedge(0,1,w,rw);
                    int s = reverse ? 1 : 0, t = 1-s;
                    need(upstream::dinic(s,t,2) == (reverse ? rw : w));
                    need(upstream::edge[2].flow == (reverse ? -rw : w));
                }
        vector<Arc> chain;
        for (int u = 1; u < 2009; u++) chain.push_back({u,u+1,1});
        check(2009,1,2009,chain,1);
        for (long long cap : {static_cast<long long>(upstream::INF)+1,LLONG_MAX})
        {
            Dinic g(2);
            g.add(1,2,cap);
            need(g.flow(1,2) == cap);
            certificate(g,1,2,cap,true);
        }
        cout << "PASS " << cases << " graphs " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
