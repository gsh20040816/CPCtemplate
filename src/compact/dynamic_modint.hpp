#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN mint
template <int tag = 0> struct mint
{
    static inline int mod = 998244353;
    int v;

    static void set_mod(int p)
    {
        assert(p >= 1);
        mod = p;
    }

    mint(long long x = 0) : v((x % mod + mod) % mod) {}

    mint operator+(mint b) const { return mint((long long)v + b.v); }

    mint operator-(mint b) const { return mint((long long)v - b.v); }

    mint operator*(mint b) const { return mint(1LL * v * b.v); }

    mint &operator+=(mint b) { return *this = *this + b; }

    mint &operator-=(mint b) { return *this = *this - b; }

    mint &operator*=(mint b) { return *this = *this * b; }

    mint pow(uint64_t k) const
    {
        mint a = *this, r = 1;
        for (; k; k >>= 1, a *= a)
            if (k & 1) r *= a;
        return r;
    }

    optional<mint> try_inv() const
    {
        long long a = v, b = mod, x = 1, y = 0;
        while (b)
        {
            long long q = a / b;
            tie(a, b) = pair{b, a - q * b};
            tie(x, y) = pair{y, x - q * y};
        }
        if (a != 1) return nullopt;
        return mint(x);
    }

    mint inv() const
    {
        auto x = try_inv();
        assert(x.has_value());
        return *x;
    }

    mint operator/(mint b) const { return *this * b.inv(); }

    mint &operator/=(mint b) { return *this = *this / b; }

    bool operator==(const mint &) const = default;
};

// END mint
