#include "../src/compact/graph_advanced.hpp"
#include "../src/classic/graph_advanced.hpp"
#include <cassert>
#include <iostream>
using I = __int128_t;
using Matrix = vector<vector<I>>;

void check(const Matrix &w, optional<I> known = nullopt)
{
    int n=w.size();
    I expected=I(1)<<120;
    if(known)
        expected=*known;
    else
        for(int mask=1;mask<(1<<n)-1;mask+=2)
        {
            I cost=0;
            for(int u=0;u<n;u++)
                for(int v=u+1;v<n;v++)
                    if(((mask>>u)&1)!=((mask>>v)&1))
                        cost+=w[u][v];
            expected=min(expected,cost);
        }
    auto a=StoerWagner::solve(w);
    auto b=Global_Min_Cut::Solve(w);
    for(auto result:{a,b})
    {
        assert(result.first==expected);
        assert(!result.second.empty() && result.second.size()<w.size());
        vector<bool> inside(n);
        for(int v:result.second)
        {
            assert(0<=v && v<n && !inside[v]);
            inside[v]=true;
        }
        I cost=0;
        for(int u=0;u<n;u++)
            for(int v=u+1;v<n;v++)
                if(inside[u]!=inside[v])
                    cost+=w[u][v];
        assert(cost==expected);
    }
}

int main()
{
    for(int n=2;n<=4;n++)
    {
        int cases=1;
        for(int i=0;i<n*(n-1)/2;i++)
            cases*=3;
        for(int mask=0;mask<cases;mask++)
        {
            Matrix w(n,vector<I>(n));
            int state=mask;
            for(int u=0;u<n;u++)
                for(int v=u+1;v<n;v++)
                {
                    w[u][v]=w[v][u]=state%3;
                    state/=3;
                }
            check(w);
        }
    }
    mt19937 rng(1338);
    for(int t=0;t<500;t++)
    {
        int n=2+rng()%8;
        Matrix w(n,vector<I>(n));
        for(int i=0;i<30;i++)
        {
            int u=rng()%n,v=rng()%n;
            if(u!=v)
            {
                int c=rng()%20;
                w[u][v]+=c;
                w[v][u]+=c;
            }
        }
        check(w);
    }
    for(int n:{2,80,300})
    {
        I scale=I(1)<<100;
        Matrix ring(n,vector<I>(n));
        for(int i=0;i<n;i++)
        {
            int j=(i+1)%n;
            ring[i][j]+=scale;
            ring[j][i]+=scale;
        }
        check(ring,2*scale);
        Matrix complete(n,vector<I>(n,scale));
        for(int i=0;i<n;i++)
            complete[i][i]=0;
        check(complete,I(n-1)*scale);
        check(Matrix(n,vector<I>(n)),0);
    }
    cout << "Global min-cut dual exhaustive partition oracle, returned-side certificates, parallel sums and 300-vertex int128 families PASS\n";
}
