#include "../src/classic/ntt_convolution.hpp"
#include "../src/compact/ntt_convolution.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B=boost::multiprecision::cpp_int;
long long power(long long a,long long k,int mod)
{
    B x=a,y=1;
    while(k)
    {
        if(k&1) y=y*x%mod;
        x=x*x%mod;
        k>>=1;
    }
    return y.convert_to<long long>();
}
template<int P,int G> void run()
{
    using N=NttConvolution<P,G>;
    using C=Ntt_Convolution<P,G>;
    for(int d=2;d<=P/d;d++) assert(P%d);
    int phi=P-1;
    for(int d=2;d<=phi/d;d++)
        if(phi%d==0)
        {
            assert(power(G,(P-1)/d,P)!=1);
            while(phi%d==0) phi/=d;
        }
    if(phi>1) assert(power(G,(P-1)/phi,P)!=1);
    mt19937 rng(P);
    for(int n=1;n<=min(N::max_size,32);n*=2)
    {
        typename N::Poly a(n);
        typename C::Poly b(n);
        for(int i=0;i<n;i++)
        {
            int value=rng()%P;
            a[i]=value;
            b[i]=value;
        }
        auto original=a;
        vector<int> want(n);
        long long w=power(G,(P-1)/n,P);
        for(int i=0;i<n;i++)
        {
            B sum=0;
            for(int j=0;j<n;j++) sum+=B(a[j].v)*power(w,i*j,P);
            want[i]=(sum%P).convert_to<int>();
        }
        N::ntt(a);
        C::Ntt(b);
        for(int i=0;i<n;i++) assert(a[i].v==want[i] && a[i].v==b[i].v);
        N::ntt(a,true);
        C::Ntt(b,true);
        for(int i=0;i<n;i++) assert(a[i].v==original[i].v && b[i].v==a[i].v);
    }
    for(int t=0;t<150;t++)
    {
        int n=rng()%(min(N::max_size,20)+1);
        int m=rng()%(min(N::max_size-n+1,20)+1);
        typename N::Poly a(n),b(m);
        typename C::Poly c(n),d(m);
        for(int i=0;i<n;i++)
        {
            int value=rng()%P;
            a[i]=value;
            c[i]=value;
        }
        for(int i=0;i<m;i++)
        {
            int value=rng()%P;
            b[i]=value;
            d[i]=value;
        }
        vector<B> want(n && m?n+m-1:0);
        for(int i=0;i<n;i++) for(int j=0;j<m;j++) want[i+j]+=B(a[i].v)*b[j].v;
        auto x=N::multiply(a,b);
        auto y=C::Multiply(c,d);
        assert(x.size()==want.size() && y.size()==want.size());
        for(int i=0;i<(int)x.size();i++) assert(x[i].v==(want[i]%P).template convert_to<int>() && x[i].v==y[i].v);
    }
    if constexpr(N::max_size >= (1<<18))
    {
        int n=131073,m=131071;
        auto x=N::multiply(typename N::Poly(n,1),typename N::Poly(m,1));
        auto y=C::Multiply(typename C::Poly(n,1),typename C::Poly(m,1));
        for(int i=0;i<n+m-1;i++)
        {
            int want=min({i+1,n,m,n+m-1-i})%P;
            assert(x[i].v==want && y[i].v==want);
        }
    }
}
int main()
{
    run<2,1>();
    run<3,2>();
    run<17,3>();
    run<97,5>();
    run<998244353,3>();
    run<167772161,3>();
    run<2013265921,31>();
    cout<<"Parameterized NTT dual cpp_int DFT/convolution oracles, certified primitive roots, capacity boundaries and large triangular convolutions PASS\n";
}
