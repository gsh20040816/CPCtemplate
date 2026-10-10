#include <cstdint>
#include <immintrin.h>

#pragma GCC push_options
#pragma GCC target("avx2")

// n >= 0; a, b, out each contain n uint32_t; output does not overlap input.
void add_avx2(const uint32_t* a, const uint32_t* b, uint32_t* out, int n) {
    int i = 0;
    for (; i <= n - 8; i += 8) {
        auto x = _mm256_loadu_si256((const __m256i*)(a + i));
        auto y = _mm256_loadu_si256((const __m256i*)(b + i));
        auto z = _mm256_add_epi32(x, y);
        _mm256_storeu_si256((__m256i*)(out + i), z);
    }
    for (; i < n; i++) {
        out[i] = a[i] + b[i];
    }
}

int count_less_avx2(const int32_t* a, int n, int32_t bound) {
    auto limit = _mm256_set1_epi32(bound);
    int count = 0;
    int i = 0;
    for (; i <= n - 8; i += 8) {
        auto x = _mm256_loadu_si256((const __m256i*)(a + i));
        auto mask = _mm256_cmpgt_epi32(limit, x);
        unsigned bits = _mm256_movemask_ps(_mm256_castsi256_ps(mask));
        count += __builtin_popcount(bits);
    }
    for (; i < n; i++) {
        count += a[i] < bound;
    }
    return count;
}

#pragma GCC pop_options
#pragma GCC push_options
#pragma GCC target("avx512f")

void add_avx512(const uint32_t* a, const uint32_t* b, uint32_t* out, int n) {
    int i = 0;
    for (; i <= n - 16; i += 16) {
        auto x = _mm512_loadu_si512(a + i);
        auto y = _mm512_loadu_si512(b + i);
        _mm512_storeu_si512(out + i, _mm512_add_epi32(x, y));
    }
    if (i < n) {
        __mmask16 mask = (1u << (n - i)) - 1;
        auto x = _mm512_maskz_loadu_epi32(mask, a + i);
        auto y = _mm512_maskz_loadu_epi32(mask, b + i);
        _mm512_mask_storeu_epi32(out + i, mask, _mm512_add_epi32(x, y));
    }
}

#pragma GCC pop_options
