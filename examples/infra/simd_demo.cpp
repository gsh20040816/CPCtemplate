#include <bits/stdc++.h>
#include <cassert>
#include "simd.hpp"
using namespace std;

#pragma GCC push_options
#pragma GCC target("avx2")
void reverse_eight(const int32_t* a, int32_t* out) {
    auto x = _mm256_loadu_si256((const __m256i*)a);
    auto order = _mm256_setr_epi32(7, 6, 5, 4, 3, 2, 1, 0);
    auto y = _mm256_permutevar8x32_epi32(x, order);
    _mm256_storeu_si256((__m256i*)out, y);
}
#pragma GCC pop_options

int main() {
    vector<uint32_t> a{0, UINT32_MAX, 7};
    vector<uint32_t> b{1, 2, 8};
    vector<uint32_t> out(3);
    add_avx2(a.data(), b.data(), out.data(), 3);
    assert(out == vector<uint32_t>({1, 1, 15}));
    add_avx512(a.data(), b.data(), out.data(), 3);
    assert(out == vector<uint32_t>({1, 1, 15}));
    vector<int32_t> c{0, -1, 2, 3, 4, 5, 6, INT32_MIN};
    vector<int32_t> reversed(8);
    reverse_eight(c.data(), reversed.data());
    reverse(c.begin(), c.end());
    assert(c == reversed);
    assert(count_less_avx2(c.data(), 8, 0) == 2);
    cout << "SIMD demo PASS\n";
}
