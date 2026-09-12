#include "../src/compact/number_theory.hpp"
#include "../src/classic/number_theory.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <cassert>
#include <iostream>
using boost::multiprecision::cpp_int;
using ll = long long;

cpp_int floor_div(cpp_int a, ll m)
{
    cpp_int q = a/m;
    if(a%m<0)
        q--;
    return q;
}

void check(ll n,ll m,ll a,ll b,cpp_int expected)
{
    assert(cpp_int(NumberTheory::floor_sum(n,m,a,b)) == expected);
    assert(cpp_int(Number_Theory::Floor_Sum(n,m,a,b)) == expected);
}

cpp_int direct(ll n,ll m,ll a,ll b)
{
    cpp_int answer=0;
    for(ll i=0;i<n;i++)
        answer+=floor_div(cpp_int(a)*i+b,m);
    return answer;
}

cpp_int consecutive(ll n,ll m,cpp_int b)
{
    cpp_int q=floor_div(b,m);
    ll r=(b-q*m).convert_to<ll>();
    ll full=(n+r)/m;
    ll tail=(n+r)%m;
    return q*n+cpp_int(m)*full*(full-1)/2+cpp_int(full)*tail;
}

int main()
{
    for(ll n=0;n<=10;n++)
        for(ll m=1;m<=12;m++)
            for(ll a=-15;a<=15;a++)
                for(ll b=-15;b<=15;b++)
                    check(n,m,a,b,direct(n,m,a,b));
    mt19937_64 rng(1000000000);
    for(int i=0;i<3000;i++)
    {
        ll n=rng()%51,m=1+rng()%1000000000;
        ll a=bit_cast<ll>(rng()),b=bit_cast<ll>(rng());
        check(n,m,a,b,direct(n,m,a,b));
    }
    for(ll n:{0LL,1LL,1000000000LL})
        for(ll m:{1LL,2LL,3LL,999999937LL,1000000000LL})
            for(ll b:{LLONG_MIN,-1LL,0LL,1LL,LLONG_MAX})
            {
                check(n,m,0,b,floor_div(cpp_int(b),m)*n);
                check(n,m,1,b,consecutive(n,m,cpp_int(b)));
                check(n,m,-1,b,consecutive(n,m,cpp_int(b)-n+1));
                for(ll k:{-1000000000LL,1000000000LL})
                    check(n,m,k*m,b,cpp_int(k)*n*(n-1)/2+floor_div(cpp_int(b),m)*n);
            }
    for(ll a:{LLONG_MIN,LLONG_MAX})
        for(ll b:{LLONG_MIN,LLONG_MAX})
            check(1000000000,1,a,b,cpp_int(a)*1000000000*999999999/2+cpp_int(b)*1000000000);
    cout << "Floor sum dual cpp_int signed oracle, zero terms, quotient boundaries and billion-term closed forms PASS\n";
}
