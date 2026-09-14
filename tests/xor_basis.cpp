#include "../src/compact/data_structure.hpp"
#include "../src/classic/data_structure.hpp"
#include <iostream>
#include <random>
#include <set>
using U = unsigned long long;
using W = __uint128_t;

void verify(XorBasis &a, Xor_Basis &b, const vector<U> &values)
{
    set<U> all{0}, nonempty;
    for (unsigned mask = 1; mask < (1u << values.size()); mask++)
    {
        U x = 0;
        for (int i = 0; i < (int)values.size(); i++)
            if (mask >> i & 1)
                x ^= values[i];
        all.insert(x);
        nonempty.insert(x);
    }
    assert((W(1) << a.rank) == all.size());
    assert(a.rank == b.rank);
    assert(a.dependent == nonempty.count(0));
    assert(a.dependent == b.dependent);
    for (U x : {0ULL,1ULL,7ULL,255ULL,1ULL<<63,~0ULL})
    {
        U want = 0;
        for (U y : all)
            want = max(want,x^y);
        assert(a.query(x) == want && b.Query(x) == want);
        assert(a.contains(x) == all.count(x));
        assert(b.Contains(x) == all.count(x));
    }
    for (U x : all)
        assert(a.contains(x) && b.Contains(x));
    for (bool mode : {false,true})
    {
        auto &expected = mode ? nonempty : all;
        W k = 1;
        assert(!a.kth(0,mode) && !b.Kth(0,mode));
        for (U x : expected)
        {
            assert(a.kth(k,mode) == x && b.Kth(k,mode) == x);
            k++;
        }
        assert(!a.kth(k,mode) && !b.Kth(k,mode));
        assert(a.minimum(mode) == (expected.empty() ? optional<U>{} : *expected.begin()));
        assert(b.Minimum(mode) == a.minimum(mode));
    }
    auto old_a = a.p, old_b = b.p;
    a.rebuild();
    b.Rebuild();
    assert(a.p == old_a && b.p == old_b);
}

int main()
{
    for (int n = 0, total = 1; n <= 5; n++, total *= 4)
        for (int code = 0; code < total; code++)
        {
            XorBasis a;
            Xor_Basis b;
            vector<U> values;
            int t = code;
            for (int i = 0; i < n; i++)
            {
                U x = t%4;
                t /= 4;
                assert(a.insert(x) == b.Insert(x));
                values.push_back(x);
                verify(a,b,values);
            }
            verify(a,b,values);
            a = XorBasis();
            b.Init();
            verify(a,b,{});
        }
    mt19937_64 rng(712367);
    for (int trial = 0; trial < 500; trial++)
    {
        vector<U> values;
        XorBasis a, c;
        Xor_Basis b, d;
        for (int i = 0; i < 8; i++)
        {
            U x = trial%2 ? rng() : rng()%64;
            values.push_back(x);
            if (i < 4)
            {
                a.insert(x);
                b.Insert(x);
            }
            else
            {
                c.insert(x);
                d.Insert(x);
            }
        }
        a.merge(c);
        b.Merge(d);
        verify(a,b,values);
    }
    XorBasis a;
    Xor_Basis b;
    for (int i = 0; i < 64; i++)
    {
        assert(a.insert(1ULL<<i) && b.Insert(1ULL<<i));
        assert(a.kth(1,false) == 0 && b.Kth(1,false) == 0);
    }
    W count = W(1)<<64;
    assert(a.kth(count,false) == ~0ULL && b.Kth(count,false) == ~0ULL);
    assert(!a.kth(count,true) && !b.Kth(count,true));
    assert(!a.kth(~W(0),false) && !b.Kth(~W(0),false));
    for (int i = 0; i < 10000; i++)
    {
        U x = rng();
        assert(a.kth(W(x)+1,false) == x && b.Kth(W(x)+1,false) == x);
    }
    a.merge(a);
    b.Merge(b);
    assert(a.dependent && b.dependent);
    assert(a.kth(count,true) == ~0ULL && b.Kth(count,true) == ~0ULL);
    a = XorBasis();
    b.Init();
    for (int i = 1; i < 64; i++)
    {
        a.insert(1ULL<<i);
        b.Insert(1ULL<<i);
    }
    W half = W(1)<<63;
    assert(a.kth(half,false) == ~1ULL && b.Kth(half,false) == ~1ULL);
    assert(!a.kth(half,true) && !b.Kth(half,true));
    XorBasis zero;
    Xor_Basis zero_b;
    zero.insert(0);
    zero_b.Insert(0);
    a.merge(zero);
    b.Merge(zero_b);
    assert(a.kth(half,true) == ~1ULL && b.Kth(half,true) == ~1ULL);
    cout << "Xor basis dual exhaustive nonempty subsets, merge, cache and 64-bit kth boundaries PASS\n";
}
