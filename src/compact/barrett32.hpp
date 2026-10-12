#pragma once
#include <cassert>
#include <cstdint>

// BEGIN Barrett32
struct Barrett32
{
    uint32_t mod;
    uint64_t reciprocal;

    Barrett32(uint32_t m) : mod(m)
    {
        assert(m != 0);
        reciprocal = UINT64_MAX / m + 1;
    }

    // Requires a < mod and b < mod.
    uint32_t mul(uint32_t a, uint32_t b) const
    {
        uint64_t z = uint64_t(a) * b;
        uint64_t q = (__uint128_t(z) * reciprocal) >> 64;
        uint64_t y = q * mod;
        return uint32_t(z - y + (z < y ? mod : 0));
    }
};
// END Barrett32
