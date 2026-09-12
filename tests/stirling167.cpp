#include <bits/stdc++.h>
#include <cassert>
namespace classic {
#include "../src/classic/stirling.hpp"
}
namespace compact {
#include "../src/compact/stirling.hpp"
}
using namespace std;
using Z=compact::ModInt<167772161>;
const int P=167772161;
void second(unsigned long long n,int m,const vector<int>&want)
{
    auto a=compact::stirling_second_row<167772161>(n,m);
    auto b=classic::Stirling_Second_Row<167772161>(n,m);
    assert(a.size()==want.size() && b.size()==want.size());
    for(int i=0;i<=m;i++) assert(a[i].v==want[i] && a[i].v==b[i].v);
}
void first(int n,const vector<int>&want)
{
    auto a=compact::stirling_first_row<167772161>(n);
    auto b=classic::Stirling_First_Row<167772161>(n);
    assert(a.size()==want.size() && b.size()==want.size());
    for(int i=0;i<=n;i++) assert(a[i].v==want[i] && a[i].v==b[i].v);
}
vector<int> matrix_row(unsigned long long n,int m)
{
    using Mat=vector<vector<long long>>;
    auto mul=[&](const Mat&a,const Mat&b)
    {
        Mat c(m+1,vector<long long>(m+1));
        for(int i=0;i<=m;i++) for(int k=0;k<=m;k++) for(int j=0;j<=m;j++)
            c[i][j]=(c[i][j]+a[i][k]*b[k][j])%P;
        return c;
    };
    Mat a(m+1,vector<long long>(m+1)),r=a;
    for(int i=0;i<=m;i++)
    {
        a[i][i]=i;
        r[i][i]=1;
        if(i) a[i][i-1]=1;
    }
    while(n)
    {
        if(n&1) r=mul(r,a);
        a=mul(a,a);
        n>>=1;
    }
    vector<int> result(m+1);
    for(int i=0;i<=m;i++) result[i]=r[i][0];
    return result;
}
template<int mod,int primitive>
void small_modulus()
{
    vector<int> want{1};
    const int limit=compact::NttConvolution<mod,primitive>::max_size;
    for(int n=0;n<limit;n++)
    {
        auto a=compact::stirling_first_row<mod,primitive>(n);
        auto b=classic::Stirling_First_Row<mod,primitive>(n);
        assert(a.size()==want.size() && b.size()==want.size());
        for(int i=0;i<=n;i++)
            assert(a[i].v==want[i] && b[i].v==want[i]);
        vector<int> next(n+2);
        for(int i=0;i<=n;i++)
        {
            next[i]=(next[i]+want[i]*n)%mod;
            next[i+1]=(next[i+1]+want[i])%mod;
        }
        want=next;
    }
}
int main()
{
    small_modulus<2,1>();
    small_modulus<3,2>();
    small_modulus<17,3>();
    small_modulus<97,5>();
    for(int n=0;n<=9;n++)
    {
        vector<int> blocks(n+1),cycles(n+1),p(n);
        function<void(int,int)> enumerate=[&](int i,int k)
        {
            if(i==n)
            {
                blocks[k]++;
                return;
            }
            for(int label=0;label<=k;label++) enumerate(i+1,k+(label==k));
        };
        enumerate(0,0);
        iota(p.begin(),p.end(),0);
        do
        {
            vector<bool> seen(n);
            int k=0;
            for(int i=0;i<n;i++) if(!seen[i])
            {
                k++;
                for(int v=i;!seen[v];v=p[v]) seen[v]=true;
            }
            cycles[k]++;
        }while(next_permutation(p.begin(),p.end()));
        first(n,cycles);
        second(n,n,blocks);
    }
    vector<int> a{1},b{1};
    for(int n=0;n<=300;n++)
    {
        first(n,a);
        auto extra=b;
        extra.resize(n+8);
        second(n,n+7,extra);
        vector<int> x(n+2),y(n+2);
        for(int k=1;k<=n+1;k++)
        {
            x[k]=(a[k-1]+(k<=n?1LL*n*a[k]:0))%P;
            y[k]=(b[k-1]+(k<=n?1LL*k*b[k]:0))%P;
        }
        a=x;
        b=y;
    }
    for(auto n:{0ULL,1ULL,167772161ULL,1ULL<<63,ULLONG_MAX}) second(n,7,matrix_row(n,7));
    int n=200000;
    auto row=compact::stirling_second_row<167772161>(n,n);
    auto old=classic::Stirling_Second_Row<167772161>(n,n);
    for(int i=0;i<=n;i++) assert(row[i].v==old[i].v);
    assert(row[0].v==0 && row[n].v==1 && row[1].v==1);
    assert(row[n-1].v==int(1LL*n*(n-1)/2%P));
    for(Z x:{Z(5),Z(123456789),Z(P-1)})
    {
        Z sum=0,falling=1;
        for(int k=0;k<=n;k++)
        {
            sum=sum+row[k]*falling;
            falling=falling*(x-k);
        }
        assert(sum.v==x.pow(n).v);
    }
    n=262143;
    auto c=compact::stirling_first_row<167772161>(n);
    auto d=classic::Stirling_First_Row<167772161>(n);
    for(int i=0;i<=n;i++) assert(c[i].v==d[i].v);
    for(Z x:{Z(0),Z(1),Z(7),Z(987654321)})
    {
        Z value=0,want=1;
        for(int i=n;i>=0;i--) value=value*x+c[i];
        for(int i=0;i<n;i++) want=want*(x+i);
        assert(value.v==want.v);
    }
    cout<<"Stirling 167772161 rows dual partition/permutation enumeration, DP and uint64 matrix oracles, 200000 second-kind and 262143 first-kind identities PASS\n";
}
