#pragma once
#include "algebra.hpp"
#include "linear_congruence.hpp"

struct Kth_Residue
{
    using ll = long long;
    ll first, ratio, count;

    // Prime p <= 1e12; g is a primitive root of p; k > 0.
    // All roots: first * ratio^i mod p, 0 <= i < count.
    static optional<Kth_Residue> Solve(ll a, unsigned long long k, ll p, ll g)
    {
        assert(p >= 2 && p <= 1000000000000LL && g >= 1 && g < p && k > 0);
        a %= p;
        if ( a < 0 )
            a += p;
        if ( a == 0 )
            return Kth_Residue{0, 1, 1};
        ll logarithm = Discrete_Log::Solve(g, a, p);
        if ( logarithm < 0 )
            return nullopt;
        auto [exponent, period] = Linear_Congruence(k % (p - 1), -logarithm, p - 1);
        if ( exponent < 0 )
            return nullopt;
        ll first = Number_Theory::Power(g, exponent, p);
        ll ratio = Number_Theory::Power(g, period, p);
        return Kth_Residue{first, ratio, (p - 1) / period};
    }
};
