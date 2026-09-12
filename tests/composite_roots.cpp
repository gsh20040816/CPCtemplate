#include "../src/classic/composite_roots.hpp"
#include "../src/compact/composite_roots.hpp"
#include "../src/compact/primitive_root.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B = boost::multiprecision::cpp_int;
using L = long long;
using U = unsigned long long;
using Factors = vector<tuple<L,int,L>>;
L power(L a,U k,L mod)
{
    B x=a,result=1%mod;
    while (k)
    {
        if (k&1) result=result*x%mod;
        x=x*x%mod;
        k>>=1;
    }
    return result.convert_to<L>();
}
Factors factor(int m)
{
    Factors f;
    for (int p=2;p<=m;p++)
        if (m%p==0)
        {
            int e=0,q=1;
            while (m%p==0)
            {
                m/=p;
                q*=p;
                e++;
            }
            f.push_back({p,e,p==2?0:PrimitiveRoot(q).minimum()});
        }
    return f;
}
void check(L a,U k,Factors f, bool exhaustive=true)
{
    L mod=1;
    for (auto [p,e,g]:f) for (int i=0;i<e;i++) mod*=p;
    L target=a%mod;
    if (target<0) target+=mod;
    vector<L> want;
    if (exhaustive)
        for (L v=0;v<mod;v++) if (power(v,k,mod)==target) want.push_back(v);
    for (int reverse_order=0;reverse_order<2;reverse_order++)
    {
        auto x=CompositeRoots::solve(a,k,f);
        auto y=Composite_Roots::Solve(a,k,f);
        assert(bool(x)==bool(y));
        if (!x)
            assert(exhaustive && want.empty());
        else
        {
            assert(x->mod==mod && y->mod==mod && x->total==y->total);
            if (exhaustive)
            {
                vector<L> got;
                for (L i=0;i<x->total;i++)
                {
                    L v=x->get(i);
                    assert(v==y->Get(i));
                    got.push_back(v);
                }
                sort(got.begin(),got.end());
                assert(got==want);
            }
            else
            {
                mt19937_64 rng(20260919);
                for (int t=0;t<300;t++)
                {
                    L i=rng()%x->total,v=x->get(i);
                    assert(v==y->Get(i) && 0<=v && v<mod && power(v,k,mod)==target);
                }
            }
        }
        reverse(f.begin(),f.end());
    }
}
int main()
{
    for (int m=1;m<=180;m++)
    {
        auto f=factor(m);
        for (U k=1;k<=8;k++)
            for (L a=0;a<m;a++) check(a,k,f);
        for (U k:{ULLONG_MAX,U(1)<<63})
            for (L a:{LLONG_MIN,LLONG_MAX,L(-1)}) check(a,k,f);
    }
    Factors big{{2,18,0},{3,10,2}};
    L m=(1LL<<18)*59049;
    check(power(84,6,m),6,big,false);
    check(0,ULLONG_MAX,big,false);
    auto zero=CompositeRoots::solve(0,ULLONG_MAX,big);
    assert(zero && zero->total==m/6);
    Factors many;
    for (int p:{2,3,5,7,11,13,17,19,23,29,31})
        many.push_back({p,1,p==2?0:PrimitiveRoot(p).minimum()});
    check(1,2,many,false);
    auto roots=CompositeRoots::solve(1,2,many);
    assert(roots && roots->total==1024);
    set<L> unique;
    for (L i=0;i<roots->total;i++)
    {
        L v=roots->get(i);
        assert(power(v,2,roots->mod)==1);
        unique.insert(v);
    }
    assert(unique.size()==1024);
    cout<<"Composite roots dual exhaustive CRT root sets, reordered factors, modulus one, signed/uint64 extremes and large mixed factors PASS\n";
}
