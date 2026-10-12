#include <bits/stdc++.h>
#include <cassert>
namespace original
{
#include "fixtures/wida_montgomery_poly/12C.cpp"
}
#include "../src/compact/fps_sqrt.hpp"
using namespace std;
int main(int argc,char **argv)
{
    int n=stoi(argv[1]);
    vector<int> result(n);
    auto start=chrono::steady_clock::now();
    if (string(argv[2])=="original")
    {
        using Z=original::MontgomeryModInt32<998244353>;
        vector<Z> a(n);
        for (int i=0;i<n;i++)
            a[i]=Z(i+1);
        auto r=original::sqrtinv(a);
        for (int i=0;i<n;i++)
            result[i]=r[i].get();
    }
    else
    {
        FpsSqrt::Poly a(n);
        for (int i=0;i<n;i++)
            a[i]=i+1;
        auto root=FpsSqrt::sqrt(a,n);
        if (!root)
            return 1;
        auto r=FpsInverse::inverse(*root,n);
        for (int i=0;i<n;i++)
            result[i]=r[i].v;
    }
    double seconds=chrono::duration<double>(chrono::steady_clock::now()-start).count();
    for (int i=0;i<n;i++)
    {
        int expected=i==0?1:(i==1?998244352:0);
        if (result[i]!=expected)
            return 2;
    }
    cout << seconds << '\n';
}
