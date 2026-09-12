#include <bits/stdc++.h>
#include <cassert>
namespace compact {
#include "../src/compact/euler_lca.hpp"
#include "../src/compact/tree_diameter.hpp"
}
namespace classic {
#include "../src/classic/euler_lca.hpp"
#include "../src/classic/tree_diameter.hpp"
}
using namespace std;
using ll=long long;
void check(int n,const vector<tuple<int,int,ll>>&edges)
{
    compact::EulerLCA lca(n);
    classic::Euler_LCA<10,5> old;
    old.Init(n);
    vector<vector<pair<int,ll>>> g(n);
    for(auto [u,v,w]:edges)
    {
        lca.add(u+1,v+1,w);
        old.Insert(u+1,v+1,w);
        g[u].push_back({v,w});
        g[v].push_back({u,w});
    }
    vector<vector<ll>> d(n,vector<ll>(n));
    for(int start=0;start<n;start++)
    {
        vector<int> seen(n);
        queue<int> q;
        q.push(start);
        seen[start]=1;
        while(!q.empty())
        {
            int u=q.front();
            q.pop();
            for(auto [v,w]:g[u]) if(!seen[v])
            {
                __int128 value=__int128(d[start][u])+w;
                assert(value<=LLONG_MAX);
                d[start][v]=ll(value);
                seen[v]=1;
                q.push(v);
            }
        }
    }
    for(int root=1;root<=n;root++)
    {
        lca.build(root);
        old.Build(root);
        for(int u=0;u<n;u++) for(int v=0;v<n;v++)
        {
            assert(lca.weighted_distance(u+1,v+1)==d[u][v]);
            assert(old.Weighted_Distance(u+1,v+1)==d[u][v]);
        }
    }
    auto dist=[&](int u,int v) {return lca.weighted_distance(u+1,v+1);};
    auto dist2=[&](int u,int v) {return old.Weighted_Distance(u+1,v+1);};
    vector<compact::TreeDiameter>a(1<<n);
    vector<classic::Tree_Diameter>b(1<<n);
    for(int mask=0;mask<(1<<n);mask++)
    {
        if(mask)
        {
            int v=__builtin_ctz(unsigned(mask));
            a[mask]=a[mask^(1<<v)];
            b[mask]=b[mask^(1<<v)];
            a[mask].insert(v,dist);
            b[mask].Insert(v,dist2);
        }
        ll length=0;
        for(int i=0;i<n;i++) if(mask>>i&1)
            for(int j=0;j<n;j++) if(mask>>j&1) length=max(length,d[i][j]);
        assert(a[mask].length==length && b[mask].length==length);
        for(int v=0;v<n;v++)
        {
            auto x=a[mask].farthest(v,dist);
            auto y=b[mask].Farthest(v,dist2);
            if(!mask) {assert(!x && !y); continue;}
            ll want=0;
            for(int i=0;i<n;i++) if(mask>>i&1) want=max(want,d[i][v]);
            assert(x && y && x->second==want && y->second==want);
            assert((mask>>x->first&1) && (mask>>y->first&1));
            assert(d[x->first][v]==want && d[y->first][v]==want);
        }
        auto x=a[mask];
        auto y=b[mask];
        x.merge(x,dist);
        y.Merge(y,dist2);
        assert(x.length==length && y.length==length);
    }
    mt19937 rng(n);
    for(int t=0;t<1000;t++)
    {
        int x=rng()%a.size(),y=rng()%a.size();
        auto c=a[x];
        auto e=b[x];
        c.merge(a[y],dist);
        e.Merge(b[y],dist2);
        assert(c.length==a[x|y].length && e.length==a[x|y].length);
        for(int v=0;v<n && (x|y);v++)
            assert(c.farthest(v,dist)->second==a[x|y].farthest(v,dist)->second);
    }
}
int main()
{
    mt19937 rng(8235);
    for(int trial=0;trial<200;trial++)
    {
        int n=1+rng()%10;
        vector<tuple<int,int,ll>> e;
        for(int v=1;v<n;v++) e.emplace_back(v,rng()%v,trial%3==0?0:rng()%100);
        check(n,e);
    }
    check(2,{{0,1,LLONG_MAX}});
    check(3,{{0,1,LLONG_MAX/2},{1,2,LLONG_MAX/2}});
    cout << "Tree diameter dual exhaustive subsets, unions, farthest witnesses and weighted Euler LCA BFS/all-root oracles with zero and int64 distances PASS\n";
}
