#include "../src/classic/matrix_tree_mod.hpp"
#include "../src/compact/matrix_tree_mod.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B=boost::multiprecision::cpp_int;
using E=tuple<int,int,long long>;
B oracle(int n,const vector<E>&edges,int root,int kind)
{
    B result=0;
    for(unsigned mask=0;mask<(1U<<edges.size());mask++)
    {
        if(__builtin_popcount(mask)!=n-1) continue;
        vector<vector<int>> g(n);
        vector<int> degree(n);
        B weight=1;
        bool good=true;
        for(int i=0;i<(int)edges.size();i++)
            if(mask>>i&1)
            {
                auto [u,v,w]=edges[i];
                if(u==v) good=false;
                if(kind==2) swap(u,v);
                g[u].push_back(v);
                degree[u]++;
                if(!kind) g[v].push_back(u);
                weight*=w;
            }
        if(kind)
            for(int i=0;i<n;i++) if(degree[i]!=(i!=root)) good=false;
        for(int start=0;start<n;start++)
        {
            vector<int> seen(n);
            function<void(int)> dfs=[&](int u)
            {
                seen[u]=1;
                for(int v:g[u]) if(!seen[v]) dfs(v);
            };
            dfs(start);
            if(!seen[root]) good=false;
        }
        if(good) result+=weight;
    }
    return result;
}

void check(int n,const vector<E>&edges,long long mod)
{
    for(int root=0;root<n;root++)
        for(int kind=0;kind<3;kind++)
        {
            B want=oracle(n,edges,root,kind)%mod;
            if(want<0) want+=mod;
            auto x=MatrixTreeMod::count(n,edges,root,MatrixTreeMod::Kind(kind),mod);
            auto y=Matrix_Tree_Mod::Count(n,edges,root,Matrix_Tree_Mod::Kind(kind),mod);
            assert(x==y && x==want.convert_to<long long>());
        }
}
int main()
{
    vector<long long> mods{1,4,6,12,1000000006,LLONG_MAX};
    mt19937 rng(20260922);
    for(int t=0;t<300;t++)
    {
        int n=1+rng()%5;
        vector<E> edges;
        for(int i=0,m=rng()%10;i<m;i++)
            edges.push_back({rng()%n,rng()%n,int(rng()%13)-6});
        for(auto mod:mods) check(n,edges,mod);
    }
    for(auto mod:mods)
    {
        check(1,{{0,0,LLONG_MIN}},mod);
        check(2,{{0,1,LLONG_MAX-1},{0,1,LLONG_MAX-2},{1,0,LLONG_MIN},{1,1,LLONG_MAX}},mod);
    }
    int n=160;
    long long w=LLONG_MAX-7;
    B want=1;
    for(int i=0;i<n-2;i++) want*=n;
    for(int i=0;i<n-1;i++) want*=w;
    for(int kind=0;kind<3;kind++)
    {
        vector<E> edges;
        for(int u=0;u<n;u++)
            for(int v=0;v<n;v++)
                if(u!=v && (kind || u<v)) edges.push_back({u,v,w});
        for(long long mod:{1000000006LL,LLONG_MAX})
        {
            auto x=MatrixTreeMod::count(n,edges,37,MatrixTreeMod::Kind(kind),mod);
            auto y=Matrix_Tree_Mod::Count(n,edges,37,Matrix_Tree_Mod::Kind(kind),mod);
            assert(x==y && x==(want%mod).convert_to<long long>());
        }
    }
    cout<<"Composite-mod Matrix tree dual weighted edge-set oracle, all roots/directions, signed64 accumulation and large Cayley matrices PASS\n";
}
