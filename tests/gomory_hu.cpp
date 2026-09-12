#include "../src/classic/gomory_hu.hpp"
#include "../src/compact/gomory_hu.hpp"
#include "../src/compact/cut_tree_queries.hpp"
#include "../src/classic/cut_tree_queries.hpp"
#include <cassert>
#include <iostream>
using Edge=tuple<int,int,long long>;
static Network_Flow<100,2000> flow;

void verify(int n,const vector<Edge> &edges,const vector<Edge> &tree,bool brute)
{
    assert(tree.size()==size_t(n-1));
    vector<vector<tuple<int,long long,int>>> g(n);
    for(int i=0;i<n-1;i++)
    {
        auto [u,v,w]=tree[i];
        assert(0<=u && u<n && 0<=v && v<n && u!=v && w>=0);
        g[u].push_back({v,w,i});
        g[v].push_back({u,w,i});
    }
    vector<vector<long long>> paths(n,vector<long long>(n));
    for(int s=0;s<n;s++)
    {
        vector<bool> seen(n);
        auto dfs=[&](auto &&self,int u,int parent,long long value)->void
        {
            assert(!seen[u]);
            seen[u]=true;
            paths[s][u]=value;
            for(auto [v,w,id]:g[u])
                if(v!=parent)
                    self(self,v,u,min(value,w));
        };
        dfs(dfs,s,-1,LLONG_MAX);
        assert(count(seen.begin(),seen.end(),true)==n);
    }
    assert(cut_tree_values(n,tree)==paths);
    assert(Cut_Tree_Values(n,tree)==paths);
    // Every tree edge must describe an actual minimum cut of the original graph.
    for(int banned=0;banned<n-1;banned++)
    {
        auto [s,t,value]=tree[banned];
        vector<bool> side(n);
        auto dfs=[&](auto &&self,int u,int parent)->void
        {
            side[u]=true;
            for(auto [v,w,id]:g[u])
                if(v!=parent && id!=banned)
                    self(self,v,u);
        };
        dfs(dfs,s,-1);
        __int128_t weight=0;
        for(auto [u,v,w]:edges)
            if(side[u]!=side[v])
                weight+=w;
        assert(weight==value);
    }
    if(brute)
    {
        vector<vector<long long>> expected(n,vector<long long>(n,LLONG_MAX));
        for(int mask=1;mask<(1<<n)-1;mask++)
        {
            long long cost=0;
            for(auto [u,v,w]:edges)
                if(((mask>>u)&1)!=((mask>>v)&1))
                    cost+=w;
            for(int u=0;u<n;u++)
                for(int v=u+1;v<n;v++)
                    if(((mask>>u)&1)!=((mask>>v)&1))
                        expected[u][v]=min(expected[u][v],cost);
        }
        for(int u=0;u<n;u++)
            for(int v=u+1;v<n;v++)
                assert(paths[u][v]==expected[u][v]);
    }
}

void check(int n,vector<Edge> edges,bool brute=true)
{
    verify(n,edges,gomory_hu(n,edges),brute);
    verify(n,edges,Gomory_Hu(n,edges,flow),brute);
}

int main()
{
    check(1,{{0,0,100}});
    for(int mask=0;mask<729;mask++)
    {
        vector<Edge> edges;
        int state=mask;
        for(int u=0;u<4;u++)
            for(int v=u+1;v<4;v++)
            {
                edges.push_back({u,v,state%3});
                state/=3;
            }
        check(4,edges);
    }
    mt19937 rng(4899);
    for(int t=0;t<250;t++)
    {
        int n=2+rng()%7;
        vector<Edge> edges;
        for(int i=0;i<20;i++)
            edges.push_back({int(rng()%n),int(rng()%n),rng()%30});
        check(n,edges);
        shuffle(edges.begin(),edges.end(),rng);
        check(n,edges);
    }
    vector<Edge> path;
    for(int i=0;i<69;i++)
        path.push_back({i,i+1,LLONG_MAX/70});
    check(70,path,false);
    check(70,{},false);
    cout << "Gomory-Hu dual all-pairs cut oracle, tree-edge cut certificates, multigraph reorder and 70-vertex high capacities PASS\n";
}
