#include "../src/compact/number_theory.hpp"
#include "../src/classic/number_theory.hpp"
#include <iostream>

template <int p> void check()
{
    Binomial<p> a;
    Combination<p> b;
    vector<vector<int>> pascal(p, vector<int>(p));
    pascal[0][0] = 1;
    for (int n = 1; n < p; n++)
        for (int k = 0; k <= n; k++)
            pascal[n][k] = ((k ? pascal[n-1][k-1] : 0) + pascal[n-1][k]) % p;
    for (int limit = 0; limit < p; limit++)
    {
        a.init(limit);
        b.Init(limit);
        a.init(limit / 2);
        b.Init(limit / 2);
        assert((int)a.fac.size() == limit + 1);
        assert((int)b.fac.size() == limit + 1);
        for (int n = 0; n <= limit; n++)
        {
            int falling = 1;
            for (int k = 0; k <= n; k++)
            {
                assert(a.choose(n,k).v == pascal[n][k]);
                assert(b.Choose(n,k).v == pascal[n][k]);
                assert(a.permute(n,k).v == falling);
                assert(b.Permute(n,k).v == falling);
                falling = 1LL * falling * (n-k) % p;
            }
            assert((a.fac[n] * a.ifac[n]).v == 1);
            assert((b.fac[n] * b.ifac[n]).v == 1);
            assert(a.choose(n,-1).v == 0 && b.Choose(n,n+1).v == 0);
            assert(a.permute(n,n+1).v == 0 && b.Permute(n,-1).v == 0);
        }
    }
    assert(a.choose(-1,0).v == 0 && b.Choose(-1,0).v == 0);
    assert(a.permute(-1,0).v == 0 && b.Permute(-1,0).v == 0);
    Binomial<p> direct(p-1);
    Combination<p> direct_b(p-1);
    for (int i = 0; i < p; i++)
    {
        assert(direct.fac[i].v == a.fac[i].v);
        assert(direct_b.ifac[i].v == b.ifac[i].v);
    }
}

int main()
{
    check<2>();
    check<3>();
    check<7>();
    check<101>();
    Binomial<1000000007> a(1000);
    Combination<1000000007> b(1000);
    a.init(1000000);
    b.Init(1000000);
    long long factorial = 1;
    for (int n = 0; n <= 1000000; n++)
    {
        if (n)
            factorial = factorial * n % 1000000007;
        assert(a.fac[n].v == factorial && b.fac[n].v == factorial);
        assert((a.fac[n] * a.ifac[n]).v == 1);
        assert((b.fac[n] * b.ifac[n]).v == 1);
        assert(a.permute(n,n).v == factorial && b.Permute(n,n).v == factorial);
        assert(a.choose(n,1).v == n && b.Choose(n,1).v == n);
    }
    cout << "Binomial dual Pascal/falling-factorial oracle, incremental growth, no-shrink reuse, boundaries and million-entry tables PASS\n";
}
