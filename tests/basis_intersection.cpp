#include "../src/compact/basis_intersection.hpp"
#include "../src/classic/basis_intersection.hpp"
#include <iostream>
#include <random>
#include <set>
using U = unsigned long long;

set<U> enumerate_span(const vector<U> &v)
{
    set<U> s{0};
    for (U x : v)
    {
        auto old = s;
        for (U y : old)
            s.insert(x^y);
    }
    return s;
}

void check(const vector<U> &va, const vector<U> &vb)
{
    XorBasis a,b;
    Xor_Basis ca,cb;
    for (U x : va)
    {
        a.insert(x);
        ca.Insert(x);
    }
    for (U x : vb)
    {
        b.insert(x);
        cb.Insert(x);
    }
    auto sa = enumerate_span(va), sb = enumerate_span(vb);
    set<U> si, su;
    for (U x : sa)
    {
        if (sb.count(x))
            si.insert(x);
        for (U y : sb)
            su.insert(x^y);
    }
    auto c = basis_intersection(a,b);
    auto reverse_c = basis_intersection(b,a);
    auto cc = Basis_Intersection(ca,cb);
    auto [sum, both] = basis_sum_intersection(a,b);
    auto [csum, cboth] = Basis_Sum_Intersection(ca,cb);
    assert(!c.dependent && !cc.dependent && !sum.dependent && !both.dependent);
    assert(!csum.dependent && !cboth.dependent);
    assert((1ULL<<c.rank) == si.size());
    assert((1ULL<<sum.rank) == su.size());
    assert(c.rank == cc.rank && c.rank == both.rank && c.rank == cboth.rank);
    assert(a.rank+b.rank == sum.rank+c.rank);
    assert(csum.rank == sum.rank);
    for (U x : su)
    {
        bool want = si.count(x);
        assert(c.contains(x) == want && cc.Contains(x) == want);
        assert(reverse_c.contains(x) == want);
        assert(both.contains(x) == want && cboth.Contains(x) == want);
        assert(sum.contains(x) && csum.Contains(x));
    }
    unsigned k = 1;
    for (U x : si)
    {
        assert(c.kth(k,false) == x && cc.Kth(k,false) == x);
        k++;
    }
    assert(!c.kth(k,false) && !cc.Kth(k,false));
    for (U x : {0ULL,1ULL,1ULL<<63,~0ULL})
    {
        assert(c.contains(x) == bool(si.count(x)));
        assert(sum.contains(x) == bool(su.count(x)));
    }
}

int main()
{
    // All pairs of generator subsets over F2^3, including zero and dependencies.
    for (int a = 0; a < 256; a++)
        for (int b = 0; b < 256; b++)
        {
            vector<U> va,vb;
            for (int i = 0; i < 8; i++)
            {
                if (a>>i&1)
                    va.push_back(i);
                if (b>>i&1)
                    vb.push_back(i);
            }
            check(va,vb);
        }
    mt19937_64 rng(20260912);
    for (int trial = 0; trial < 500; trial++)
    {
        U shared = rng();
        check({shared,rng(),rng(),0},{shared,rng(),rng(),shared});
    }
    XorBasis full, even, odd;
    Xor_Basis cfull, ceven, codd;
    for (int i = 0; i < 64; i++)
    {
        U x = 1ULL<<i;
        full.insert(x);
        cfull.Insert(x);
        if (i%2)
        {
            odd.insert(x);
            codd.Insert(x);
        }
        else
        {
            even.insert(x);
            ceven.Insert(x);
        }
    }
    assert(basis_intersection(even,odd).rank == 0);
    assert(Basis_Intersection(ceven,codd).rank == 0);
    auto [s,t] = basis_sum_intersection(even,odd);
    auto [cs,ct] = Basis_Sum_Intersection(ceven,codd);
    assert(s.rank == 64 && cs.rank == 64 && t.rank == 0 && ct.rank == 0);
    auto same = basis_intersection(full,full);
    auto csame = Basis_Intersection(cfull,cfull);
    auto [all,both] = basis_sum_intersection(full,full);
    auto [call,cboth] = Basis_Sum_Intersection(cfull,cfull);
    assert(same.rank == 64 && csame.rank == 64);
    assert(all.rank == 64 && both.rank == 64 && call.rank == 64 && cboth.rank == 64);
    assert(same.kth(__uint128_t(1)<<64,false) == ~0ULL);
    assert(csame.Kth(__uint128_t(1)<<64,false) == ~0ULL);
    assert(!same.dependent && !both.dependent && !all.dependent);
    for (int i = 0; i < 10000; i++)
    {
        U x = rng();
        assert(both.contains(x) && cboth.Contains(x));
    }
    cout << "Basis intersection dual exhaustive subspaces, Zassenhaus sum, generators and 64-bit boundaries PASS\n";
}
