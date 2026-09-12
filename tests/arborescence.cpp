#include "../src/compact/graph_advanced.hpp"
#include "../src/classic/graph_advanced.hpp"
#include <cassert>
#include <iostream>
using I = __int128_t;
using Edge = Arborescence::Edge;

void check(int n,int root,const vector<Edge> &edges)
{
    vector<vector<Edge>> incoming(n);
    for(auto e:edges)
        if(e.u!=e.v)
            incoming[e.v].push_back(e);
    vector<int> parent(n,-1);
    optional<I> expected;
    auto enumerate=[&](auto &&self,int v,I cost)->void
    {
        if(v==n)
        {
            for(int start=0;start<n;start++)
            {
                int u=start;
                int steps=0;
                while(u!=root && steps<n)
                {
                    u=parent[u];
                    steps++;
                }
                if(u!=root)
                    return;
            }
            if(!expected || cost<*expected)
                expected=cost;
            return;
        }
        if(v==root)
        {
            self(self,v+1,cost);
            return;
        }
        for(auto e:incoming[v])
        {
            parent[v]=e.u;
            self(self,v+1,cost+e.w);
        }
    };
    enumerate(enumerate,0,0);
    vector<Directed_MST::Edge> other;
    for(auto e:edges)
        other.push_back({e.u,e.v,e.w});
    assert(Arborescence::solve(n,root,edges)==expected);
    assert(Directed_MST::Solve(n,root,other)==expected);
}

int main()
{
    check(1,0,{});
    check(2,0,{{0,1,-1}});
    check(3,0,{{1,2,0},{2,1,0}});
    check(1,0,{{0,0,-(I(1)<<60)}});
    for(int mask=0;mask<4096;mask++)
    {
        vector<Edge> edges;
        int state=mask;
        for(int u=0;u<3;u++)
            for(int v=0;v<3;v++)
                if(u!=v)
                {
                    int type=state%4;
                    state/=4;
                    if(type)
                        edges.push_back({u,v,type==1?-3:type==2?0:5});
                }
        for(int root=0;root<3;root++)
            check(3,root,edges);
    }
    mt19937 rng(4716);
    for(int t=0;t<500;t++)
    {
        int n=2+rng()%5;
        vector<Edge> edges;
        for(int i=0;i<12;i++)
            edges.push_back({int(rng()%n),int(rng()%n),int(rng()%21)-10});
        for(int root=0;root<n;root++)
            check(n,root,edges);
        shuffle(edges.begin(),edges.end(),rng);
        check(n,0,edges);
    }
    for(I scale:{I(1),I(1)<<100})
    {
        int n=800;
        vector<Edge> edges={{0,1,99*scale},{0,n-1,6*scale},{1,0,-1000*scale}};
        for(int i=1;i+1<n;i++)
        {
            edges.push_back({i,i+1,-scale});
            edges.push_back({i+1,i,-scale});
        }
        vector<Directed_MST::Edge> other;
        for(auto e:edges)
            other.push_back({e.u,e.v,e.w});
        I expected=(I(7)-(n-1))*scale;
        assert(Arborescence::solve(n,0,edges)==expected);
        assert(Directed_MST::Solve(n,0,other)==expected);
    }
    cout << "Arborescence dual exhaustive all-root incoming-edge oracle, loops/parallel edges and 800-vertex nested contractions PASS\n";
}
