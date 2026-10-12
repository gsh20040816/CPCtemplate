#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN Montgomery
// Odd modulus, including composites. v is a Montgomery residue; use get().
template <uint32_t P> struct Montgomery
{
    static_assert(P > 1 && P < (1U << 30) && (P & 1));

    static constexpr uint32_t inverse32()
    {
        uint32_t x = P;
        for (int i = 0; i < 4; i++)
            x *= 2U - P * x;
        return -x;
    }

    static constexpr uint32_t neg_inv = inverse32();
    static constexpr uint32_t r2 = -uint64_t(P) % P;
    uint32_t v = 0;

    // Internal: x < P * 2^32. The returned residue lies in [0, P).
    static uint32_t reduce(uint64_t x)
    {
        uint32_t q = uint32_t(x) * neg_inv;
        uint32_t y = (x + uint64_t(q) * P) >> 32;
        return y >= P ? y - P : y;
    }

    Montgomery(long long x = 0)
    {
        long long y = x % P;
        if (y < 0)
            y += P;
        v = reduce(uint64_t(y) * r2);
    }

    uint32_t get() const
    {
        return reduce(v);
    }

    Montgomery operator+(Montgomery b) const
    {
        Montgomery r;
        r.v = v + b.v;
        if (r.v >= P)
            r.v -= P;
        return r;
    }

    Montgomery operator-(Montgomery b) const
    {
        Montgomery r;
        r.v = v >= b.v ? v - b.v : v + P - b.v;
        return r;
    }

    Montgomery operator-() const
    {
        Montgomery r;
        r.v = v == 0 ? 0 : P - v;
        return r;
    }

    Montgomery operator*(Montgomery b) const
    {
        Montgomery r;
        r.v = reduce(uint64_t(v) * b.v);
        return r;
    }

    Montgomery &operator+=(Montgomery b)
    {
        return *this = *this + b;
    }

    Montgomery &operator-=(Montgomery b)
    {
        return *this = *this - b;
    }

    Montgomery &operator*=(Montgomery b)
    {
        return *this = *this * b;
    }

    Montgomery pow(uint64_t k) const
    {
        Montgomery a = *this, r = 1;
        while (k)
        {
            if (k & 1)
                r *= a;
            a *= a;
            k >>= 1;
        }
        return r;
    }

    optional<Montgomery> try_inv() const
    {
        long long a = get(), b = P, x = 1, y = 0;
        while (b)
        {
            long long q = a / b;
            tie(a, b) = pair{b, a - q * b};
            tie(x, y) = pair{y, x - q * y};
        }
        if (a != 1)
            return nullopt;
        return Montgomery(x);
    }

    Montgomery inv() const
    {
        auto r = try_inv();
        assert(r.has_value());
        return *r;
    }

    Montgomery operator/(Montgomery b) const
    {
        return *this * b.inv();
    }

    Montgomery &operator/=(Montgomery b)
    {
        return *this = *this / b;
    }

    bool operator==(const Montgomery &) const = default;
};
// END Montgomery
