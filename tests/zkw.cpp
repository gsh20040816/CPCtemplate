#include "../src/compact/zkw_flow.hpp"
namespace upstream
{
#include "fixtures/zkw_sources/kuangbin.inc"
}
using I = __int128_t;
struct Arc
{
    int u, v, cap, cost;
};
long long checks = 0, cases = 0, source_cases = 0;
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
void check(int n, const vector<Arc> &e)
{
    cases++;
    auto want = enumerate(n,e);
    int maxf = (int)want.size()-1;
    ZkwFlow g(n);
    bool nonnegative = true;
    upstream::solve.init();
    for (auto a : e)
    {
        g.add(a.u,a.v,a.cap,a.cost);
        upstream::solve.addedge(a.u-1,a.v-1,a.cap,a.cost);
        if (a.cost < 0) nonnegative = false;
    }
    if (nonnegative)
    {
        source_cases++;
        auto [cost,f] = upstream::solve.mincostmaxflow(0,n-1,n);
        need(f == maxf && I(cost) == *want.back());
        vector<long long> sf;
        for (int i = 0; i < (int)e.size(); i++) sf.push_back(upstream::edge[2*i].flow);
        certificate(n,e,sf,f,cost);
        need(upstream::solve.mincostmaxflow(0,n-1,n) == make_pair(0,0));
    }
    need(g.flow(1,n,0) == make_pair(0LL,I(0)));
    I total = 0;
    for (int k = 1; k <= maxf; k++)
    {
        auto [f,c] = g.flow(1,n,1);
        total += c;
        need(f == 1 && total == *want[k]);
        vector<long long> used;
        for (int id = 0; id < (int)g.e.size(); id += 2)
        {
            used.push_back(g.used(id));
            need(g.e[id^1].cap == used.back());
        }
        certificate(n,e,used,k,total);
    }
    need(g.flow(1,n) == make_pair(0LL,I(0)));
    ZkwFlow full(n);
    for (auto a : e) full.add(a.u,a.v,a.cap,a.cost);
    need(full.flow(1,n) == make_pair((long long)maxf,*want.back()));
}
int main(int argc, char **argv)
{
    if (argc > 1 && string(argv[1]) == "source-product")
    {
        upstream::solve.init();
        upstream::solve.addedge(0,1,50000,50000);
        upstream::solve.mincostmaxflow(0,1,2);
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
                        int z = x%3;
                        x /= 3;
                        if (z) e.push_back({u,v,1,z-1});
                    }
            check(3,e);
        }
        mt19937 rng(4172);
        for (int it = 0; it < 2400; it++)
        {
            int n = 2+rng()%5;
            vector<int> h(n+1);
            if (it%2)
                for (int u = 1; u <= n; u++) h[u] = int(rng()%21)-10;
            vector<Arc> e;
            for (int j = 0; j < it%9; j++)
            {
                int u = 1+rng()%n, v = 1+rng()%n;
                e.push_back({u,v,int(rng()%3),int(rng()%5)+h[v]-h[u]});
            }
            check(n,e);
        }
        vector<Arc> cancel{{1,2,1,0},{2,3,1,-5},{3,4,1,0},{1,3,1,0},{2,4,1,0}};
        check(4,cancel);
        ZkwFlow g(4);
        for (auto a : cancel) g.add(a.u,a.v,a.cap,a.cost);
        need(g.flow(1,4,1) == make_pair(1LL,I(-5)));
        need(g.used(2) == 1);
        need(g.flow(1,4) == make_pair(1LL,I(5)));
        need(g.used(2) == 0);
        // Zero initial labels are not feasible for arbitrary negative edges.
        upstream::solve.init();
        for (auto a : vector<Arc>{{1,2,1,0},{2,4,1,0},{1,3,1,-1},{3,2,1,0}})
            upstream::solve.addedge(a.u-1,a.v-1,a.cap,a.cost);
        need(upstream::solve.mincostmaxflow(0,3,4) == make_pair(0,1));
        check(4,{{1,2,1,0},{2,4,1,0},{1,3,1,-1},{3,2,1,0}});
        upstream::solve.init();
        upstream::solve.addedge(0,1,1,upstream::INF);
        need(upstream::solve.mincostmaxflow(0,1,2) == make_pair(0,0));
        ZkwFlow sentinel(2);
        sentinel.add(1,2,1,upstream::INF);
        need(sentinel.flow(1,2) == make_pair(1LL,I(upstream::INF)));
        for (bool connected : {false,true})
        {
            ZkwFlow bad(4);
            bad.add(1,4,1,0);
            bad.add(2,3,1,-1);
            bad.add(3,2,1,0);
            if (connected) bad.add(1,2,1,0);
            for (long long limit : {0LL,1LL})
            {
                bool caught = false;
                try { bad.flow(1,4,limit); }
                catch (const invalid_argument &) { caught = true; }
                need(caught);
                for (int id = 0; id < (int)bad.e.size(); id += 2) need(bad.used(id) == 0);
            }
        }
        ZkwFlow huge(3);
        huge.add(1,2,LLONG_MAX,1);
        huge.add(2,3,LLONG_MAX,1);
        need(huge.flow(1,3) == make_pair(LLONG_MAX,I(LLONG_MAX)*2));
        ZkwFlow wide(3);
        wide.add(1,2,1,-LLONG_MAX);
        wide.add(2,3,1,-LLONG_MAX);
        need(wide.flow(1,3) == make_pair(1LL,-I(LLONG_MAX)*2));
        if (argc == 1)
        {
            int n = 100000;
            ZkwFlow chain(n);
            for (int u = 1; u < n; u++) chain.add(u,u+1,1,0);
            need(chain.flow(1,n) == make_pair(1LL,I(0)));
            for (int id = 0; id < (int)chain.e.size(); id += 2) need(chain.used(id) == 1);
            ZkwFlow layers(502);
            for (int u = 2; u <= 501; u++)
            {
                layers.add(1,u,1,u);
                layers.add(u,502,1,0);
            }
            need(layers.flow(1,502) == make_pair(500LL,I(2+501)*500/2));
        }
        cout << "PASS " << cases << " graphs " << source_cases << " source graphs " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
