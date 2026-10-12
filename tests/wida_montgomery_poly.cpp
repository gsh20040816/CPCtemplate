#include <bits/stdc++.h>
#include <cassert>
namespace source
{
#include "fixtures/wida_montgomery_poly/12C.cpp"
}
#include "../src/compact/fps_functions.hpp"
#include "../src/compact/fps_sqrt.hpp"
#include "../src/compact/fps_power.hpp"
#include "../src/compact/polynomial_division.hpp"
using namespace std;
constexpr int p = 998244353;
using A = vector<long long>;
using O = source::MontgomeryModInt32<p>;
using OP = vector<O>;
using F = FpsFunctions;
long long checks = 0;
void require(bool x)
{
    if (!x)
        throw runtime_error("12C source audit mismatch at " + to_string(checks));
    checks++;
}
long long power(long long a, int k)
{
    long long r = 1;
    while (k)
    {
        if (k & 1)
            r = r * a % p;
        a = a * a % p;
        k >>= 1;
    }
    return r;
}
A multiply(const A &a,const A &b,int n)
{
    A r(n);
    for (int i = 0; i < (int)a.size(); i++)
        for (int j = 0; j < (int)b.size() && i+j<n; j++)
            r[i+j] = (r[i+j]+a[i]*b[j])%p;
    return r;
}
A inverse(const A &a)
{
    A r(a.size());
    r[0] = power(a[0],p-2);
    for (int i = 1; i < (int)a.size(); i++)
    {
        long long sum = 0;
        for (int j = 1; j <= i; j++)
            sum = (sum+a[j]*r[i-j])%p;
        r[i] = (p-sum)*r[0]%p;
    }
    return r;
}
OP old(const A &a)
{
    OP r;
    for (auto x : a)
        r.emplace_back(x);
    return r;
}
F::Poly current(const A &a)
{
    F::Poly r;
    for (auto x : a)
        r.emplace_back(x);
    return r;
}
A values(const OP &a)
{
    A r;
    for (auto x : a)
        r.push_back(x.get());
    return r;
}
A values(const F::Poly &a)
{
    A r;
    for (auto x : a)
        r.push_back(x.v);
    return r;
}
map<string,pair<int,int>> source_counts;
void source_equal(const A &got, const A &expected, const string &name)
{
    auto &[total,bad] = source_counts[name];
    total++;
    if (got != expected)
    {
        if (bad == 0)
        {
            cout << name << " first mismatch got";
            for (auto x : got)
                cout << ' ' << x;
            cout << " expected";
            for (auto x : expected)
                cout << ' ' << x;
            cout << '\n';
        }
        bad++;
    }
}
void trim(A &a)
{
    while (!a.empty() && a.back()==0)
        a.pop_back();
}
int main(int argc, char **argv)
{
    if (argc > 1)
    {
        OP a{O(1),O(2)};
        auto first = values(source::sqrt(a));
        auto second = values(source::sqrt(a));
        auto inv_first = values(source::sqrtinv(a));
        auto inv_second = values(source::sqrtinv(a));
        for (const auto &r : {first,second,inv_first,inv_second})
        {
            for (auto x : r)
                cout << x << ' ';
            cout << '\n';
        }
        require(first == A({1,1}));
        require(second != first);
        require(inv_first == A({1,p-1}));
        require(inv_second != inv_first);
        for (int i=0;i<4;i++)
        {
            auto root = FpsSqrt::sqrt(F::Poly{1,2},2);
            require(root && values(*root)==A({1,1}));
            require(values(F::inverse(*root,2))==A({1,p-1}));
        }
        cout << "Repeated source calls differ; replacement calls stable\n";
        return 0;
    }
    mt19937 rng(12);
    for (int n : {1,2,3,7,8,9,16,31,32,33,63,64,65,100,127,128})
    {
        for (int repeat = 0; repeat < 5; repeat++)
        {
            A a(n),b(n);
            for (auto &x:a)
                x=rng()%p;
            for (auto &x:b)
                x=rng()%p;
            a[0]=1;
            b[0]=1;
            b.back()=1;
            auto x=old(a),y=old(b);
            auto cx=current(a),cy=current(b);
            A sum(n),dif(n);
            for (int i=0;i<n;i++)
            {
                sum[i]=(a[i]+b[i])%p;
                dif[i]=(a[i]+p-b[i])%p;
            }
            source_equal(values(source::add(x,y)),sum,"add");
            source_equal(values(source::sub(x,y)),dif,"sub");
            auto product=multiply(a,b,2*n-1);
            source_equal(values(source::mul(x,y)),product,"mul");
            require(values(F::multiply(cx,cy))==product);
            auto iv=inverse(a);
            source_equal(values(source::inv(x)),iv,"inv");
            require(values(F::inverse(cx,n))==iv);
            auto q=multiply(a,inverse(b),n);
            source_equal(values(source::quo(x,y)),q,"quo");
            auto ourq=values(F::multiply(cx,F::inverse(cy,n)));
            ourq.resize(n);
            require(ourq==q);
            A deriv(max(0,n-1)),integr(n+1);
            for (int i=1;i<n;i++)
                deriv[i-1]=a[i]*i%p;
            for (int i=0;i<n;i++)
                integr[i+1]=a[i]*power(i+1,p-2)%p;
            auto od=values(source::deriv(x));
            if (n==1)
                od.clear();
            source_equal(od,deriv,"deriv");
            require(values(F::derivative(cx))==deriv);
            source_equal(values(source::integr(x)),integr,"integr");
            require(values(F::integral(cx))==integr);
            auto lg=multiply(deriv,iv,n-1);
            lg.insert(lg.begin(),0);
            for (int i=1;i<n;i++)
                lg[i]=lg[i]*power(i,p-2)%p;
            source_equal(values(source::log(x)),lg,"log");
            require(values(F::log(cx,n))==lg);
            auto ef=a;
            ef[0]=0;
            A exponential(n);
            exponential[0]=1;
            for (int i=1;i<n;i++)
            {
                long long s=0;
                for (int j=1;j<=i;j++)
                    s=(s+ef[j]*j%p*exponential[i-j])%p;
                exponential[i]=s*power(i,p-2)%p;
            }
            source_equal(values(source::exp(old(ef))),exponential,"exp");
            require(values(F::exp(current(ef),n))==exponential);
            for (int k : {0,1,2,5})
            {
                A expected(n);
                expected[0]=1;
                for (int j=0;j<k;j++)
                    expected=multiply(expected,a,n);
                source_equal(values(source::pow(x,O(k))),expected,"pow-unit");
                require(values(FpsPower::power(cx,to_string(k),n))==expected);
            }
            auto sq=multiply(a,a,n);
            auto source_root = values(source::sqrt(old(sq)));
            source_equal(source_root,a,"sqrt");
            auto root=FpsSqrt::sqrt(current(sq),n);
            require(root && values(*root)==a);
            source_equal(values(source::sqrtinv(old(sq))),iv,"sqrtinv");
            require(values(F::inverse(*root,n))==iv);
            // Form an exact quotient and independent low-degree remainder.
            auto dividend=product;
            A remainder(max(0,n-1));
            for (int i=0;i<n-1;i++)
            {
                remainder[i]=rng()%p;
                dividend[i]=(dividend[i]+remainder[i])%p;
            }
            auto [oq,orr]=source::quo_with_rem(old(dividend),y);
            auto [nq,nr]=PolynomialDivision::divide(current(dividend),cy);
            auto ov=values(orr),nv=values(nr);
            trim(ov);
            trim(nv);
            trim(remainder);
            source_equal(values(oq),a,"division-quotient");
            require(values(nq)==a);
            source_equal(ov,remainder,"division-remainder");
            require(nv==remainder);
        }
    }
    // pow uses exp(k*log(x)) and assumes unit constant term.
    require(values(source::pow(OP{O(2)},O(2)))==A{1});
    require(values(FpsPower::power(F::Poly{2},"2",1))==A{4});
    for (const auto &[name,count] : source_counts)
        cout << name << " total " << count.first << " mismatches " << count.second << '\n';
    cout << checks << " replacement independent naive FPS checks PASS\n";
}
