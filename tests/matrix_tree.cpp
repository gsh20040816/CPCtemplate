#include "../src/classic/matrix_tree.hpp"
#include "../src/compact/matrix_tree.hpp"
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
template<int P> void check(int n,const vector<E>&edges)
{
    using M=MatrixTree<P>;
    using C=Matrix_Tree<P>;
    vector<typename M::Edge> a;
    vector<typename C::Edge> b;
    for(auto [u,v,w]:edges)
    {
        a.push_back({u,v,w});
        b.push_back({u,v,w});
    }
    for(int root=0;root<n;root++)
        for(int kind=0;kind<3;kind++)
        {
            B want=oracle(n,edges,root,kind)%P;
            if(want<0) want+=P;
            int x=M::count(n,a,root,typename M::Kind(kind)).v;
            int y=C::Count(n,b,root,typename C::Kind(kind)).v;
            assert(x==want.convert_to<int>() && x==y);
        }
}
int main()
{
    check<2>(1,{{0,0,8}});
    check<998244353>(1,{});
    check<998244353>(2,{{0,1,LLONG_MIN},{0,1,LLONG_MAX}});
    mt19937 rng(20260920);
    for(int t=0;t<400;t++)
    {
        int n=1+rng()%5;
        vector<E> edges;
        for(int i=0,m=rng()%10;i<m;i++)
            edges.push_back({rng()%n,rng()%n,int(rng()%9)-4});
        check<2>(n,edges);
        check<3>(n,edges);
        check<998244353>(n,edges);
    }
    using M=MatrixTree<998244353>;
    using C=Matrix_Tree<998244353>;
    using Z=M::Z;
    int n=220;
    for(int kind=0;kind<3;kind++)
    {
        vector<M::Edge>a;
        vector<C::Edge>b;
        for(int u=0;u<n;u++)
            for(int v=0;v<n;v++)
                if(u!=v && (kind || u<v))
                {
                    a.push_back({u,v,-3});
                    b.push_back({u,v,-3});
                }
        Z want=Z(n).pow(n-2)*Z(-3).pow(n-1);
        assert(M::count(n,a,37,M::Kind(kind)).v==want.v);
        assert(C::Count(n,b,37,C::Kind(kind)).v==want.v);
    }
    cout<<"Matrix tree dual exhaustive weighted edge sets, all roots/directions, parallel loops, signed weights and 220-vertex Cayley families PASS\n";
}
