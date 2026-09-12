#include <bits/stdc++.h>
#include <cassert>
namespace compact {
#include "../src/compact/polynomial_shift.hpp"
#include "../src/compact/chirp_z.hpp"
}
namespace classic {
#include "../src/classic/polynomial_shift.hpp"
#include "../src/classic/chirp_z.hpp"
}
using namespace std;
long long power(long long x,long long n,int p)
{
    long long ans=1;
    for(;n;n>>=1,x=x*x%p) if(n&1) ans=ans*x%p;
    return ans;
}
long long horner(const vector<int>& f,long long x,int p)
{
    long long ans=0;
    for(int i=int(f.size())-1;i>=0;i--) ans=(ans*x+f[i])%p;
    return ans;
}
template<int p,int root>
void small()
{
    using Z=compact::ModInt<p>;
    using W=classic::Mod_Int<p>;
    constexpr int cap=compact::NttConvolution<p,root>::max_size;
    mt19937 rng(p);
    for(int trial=0;trial<400;trial++)
    {
        int n=rng()%(min(25,(cap+1)/2)+1);
        vector<int> f(n);
        for(int &x:f) x=rng()%p;
        vector<Z> a(f.begin(),f.end());
        vector<W> b(f.begin(),f.end());
        int c=rng()%p;
        auto x=compact::polynomial_shift<p,root>(a,Z(c));
        auto y=classic::Polynomial_Shift<p,root>(b,W(c));
        vector<long long> want(n),choose(1,1);
        for(int i=0;i<n;i++)
        {
            for(int j=0;j<=i;j++)
                want[j]=(want[j]+f[i]*choose[j]%p*power(c,i-j,p))%p;
            choose.push_back(0);
            for(int j=i+1;j>0;j--) choose[j]=(choose[j]+choose[j-1])%p;
        }
        assert(x.size()==f.size() && y.size()==f.size());
        for(int i=0;i<n;i++) assert(x[i].v==want[i] && y[i].v==want[i]);
    }
    for(int trial=0;trial<600;trial++)
    {
        int n=rng()%(min(32,cap)+1);
        int m=rng()%(min(40,cap-max(1,n)+1)+1);
        if(trial%3==0 && cap<=32 && n>0) m=cap-n+1;
        int start=rng()%p,ratio=trial%5==0?0:trial%5==1?1:rng()%p;
        vector<int> f(n);
        for(int &x:f) x=rng()%p;
        vector<Z> a(f.begin(),f.end());
        vector<W> b(f.begin(),f.end());
        auto x=compact::chirp_z<p,root>(a,Z(start),Z(ratio),m);
        auto y=classic::Chirp_Z<p,root>(b,W(start),W(ratio),m);
        assert(x.size()==size_t(m) && y.size()==size_t(m));
        long long point=start;
        for(int i=0;i<m;i++)
        {
            long long want=horner(f,point,p);
            assert(x[i].v==want && y[i].v==want);
            point=point*ratio%p;
        }
    }
}
void large()
{
    const int p=998244353,n=200001,m=200000;
    using Z=compact::ModInt<p>;
    using W=classic::Mod_Int<p>;
    vector<Z> f(n,1);
    vector<W> g(n,1);
    auto x=compact::chirp_z(f,Z(123),Z(3),m);
    auto y=classic::Chirp_Z(g,W(123),W(3),m);
    long long point=123;
    for(int i=0;i<m;i++)
    {
        long long want=point==1?n:(power(point,n,p)-1+p)*power((point-1+p)%p,p-2,p)%p;
        assert(x[i].v==want && y[i].v==want);
        point=point*3%p;
    }
    // Independently build (x+7)^d by the integer binomial recurrence modulo p.
    const int d=131072;
    f.resize(d+1);
    g.resize(d+1);
    long long bin=1;
    for(int i=0;i<=d;i++)
    {
        long long v=bin*power(7,d-i,p)%p;
        f[i]=v;
        g[i]=v;
        if(i<d) bin=bin*(d-i)%p*power(i+1,p-2,p)%p;
    }
    for(int c:{p-7,13})
    {
        x=compact::polynomial_shift(f,Z(c));
        y=classic::Polynomial_Shift(g,W(c));
        bin=1;
        for(int i=0;i<=d;i++)
        {
            long long want=bin*power((7+c)%p,d-i,p)%p;
            assert(x[i].v==want && y[i].v==want);
            if(i<d) bin=bin*(d-i)%p*power(i+1,p-2,p)%p;
        }
    }
}
int main()
{
    small<2,1>();
    small<3,2>();
    small<17,3>();
    small<97,5>();
    small<998244353,3>();
    small<167772161,3>();
    small<2013265921,31>();
    large();
    cout << "Polynomial shift and Chirp-Z dual Pascal/Horner oracles, zero/one ratios, small-field capacity boundaries and large binomial/geometric identities PASS\n";
}
