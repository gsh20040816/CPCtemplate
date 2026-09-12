#include "../src/compact/floor_moments.hpp"
#include "../src/classic/floor_moments.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
using boost::multiprecision::cpp_int;
using ll = long long;

int residue(cpp_int x)
{
    x%=998244353;
    if(x<0)
        x+=998244353;
    return x.convert_to<int>();
}

void check(ll n,ll m,ll a,ll b,array<cpp_int,3> expected)
{
    auto x=floor_moments(n,m,a,b);
    auto y=Floor_Moments(n,m,a,b);
    for(int i=0;i<3;i++)
    {
        assert(x[i].v==residue(expected[i]));
        assert(y[i].v==residue(expected[i]));
    }
}

void direct(ll n,ll m,ll a,ll b)
{
    array<cpp_int,3> sum{};
    for(ll i=0;i<n;i++)
    {
        cpp_int value=cpp_int(a)*i+b;
        cpp_int q=value/m;
        if(value%m<0)
            q--;
        sum[0]+=q;
        sum[1]+=i*q;
        sum[2]+=q*q;
    }
    check(n,m,a,b,sum);
}

int main()
{
    for(ll n=0;n<=12;n++)
        for(ll m=1;m<=12;m++)
            for(ll a=-12;a<=12;a++)
                for(ll b=-12;b<=12;b++)
                    direct(n,m,a,b);
    mt19937_64 rng(5170);
    for(int i=0;i<2000;i++)
        direct(rng()%40,1+rng()%1000000000,bit_cast<ll>(rng()),bit_cast<ll>(rng()));
    for(ll n:{0LL,1LL,1000000000LL,1000000001LL})
        for(ll a:{LLONG_MIN,-1LL,0LL,1LL,LLONG_MAX})
            for(ll b:{LLONG_MIN,-1LL,0LL,1LL,LLONG_MAX})
            {
                cpp_int s1=cpp_int(n)*(n-1)/2;
                cpp_int s2=cpp_int(n)*(n-1)*(2*n-1)/6;
                check(n,1,a,b,{cpp_int(a)*s1+cpp_int(b)*n,
                              cpp_int(a)*s2+cpp_int(b)*s1,
                              cpp_int(a)*a*s2+2*cpp_int(a)*b*s1+cpp_int(b)*b*n});
            }
    cout << "Floor moments dual cpp_int weighted/squared oracle, signed extremes, zero terms and billion-term polynomial certificates PASS\n";
}
