#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct Dinic
{
    using ll=long long;
    struct Edge { int from,to; ll cap,initial; };
    int n; vector<Edge> e; vector<vector<int>> g;
    vector<int> dep,cur;
    Dinic(int n):n(n),g(n+1),dep(n+1),cur(n+1) {}
    int add(int u,int v,ll c)
    {
        assert(c>=0); int id=(int)e.size();
        e.push_back({u,v,c,c}); e.push_back({v,u,0,0});
        g[u].push_back(id); g[v].push_back(id+1); return id;
    }
    bool bfs(int s,int t)
    {
        fill(dep.begin(),dep.end(),-1); queue<int> q;
        dep[s]=0; q.push(s);
        while (!q.empty())
        {
            int u=q.front(); q.pop();
            for (int id:g[u]) if (e[id].cap&&dep[e[id].to]<0)
            { dep[e[id].to]=dep[u]+1; q.push(e[id].to); }
        }
        return dep[t]>=0;
    }
    ll dfs(int u,int t,ll f)
    {
        if (u==t) return f;
        for (int &i=cur[u];i<(int)g[u].size();i++)
        {
            int id=g[u][i],v=e[id].to;
            if (!e[id].cap||dep[v]!=dep[u]+1) continue;
            ll d=dfs(v,t,min(f,e[id].cap));
            if (d) { e[id].cap-=d; e[id^1].cap+=d; return d; }
        }
        return 0;
    }
    // Returns additional flow; reuse only with the same source/sink.
    ll flow(int s,int t,ll limit=LLONG_MAX)
    {
        assert(s!=t&&limit>=0); ll ans=0;
        while (ans<limit&&bfs(s,t))
        {
            fill(cur.begin(),cur.end(),0);
            while (ans<limit)
            {
                ll d=dfs(s,t,limit-ans);
                if (!d) break;
                ans+=d;
            }
        }
        return ans;
    }
    ll used(int id) const { return e[id].initial-e[id].cap; }
    vector<int> cut(int s)
    {
        bfs(s,s); vector<int> ans;
        for (int u=1;u<=n;u++) if (dep[u]>=0) ans.push_back(u);
        return ans;
    }
};

struct MinCostFlow
{
    using ll=long long; using i128=__int128_t;
    struct Edge { int from,to; ll cap,cost,initial; };
    int n; vector<Edge> e; vector<vector<int>> g;
    MinCostFlow(int n):n(n),g(n+1) {}
    int add(int u,int v,ll cap,ll cost)
    {
        assert(cap>=0&&cost!=LLONG_MIN); int id=(int)e.size();
        e.push_back({u,v,cap,cost,cap});
        e.push_back({v,u,0,-cost,0});
        g[u].push_back(id); g[v].push_back(id+1); return id;
    }
    ll used(int id) const { return e[id].initial-e[id].cap; }
    // Negative costs allowed; initial residual graph must have no negative cycle.
    pair<ll,i128> flow(int s,int t,ll limit=LLONG_MAX)
    {
        assert(s!=t&&limit>=0);
        const i128 inf=i128(1)<<120;
        vector<i128> h(n+1,0),d(n+1);
        vector<int> pre(n+1);
        // Super-source Bellman-Ford: feasible potentials for every vertex.
        for (int it=0;it<n;it++)
        {
            bool changed=false;
            for (auto &a:e) if (a.cap&&h[a.to]>h[a.from]+a.cost)
            { h[a.to]=h[a.from]+a.cost; changed=true; }
            if (!changed) break;
            if (it==n-1) throw invalid_argument("negative cycle");
        }
        ll f=0; i128 cost=0;
        while (f<limit)
        {
            fill(d.begin(),d.end(),inf); d[s]=0;
            priority_queue<pair<i128,int>,vector<pair<i128,int>>,greater<pair<i128,int>>> q;
            q.push({0,s});
            while (!q.empty())
            {
                auto [du,u]=q.top(); q.pop();
                if (du!=d[u]) continue;
                for (int id:g[u])
                {
                    auto &a=e[id];
                    i128 nd=du+a.cost+h[u]-h[a.to];
                    if (a.cap&&nd<d[a.to])
                    { d[a.to]=nd; pre[a.to]=id; q.push({nd,a.to}); }
                }
            }
            if (d[t]==inf) break;
            for (int u=1;u<=n;u++) if (d[u]!=inf) h[u]+=d[u];
            ll take=limit-f;
            for (int u=t;u!=s;u=e[pre[u]].from)
                take=min(take,e[pre[u]].cap);
            for (int u=t;u!=s;u=e[pre[u]].from)
            {
                int id=pre[u]; e[id].cap-=take; e[id^1].cap+=take;
                cost+=i128(take)*e[id].cost;
            }
            f+=take;
        }
        return {f,cost};
    }
};

int main()
{
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n,m,s,t; cin>>n>>m>>s>>t;
    Dinic g(n);
    for (int i=0;i<m;i++) { int u,v; long long c; cin>>u>>v>>c; g.add(u,v,c); }
    cout<<g.flow(s,t)<<'\n';
}
