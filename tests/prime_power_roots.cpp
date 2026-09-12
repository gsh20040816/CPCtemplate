#include "../src/classic/prime_power_roots.hpp"
#include "../src/compact/prime_power_roots.hpp"
#include "../src/compact/primitive_root.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B = boost::multiprecision::cpp_int;
using L = long long;
using U = unsigned long long;
L power(L x,U k,L mod)
{
    B a=x,result=1;
    while (k)
    {
        if (k&1) result=result*a%mod;
        a=a*a%mod;
        k>>=1;
    }
    return result.convert_to<L>();
}
void check(L a,U k,L p,int e,L g,bool exhaustive=true)
{
    L mod=1;
    for (int i=0;i<e;i++) mod*=p;
    L target=a%mod;
    if (target<0) target+=mod;
    auto x=PrimePowerRoots::solve(a,k,p,e,g);
    auto y=Prime_Power_Roots::Solve(a,k,p,e,g);
    assert(bool(x)==bool(y));
    vector<L> want;
    if (exhaustive)
        for (L v=0;v<mod;v++) if (power(v,k,mod)==target) want.push_back(v);
    if (!x)
    {
        assert(exhaustive && want.empty());
        return;
    }
    assert(x->first==y->first && x->step==y->step && x->lifts==y->lifts);
    assert(x->ratio==y->ratio && x->count==y->count && x->size()==y->Size());
    assert(x->step*x->lifts==mod && x->size()<=mod);
    if (exhaustive)
    {
        vector<L> got;
        for (L i=0;i<x->count[0];i++)
            for (L j=0;j<x->count[1];j++)
                for (L z=0;z<x->lifts;z++)
                {
                    L v=x->get(i,j,z);
                    assert(v==y->Get(i,j,z));
                    got.push_back(v);
                }
        sort(got.begin(),got.end());
        assert(got==want);
    }
    else
    {
        mt19937_64 rng(20260918);
        for (int t=0;t<100;t++)
        {
            L i=rng()%x->count[0],j=rng()%x->count[1],z=rng()%x->lifts;
            L v=x->get(i,j,z);
            assert(v==y->Get(i,j,z) && 0<=v && v<mod);
            assert(power(v,k,mod)==target);
        }
    }
}
int main()
{
    for (int p:{2,3,5,7,11,13})
    {
        int mod=1;
        for (int e=1;mod<=256/p;e++)
        {
            mod*=p;
            L g=p==2?0:PrimitiveRoot(mod).minimum();
            for (U k=1;k<=12;k++)
                for (L a=-mod;a<=mod;a++) check(a,k,p,e,g);
            for (U k:{ULLONG_MAX,U(1)<<63})
                for (L a:{LLONG_MIN,LLONG_MAX,L(0),L(1),L(-1)}) check(a,k,p,e,g);
        }
    }
    check(power(1234567,3,1LL<<39),3,2,39,0,false);
    check(1,2,2,39,0,false);
    auto four=PrimePowerRoots::solve(1,2,2,39);
    assert(four && four->size()==4);
    check(0,ULLONG_MAX,2,39,0,false);
    auto zero=PrimePowerRoots::solve(0,ULLONG_MAX,2,39);
    assert(zero && zero->step==2 && zero->size()==(1LL<<38));
    check(1,1ULL<<38,2,39,0,false);
    auto units=PrimePowerRoots::solve(1,1ULL<<38,2,39);
    assert(units && units->size()==(1LL<<38));
    L mod=1;
    for (int i=0;i<20;i++) mod*=3;
    // 2 is a primitive root modulo 3^20: certify both prime factors of phi.
    L phi=mod/3*2;
    assert(power(2,phi,mod)==1 && power(2,phi/2,mod)!=1 && power(2,phi/3,mod)!=1);
    check(power(81*7,3,mod),3,3,20,2,false);
    check(0,7,3,20,2,false);
    cout<<"Prime-power roots dual exhaustive nonunit/unit root sets, 2-adic sign group, uint64 exponents and compressed large lifts PASS\n";
}
