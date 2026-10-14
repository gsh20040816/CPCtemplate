#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN ODT
// Chtholly tree on [lo, hi): map keys are segment starts, the key hi closes the last segment.
template <class T> struct ODT
{
    map<long long, T> mp;

    ODT(long long lo, long long hi, T v = T())
    {
        mp[lo] = v;
        mp[hi] = T();
    }

    // Make x a segment start (lo <= x <= hi) and return its iterator.
    typename map<long long, T>::iterator split(long long x)
    {
        auto it = prev(mp.upper_bound(x));
        if (it->first == x) return it;
        return mp.emplace_hint(next(it), x, it->second);
    }

    // Set [l, r) to v, l <= r.
    void assign(long long l, long long r, T v)
    {
        auto R = split(r), L = split(l);
        mp.erase(L, R);
        mp.emplace_hint(R, l, v);
    }

    // f(l, r, value&) for every segment inside [l, r); f may change the value.
    template <class F> void each(long long l, long long r, F f)
    {
        auto R = split(r), L = split(l);
        for (; L != R; ++L) f(L->first, next(L)->first, L->second);
    }
};
// END ODT
