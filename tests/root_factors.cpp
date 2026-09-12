#include "../src/classic/composite_roots.hpp"
#include "../src/compact/composite_roots.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using L=long long;
using B=boost::multiprecision::cpp_int;
L power(L a,unsigned long long k,L m)
{
    B x=a,y=1%m;
    while(k)
    {
        if(k&1) y=y*x%m;
        x=x*x%m;
        k>>=1;
    }
    return y.convert_to<L>();
}
vector<L> trial(L n)
{
    vector<L> f;
    for(L d=2;d<=n/d;d++)
        while(n%d==0)
        {
            f.push_back(d);
            n/=d;
        }
    if(n>1) f.push_back(n);
    return f;
}
void certify(L mod)
{
    PollardRho rho(1);
    Pollard_Rho old(2);
    auto a=root_factors(mod,rho);
    auto b=Root_Factors(mod,old);
    assert(a==b);
    vector<L> flat;
    L product=1;
    for(auto [p,e,g]:a)
    {
        L m=1;
        for(int i=0;i<e;i++)
        {
            m*=p;
            flat.push_back(p);
        }
        product*=m;
        if(p==2) assert(g==0);
        else
        {
            assert(gcd(g,m)==1);
            L phi=m/p*(p-1);
            assert(power(g,phi,m)==1);
            for(L d:trial(phi)) assert(power(g,phi/d,m)!=1);
            if(m<300)
                for(L h=1;h<g;h++)
                {
                    set<L> values;
                    L x=1;
                    for(L i=0;i<phi;i++)
                    {
                        values.insert(x);
                        x=x*h%m;
                    }
                    assert((L)values.size()!=phi);
                }
        }
    }
    assert(product==mod && flat==trial(mod));
}
int main()
{
    for(int m=1;m<=500;m++) certify(m);
    for(L m:{999999999989LL,1000000000000LL,999983LL*999979LL,(1LL<<39),3486784401LL}) certify(m);
    PollardRho rho(3);
    Pollard_Rho old(4);
    for(int m=1;m<=80;m++)
        for(unsigned long long k=1;k<=8;k++)
            for(L a=0;a<m;a++)
            {
                vector<L> want,got;
                for(L x=0;x<m;x++) if(power(x,k,m)==a) want.push_back(x);
                auto x=CompositeRoots::solve(a,k,m,rho);
                auto y=Composite_Roots::Solve(a,k,m,old);
                assert(bool(x)==bool(y));
                if(!x) assert(want.empty());
                else
                {
                    assert(x->total==y->total);
                    for(L i=0;i<x->total;i++)
                    {
                        L v=x->get(i);
                        assert(v==y->Get(i));
                        got.push_back(v);
                    }
                    sort(got.begin(),got.end());
                    assert(got==want);
                }
            }
    cout<<"Root preparation dual trial factorization, primitive-order certificates, trillion bounds and end-to-end composite root sets PASS\n";
}
