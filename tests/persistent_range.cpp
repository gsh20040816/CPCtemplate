#include <bits/stdc++.h>
#include <cassert>
namespace compact {
#include "../src/compact/persistent_range.hpp"
}
namespace classic {
#include "../src/classic/persistent_range.hpp"
}
using namespace std;
using ll=long long;
ll sum(const vector<ll>&v,int l,int r)
{
    __int128 ans=0;
    for(int i=l;i<r;i++) ans+=v[i];
    assert(LLONG_MIN<=ans && ans<=LLONG_MAX);
    return ll(ans);
}
void small()
{
    mt19937 rng(84973);
    for(int trial=0;trial<200;trial++)
    {
        int n=1+rng()%20;
        compact::PersistentRange a(n);
        classic::Persistent_Range b(n);
        vector<vector<ll>> versions(1,vector<ll>(n));
        for(int step=0;step<100;step++)
        {
            int from=rng()%versions.size(),to=rng()%versions.size();
            int l=rng()%(n+1),r=rng()%(n+1);
            if(l>r) swap(l,r);
            if(step%9==0) l=0;
            if(step%11==0) r=n;
            auto next=versions[from];
            int x,y;
            if(step%2)
            {
                ll value=(ll(rng()%2000001)-1000000)*1000000;
                for(int i=l;i<r;i++) next[i]+=value;
                x=a.add(from,l,r,value);
                y=b.Add(from,l,r,value);
            }
            else
            {
                for(int i=l;i<r;i++) next[i]=versions[to][i];
                x=a.splice(from,to,l,r);
                y=b.Splice(from,to,l,r);
            }
            assert(x==int(versions.size()) && y==x);
            versions.push_back(next);
            size_t ca=a.t.size(),cb=b.t.size();
            for(int v:{0,from,to,x,int(rng()%versions.size())})
                for(int i=0;i<=n;i++)
                    for(int j=i;j<=n;j++)
                    {
                        ll want=sum(versions[v],i,j);
                        assert(a.query(v,i,j)==want);
                        assert(b.Query(v,i,j)==want);
                    }
            assert(a.t.size()==ca && b.t.size()==cb);
            assert(a.t[0].sum==0 && a.t[0].lazy==0);
            assert(b.t[0].sum==0 && b.t[0].lazy==0);
        }
    }
}
void large()
{
    const int n=200000;
    compact::PersistentRange a(n);
    classic::Persistent_Range b(n);
    vector<int> constant{0};
    for(int i=1;i<=10000;i++)
    {
        int v=a.add(constant.back(),0,n,1);
        assert(v==b.Add(constant.back(),0,n,1));
        constant.push_back(v);
        int l=i%12345,r=n-i%31777;
        size_t before=a.t.size();
        int w=a.splice(v,constant[i/2],l,r);
        assert(w==b.Splice(v,constant[i/2],l,r));
        assert(a.t.size()-before<=160);
        ll want=1LL*n*i-1LL*(i-i/2)*(r-l);
        assert(a.query(w,0,n)==want && b.Query(w,0,n)==want);
        assert(a.query(v,0,n)==1LL*n*i);
        assert(a.query(w,l,r)==1LL*(r-l)*(i/2));
        assert(b.Query(w,l,r)==1LL*(r-l)*(i/2));
    }
    compact::PersistentRange x(INT_MAX);
    classic::Persistent_Range y(INT_MAX);
    int v=x.add(0,0,INT_MAX,1);
    assert(v==y.Add(0,0,INT_MAX,1));
    int w=x.splice(v,0,1,INT_MAX-1);
    assert(w==y.Splice(v,0,1,INT_MAX-1));
    assert(x.query(w,0,INT_MAX)==2 && y.Query(w,0,INT_MAX)==2);
    int z=x.add(w,INT_MAX-1,INT_MAX,-7);
    assert(z==y.Add(w,INT_MAX-1,INT_MAX,-7));
    assert(x.query(z,0,INT_MAX)==-5 && y.Query(z,0,INT_MAX)==-5);
    size_t nodes=x.t.size();
    int alias=x.splice(z,v,0,0);
    assert(x.t.size()==nodes && x.root[alias]==x.root[z]);
    int whole=x.splice(z,v,0,INT_MAX);
    assert(x.t.size()==nodes && x.root[whole]==x.root[v]);
}
int main()
{
    small();
    large();
    cout << "Persistent range dual branching vector oracle, lazy cross-version splice, immutable queries, sparse INT_MAX domain and logarithmic allocation PASS\n";
}
