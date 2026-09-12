#include <bits/stdc++.h>
#include <cassert>
namespace compact {
#include "../src/compact/subset_convolution.hpp"
}
namespace classic {
#include "../src/classic/subset_convolution.hpp"
}
using namespace std;
long long power(long long x,int n,int p)
{
    long long a=1;
    for(;n;n>>=1,x=x*x%p) if(n&1) a=a*x%p;
    return a;
}
template<int p>
void check(const vector<int>&a,const vector<int>&b)
{
    using A=compact::SetConvolution<p>;
    using B=classic::Set_Convolution<p>;
    typename A::Poly aa(a.begin(),a.end()),bb(b.begin(),b.end());
    typename B::Poly aaa(a.begin(),a.end()),bbb(b.begin(),b.end());
    int n=a.size();
    for(char op:string("|&^"))
    {
        if(op=='^' && p%2==0) continue;
        vector<long long> want(n),forward(n);
        for(int i=0;i<n;i++)
            for(int j=0;j<n;j++)
            {
                int k=op=='|'? i|j:op=='&'? i&j:i^j;
                want[k]=(want[k]+1LL*a[i]*b[j])%p;
                int sign=op=='|'? ((i|j)==i):op=='&'?((i&j)==i):(__builtin_parity(unsigned(i&j))?-1:1);
                forward[i]=(forward[i]+1LL*sign*a[j]+p)%p;
            }
        auto x=aa;
        auto y=aaa;
        A::transform(x,op);
        B::Transform(y,op);
        for(int i=0;i<n;i++) assert(x[i].v==forward[i] && y[i].v==forward[i]);
        A::transform(x,op,true);
        B::Transform(y,op,true);
        for(int i=0;i<n;i++) assert(x[i].v==a[i] && y[i].v==a[i]);
        x=A::multiply(aa,bb,op);
        y=B::Multiply(aaa,bbb,op);
        for(int i=0;i<n;i++) assert(x[i].v==want[i] && y[i].v==want[i]);
    }
    auto x=compact::subset_convolution<p>(aa,bb);
    auto y=classic::Subset_Convolution<p>(aaa,bbb);
    for(int s=0;s<n;s++)
    {
        long long want=0;
        for(int t=s;;t=(t-1)&s)
        {
            want=(want+1LL*a[t]*b[s^t])%p;
            if(t==0) break;
        }
        assert(x[s].v==want && y[s].v==want);
    }
}
template<int p>
void small()
{
    mt19937 rng(p);
    for(int t=0;t<150;t++)
    {
        int n=1<<(rng()%7);
        vector<int>a(n),b(n);
        for(int i=0;i<n;i++)
        {
            a[i]=rng()%p;
            b[i]=rng()%p;
        }
        check<p>(a,b);
    }
}
void large()
{
    const int p=1000000009,m=18,n=1<<m;
    using A=compact::SetConvolution<p>;
    using B=classic::Set_Convolution<p>;
    typename A::Poly a(n),b(n);
    typename B::Poly aa(n),bb(n);
    for(int i=0;i<n;i++)
    {
        int k=__builtin_popcount(unsigned(i));
        int x=power(123,k,p),y=power(456,k,p);
        a[i]=x;
        b[i]=y;
        aa[i]=x;
        bb[i]=y;
    }
    for(char op:string("|&^s"))
    {
        auto x=op=='s'?compact::subset_convolution<p>(a,b):A::multiply(a,b,op);
        auto y=op=='s'?classic::Subset_Convolution<p>(aa,bb):B::Multiply(aa,bb,op);
        for(int i=0;i<n;i++)
        {
            int k=__builtin_popcount(unsigned(i));
            long long v=op=='|'?power(123+456+123*456,k,p):op=='&'?power(123*456,k,p)*power(1+123+456,m-k,p)%p:op=='^'?power(123+456,k,p)*power(1+123*456,m-k,p)%p:power(123+456,k,p);
            assert(x[i].v==v && y[i].v==v);
        }
    }
}
int main()
{
    small<2>();
    small<8>();
    small<9>();
    small<998244353>();
    small<1000000009>();
    small<2147483647>();
    for(int x=0;x<81;x++)
        for(int y=0;y<81;y++)
        {
            vector<int>a(4),b(4);
            int u=x,v=y;
            for(int i=0;i<4;i++)
            {
                a[i]=u%3==2?4:u%3;
                b[i]=v%3==2?4:v%3;
                u/=3;
                v/=3;
            }
            check<5>(a,b);
        }
    large();
    cout << "Set convolutions dual direct-character and submask oracles, composite moduli, INT_MAX and 18-bit tensor identities PASS\n";
}
