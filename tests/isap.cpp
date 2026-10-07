#include "../src/compact/isap.hpp"
namespace source_sap
{
#include "fixtures/isap_sources/sap.inc"
}
namespace source_bfs
{
#include "fixtures/isap_sources/bfs.inc"
}
using I = __int128_t;
using Arc = tuple<int,int,long long>;
long long checks = 0, cases = 0, bfs_cases = 0;
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
void certificate(const Isap &g, int s, int t, long long f, bool full)
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
void check(int n, int s, int t, const vector<Arc> &e)
{
    cases++;
    long long want = oracle(n,s,t,e);
    Isap g(n);
    source_sap::init();
    source_bfs::init();
    vector<vector<int>> und(n+1);
    for (auto [u,v,c] : e)
    {
        int id = g.add(u,v,c);
        need(g.e[id].from == u && g.e[id].to == v && !(id&1));
        source_sap::addedge(u,v,c);
        source_bfs::addedge(u,v,c);
        und[u].push_back(v);
        und[v].push_back(u);
    }
    need(g.flow(s,t,0) == 0);
    long long f = g.flow(s,t,want/2);
    need(f == want/2);
    certificate(g,s,t,f,f == want);
    f += g.flow(s,t);
    need(f == want);
    certificate(g,s,t,f,true);
    need(g.flow(s,t) == 0);
    need(source_sap::sap(s,t,n) == want);
    need(source_sap::sap(s,t,n) == 0);
    vector<int> vis(n+1);
    function<void(int)> visit = [&](int u)
    {
        vis[u] = 1;
        for (int v : und[u])
            if (!vis[v]) visit(v);
    };
    visit(t);
    if (vis[s])
    {
        bfs_cases++;
        need(source_bfs::sap(s,t,n) == want);
        need(source_bfs::sap(s,t,n) == 0);
    }
    // Retain feasible old flow while adding a new direct arc.
    g.add(s,t,7);
    need(g.flow(s,t,3) == 3);
    certificate(g,s,t,f+3,false);
    need(g.flow(s,t) == 4);
    certificate(g,s,t,f+7,true);
}
int main(int argc, char **argv)
{
    if (argc > 1 && string(argv[1]) == "source-disconnected")
    {
        source_bfs::init();
        cout << source_bfs::sap(1,2,2) << '\n';
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
                        int c = x%3;
                        x /= 3;
                        if (c) e.push_back({u,v,c});
                    }
            check(3,1,3,e);
        }
        mt19937 rng(4163);
        for (int it = 0; it < 3000; it++)
        {
            int n = 2+rng()%7, s = 1+rng()%n, t = 1+rng()%n;
            if (s == t) t = t%n+1;
            vector<Arc> e;
            for (int j = 0; j < it%30; j++)
                e.push_back({1+rng()%n,1+rng()%n,rng()%11});
            check(n,s,t,e);
        }
        // The source four-argument add stores signed net flow in [-rw,w].
        for (int w = 0; w <= 4; w++)
            for (int rw = 0; rw <= 4; rw++)
                for (bool reverse : {false,true})
                {
                    int s = reverse ? 2 : 1, t = 3-s;
                    source_sap::init();
                    source_bfs::init();
                    source_sap::addedge(1,2,w,rw);
                    source_bfs::addedge(1,2,w,rw);
                    Isap g(2);
                    g.add(1,2,w);
                    g.add(2,1,rw);
                    int expected = reverse ? rw : w;
                    need(g.flow(s,t) == expected);
                    need(source_sap::sap(s,t,2) == expected);
                    need(source_bfs::sap(s,t,2) == expected);
                    need(g.used(0)-g.used(2) == source_sap::edge[0].flow);
                }
        Isap huge(3);
        huge.add(1,2,LLONG_MAX);
        huge.add(2,3,LLONG_MAX);
        need(huge.flow(1,3,LLONG_MAX-1) == LLONG_MAX-1);
        need(huge.flow(1,3) == 1);
        certificate(huge,1,3,LLONG_MAX,true);
        if (argc == 1)
        {
            int n = 100000;
            Isap chain(n);
            for (int u = 1; u < n; u++) chain.add(u,u+1,2);
            need(chain.flow(1,n,1) == 1);
            need(chain.flow(1,n) == 1);
            certificate(chain,1,n,2,true);
            // Many vertices initially reach t, but the only exit saturates.
            Isap branches(n);
            for (int u = 2; u < n; u++)
            {
                branches.add(1,u,1);
                branches.add(u,n,1);
            }
            need(branches.flow(1,n) == n-2);
            certificate(branches,1,n,n-2,true);
            Isap dead(n);
            for (int u = 1; u < n-1; u++) dead.add(u,u+1,1);
            need(dead.flow(1,n) == 0);
            certificate(dead,1,n,0,true);
        }
        cout << "PASS " << cases << " graphs " << bfs_cases << " BFS-source graphs " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
