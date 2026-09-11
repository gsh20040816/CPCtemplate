#include "../src/compact/position_basis.hpp"
#include "../src/classic/position_basis.hpp"
#include <climits>
#include <iostream>
#include <random>
#include <set>
#include <vector>
using U = unsigned long long;
using Item = pair<U,int>;

void verify(const PositionBasis &a, const Position_Basis &b, const vector<Item> &items)
{
    vector<long long> thresholds{0,1,2,3,4,INT_MAX,(long long)INT_MAX+1,LLONG_MAX};
    for (auto [x,t] : items)
    {
        thresholds.push_back(t);
        thresholds.push_back((long long)t+1);
    }
    sort(thresholds.begin(),thresholds.end());
    thresholds.erase(unique(thresholds.begin(),thresholds.end()),thresholds.end());
    for (long long lower : thresholds)
    {
        set<U> span{0};
        for (auto [x,t] : items)
            if (t >= lower)
            {
                auto old = span;
                for (U y : old)
                    span.insert(x^y);
            }
        assert((1ULL << a.rank(lower)) == span.size());
        assert(a.rank(lower) == b.Rank(lower));
        for (U seed : {0ULL,1ULL,2ULL,3ULL,7ULL,1ULL<<63,~0ULL})
        {
            U want = 0;
            for (U x : span)
                want = max(want,x^seed);
            assert(a.query(lower,seed) == want && b.Query(lower,seed) == want);
            assert(a.contains(seed,lower) == span.count(seed));
            assert(b.Contains(seed,lower) == span.count(seed));
        }
        for (U x : span)
            assert(a.contains(x,lower) && b.Contains(x,lower));
    }
}

int main()
{
    for (int n = 0, total = 1; n <= 3; n++, total *= 12)
        for (int code = 0; code < total; code++)
        {
            PositionBasis a;
            Position_Basis b;
            vector<Item> items;
            int x = code;
            for (int i = 0; i < n; i++)
            {
                Item item{x%4,x/4%3};
                x /= 12;
                items.push_back(item);
                a.insert(item.first,item.second);
                b.Insert(item.first,item.second);
                verify(a,b,items);
            }
            verify(a,b,items);
            a.init();
            b.Init();
            verify(a,b,{});
        }
    mt19937_64 rng(1100);
    for (int trial = 0; trial < 1000; trial++)
    {
        PositionBasis a;
        Position_Basis b;
        vector<Item> items;
        for (int i = 0; i < 8; i++)
        {
            U x = trial%2 ? rng() : rng()%16;
            int t = i%3 ? rng()%5 : INT_MAX;
            items.emplace_back(x,t);
            a.insert(x,t);
            b.Insert(x,t);
            verify(a,b,items);
        }
    }
    // Right endpoint sweep: compare all intervals with subset closure.
    for (int trial = 0; trial < 300; trial++)
    {
        vector<U> values(12);
        PositionBasis a;
        Position_Basis b;
        for (int r = 0; r < 12; r++)
        {
            values[r] = rng()%128;
            a.insert(values[r],r);
            b.Insert(values[r],r);
            for (int l = 0; l <= r; l++)
            {
                set<U> span{0};
                for (int j = l; j <= r; j++)
                {
                    auto old = span;
                    for (U x : old)
                        span.insert(x^values[j]);
                }
                assert(a.query(l) == *span.rbegin());
                assert(b.Query(l) == *span.rbegin());
            }
        }
    }
    PositionBasis a;
    Position_Basis b;
    for (int i = 0; i < 64; i++)
    {
        a.insert(1ULL<<i,i);
        b.Insert(1ULL<<i,i);
    }
    for (int l = 0; l <= 64; l++)
    {
        U expected = l == 64 ? 0 : ~0ULL << l;
        assert(a.rank(l) == 64-l && b.Rank(l) == 64-l);
        assert(a.query(l) == expected && b.Query(l) == expected);
    }
    for (int i = 0; i < 500000; i++)
    {
        a.insert(1ULL<<(i%64),i);
        b.Insert(1ULL<<(i%64),i);
    }
    assert(a.rank(499936) == 64 && b.Rank(499936) == 64);
    assert(a.query(499936) == ~0ULL && b.Query(499936) == ~0ULL);
    assert(a.rank(500000) == 0 && b.Rank(500000) == 0);
    cout << "Position basis dual threshold subset oracle, arbitrary tags, all intervals and 64-bit scale PASS\n";
}
