#pragma once
#include "mod64.hpp"

// BEGIN StaticMod64
template <uint64_t P> struct StaticMod64
{
    static_assert(P > 0);
    uint64_t v = 0;

    StaticMod64() = default;

    template <integral T> StaticMod64(T x)
    {
        static_assert(sizeof(T) <= 8);
        __int128_t r = __int128_t(x) % __int128_t(P);
        if (r < 0)
            r += P;
        v = r;
    }

    StaticMod64 operator+(StaticMod64 b) const
    {
        StaticMod64 r;
        r.v = v >= P - b.v ? v - (P - b.v) : v + b.v;
        return r;
    }

    StaticMod64 operator-(StaticMod64 b) const
    {
        StaticMod64 r;
        r.v = v >= b.v ? v - b.v : P - (b.v - v);
        return r;
    }

    StaticMod64 operator-() const
    {
        StaticMod64 r;
        r.v = v == 0 ? 0 : P - v;
        return r;
    }

    StaticMod64 operator*(StaticMod64 b) const
    {
        StaticMod64 r;
        r.v = Mod64::mul(v, b.v, P);
        return r;
    }

    StaticMod64 &operator+=(StaticMod64 b)
    {
        return *this = *this + b;
    }

    StaticMod64 &operator-=(StaticMod64 b)
    {
        return *this = *this - b;
    }

    StaticMod64 &operator*=(StaticMod64 b)
    {
        return *this = *this * b;
    }

    StaticMod64 pow(uint64_t k) const
    {
        StaticMod64 r;
        r.v = Mod64::power(v, k, P);
        return r;
    }

    optional<StaticMod64> try_inv() const
    {
        __int128_t a = v, b = P, x = 1, y = 0;
        while (b)
        {
            __int128_t q = a / b;
            tie(a, b) = pair{b, a - q * b};
            tie(x, y) = pair{y, x - q * y};
        }
        if (a != 1)
            return nullopt;
        if (x < 0)
            x += P;
        return StaticMod64(uint64_t(x));
    }

    StaticMod64 inv() const
    {
        auto r = try_inv();
        assert(r.has_value());
        return *r;
    }

    StaticMod64 operator/(StaticMod64 b) const
    {
        return *this * b.inv();
    }

    StaticMod64 &operator/=(StaticMod64 b)
    {
        return *this = *this / b;
    }

    bool operator==(const StaticMod64 &) const = default;
};
// END StaticMod64
