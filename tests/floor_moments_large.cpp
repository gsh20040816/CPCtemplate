#include "../src/compact/floor_moments.hpp"
#include "../src/classic/floor_moments.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
using boost::multiprecision::cpp_int;
using ll = long long;
using Z = ModInt<998244353>;

Z modular(cpp_int x)
{
    x%=998244353;
    return Z(x.convert_to<ll>());
}

array<Z,3> query(ll n,ll m,ll a,ll b)
{
    auto result=floor_moments(n,m,a,b);
    auto classic=Floor_Moments(n,m,a,b);
    for(int i=0;i<3;i++)
        assert(result[i].v==classic[i].v);
    if(n<=1000000000)
        assert(result[0].v==modular(cpp_int(NumberTheory::floor_sum(n,m,a,b))).v);
    return result;
}

void check(ll n,ll m,ll a,ll b)
{
    auto x=query(n,m,a,b);
    auto next=query(n+1,m,a,b);
    cpp_int numerator=cpp_int(a)*n+b;
    cpp_int exact=numerator/m;
    if(numerator%m<0)
        exact--;
    Z y=modular(exact);
    assert((next[0]-x[0]).v==y.v);
    assert((next[1]-x[1]).v==(Z(n)*y).v);
    assert((next[2]-x[2]).v==(y*y).v);
    cpp_int reverse_b=cpp_int(a)*(n-1)+b;
    if(reverse_b>=LLONG_MIN && reverse_b<=LLONG_MAX && a!=LLONG_MIN)
    {
        auto r=query(n,m,-a,reverse_b.convert_to<ll>());
        assert(r[0].v==x[0].v && r[2].v==x[2].v);
        assert(r[1].v==(Z(n-1)*x[0]-x[1]).v);
    }
    if(a!=LLONG_MIN)
    {
        // floor(z) + floor(-z - 1/m) = -1 for integer numerator z*m.
        auto c=query(n,m,-a,-1-b);
        Z s1=Z(n)*Z(n-1)*Z(499122177);
        assert((c[0]+x[0]+Z(n)).v==0);
        assert((c[1]+x[1]+s1).v==0);
        assert(c[2].v==(x[2]+Z(2)*x[0]+Z(n)).v);
    }
}

int main()
{
    mt19937_64 rng(517000);
    for(int i=0;i<3000;i++)
    {
        ll n=1+rng()%1000000000;
        ll m=1+rng()%1000000000;
        ll a=ll(rng()%2000000001)-1000000000;
        ll b=ll(rng()%2000000001)-1000000000;
        check(n,m,a,b);
    }
    for(ll a:{LLONG_MIN,LLONG_MAX})
        for(ll b:{LLONG_MIN,LLONG_MAX})
            check(1000000000,999999937,a,b);
    ll a=1,m=2;
    while(m<=1000000000)
    {
        check(1000000000,m,a,m-1);
        ll next=a+m;
        a=m;
        m=next;
    }
    cout << "Floor moments large dual reversal/complement/difference identities, scalar floor-sum cross-check and Fibonacci depth PASS\n";
}
