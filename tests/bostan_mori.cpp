#include <bits/stdc++.h>
#include <cassert>
namespace compact {
#include "../src/compact/bostan_mori.hpp"
}
namespace classic {
#include "../src/classic/bostan_mori.hpp"
}
using namespace std;
using U = unsigned long long;
long long power(long long a,U n,int p)
{
    long long r=1;
    for(;n;n>>=1,a=a*a%p)
        if(n&1) r=r*a%p;
    return r;
}
template<int mod,int g=3>
void rational_cases()
{
    using A=compact::BostanMori<mod,g>;
    using B=classic::Bostan_Mori<mod,g>;
    mt19937 rng(mod);
    int cap=min(16,(A::N::max_size+1)/2);
    for(int t=0;t<150;t++)
    {
        int x=rng()%(cap+1),y=1+rng()%cap;
        typename A::Poly p(x),q(y);
        typename B::Poly pp(x),qq(y);
        for(int i=0;i<x;i++)
        {
            int v=rng()%mod;
            p[i]=v;
            pp[i]=v;
        }
        for(int i=0;i<y;i++)
        {
            int v=i? rng()%mod:1+rng()%(mod-1);
            q[i]=v;
            qq[i]=v;
        }
        vector<long long> want(90);
        for(int n=0;n<90;n++)
        {
            long long v=n<x?p[n].v:0;
            for(int j=1;j<y && j<=n;j++)
                v=(v-q[j].v*want[n-j])%mod;
            want[n]=(v+mod)%mod*power(q[0].v,mod-2,mod)%mod;
            assert(A::coefficient(p,q,n).v==want[n]);
            assert(B::Coefficient(pp,qq,n).v==want[n]);
        }
    }
}
const int P=998244353;
using Matrix=vector<vector<long long>>;
Matrix multiply(Matrix a,Matrix b)
{
    int k=a.size();
    Matrix c(k,vector<long long>(k));
    for(int i=0;i<k;i++)
        for(int j=0;j<k;j++)
            for(int z=0;z<k;z++)
                c[i][j]=(c[i][j]+a[i][z]*b[z][j])%P;
    return c;
}
long long matrix_oracle(const vector<int>&init,const vector<int>&c,U n)
{
    int k=c.size();
    if(n<U(k)) return init[n];
    Matrix a(k,vector<long long>(k)),r=a;
    for(int i=0;i<k;i++)
    {
        a[0][i]=c[i];
        r[i][i]=1;
        if(i) a[i][i-1]=1;
    }
    for(U e=n-(k-1);e;e>>=1,a=multiply(a,a))
        if(e&1) r=multiply(r,a);
    long long v=0;
    for(int i=0;i<k;i++) v=(v+r[0][i]*init[k-1-i])%P;
    return v;
}
void recurrence_cases()
{
    using A=compact::BostanMori<>;
    using B=classic::Bostan_Mori<>;
    assert(A::recurrence({}, {}, ~U(0)).v==0);
    assert(B::Recurrence({}, {}, ~U(0)).v==0);
    mt19937 rng(8912);
    for(int t=0;t<150;t++)
    {
        int k=1+rng()%6;
        vector<int> init(k),c(k);
        for(int i=0;i<k;i++)
        {
            init[i]=rng()%P;
            c[i]=t%5 ? rng()%P : 0;
        }
        vector<U> ns={0,U(k-1),U(k),123,1ULL<<63,~U(0),~U(0)-1};
        for(U n:ns)
        {
            int want=matrix_oracle(init,c,n);
            assert(A::recurrence({init.begin(),init.end()},{c.begin(),c.end()},n).v==want);
            assert(B::Recurrence({init.begin(),init.end()},{c.begin(),c.end()},n).v==want);
        }
    }
}
void large_case()
{
    using A=compact::BostanMori<>;
    using B=classic::Bostan_Mori<>;
    const int k=32000;
    typename A::Poly init(k),c(k);
    typename B::Poly initial(k),coeff(k);
    long long bin=1,value=1;
    for(int i=0;i<k;i++)
    {
        init[i]=value;
        initial[i]=value;
        value=value*(k+i)%P*power(i+1,P-2,P)%P;
        bin=bin*(k-i)%P*power(i+1,P-2,P)%P;
        int v=i%2 ? (P-bin)%P : bin;
        c[i]=v;
        coeff[i]=v;
    }
    for(U n:{1000000000ULL,~U(0)})
    {
        long long want=1;
        for(int i=1;i<k;i++)
            want=want*((n%P+i)%P)%P*power(i,P-2,P)%P;
        assert(A::recurrence(init,c,n).v==want);
        assert(B::Recurrence(initial,coeff,n).v==want);
    }
}
int main()
{
    rational_cases<2,1>();
    rational_cases<3,2>();
    rational_cases<17>();
    rational_cases<97,5>();
    rational_cases<998244353>();
    rational_cases<167772161>();
    recurrence_cases();
    large_case();
    cout << "Bostan-Mori dual rational-series division, companion-matrix uint64 oracle and dense order-32000 binomial sequences PASS\n";
}
