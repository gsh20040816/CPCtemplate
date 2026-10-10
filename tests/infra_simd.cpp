#include <bits/stdc++.h>
#include <cassert>
#include <sys/mman.h>
#include <unistd.h>
#include "../examples/infra/simd.hpp"
using namespace std;

void automatic_add(const uint32_t* __restrict a, const uint32_t* __restrict b,
                   uint32_t* __restrict out, int n) {
    for (int i = 0; i < n; i++) {
        out[i] = a[i] + b[i];
    }
}

struct Guarded {
    size_t bytes = sysconf(_SC_PAGESIZE);
    void* base = mmap(nullptr, bytes * 2, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    explicit Guarded() {
        assert(base != MAP_FAILED);
        assert(mprotect((char*)base + bytes, bytes, PROT_NONE) == 0);
    }
    uint32_t* tail(int n) {
        assert(n >= 0 && (size_t)n * 4 <= bytes);
        return (uint32_t*)((char*)base + bytes) - n;
    }
    ~Guarded() {
        munmap(base, bytes * 2);
    }
};

int main(int argc, char** argv) {
    assert(__builtin_cpu_supports("avx2"));
    assert(__builtin_cpu_supports("avx512f"));
    mt19937 rng(712367);
    if (argc > 1) {
        int mode = stoi(argv[1]);
        int n = 1 << 20;
        vector<uint32_t> a(n), b(n), out(n);
        for (int i = 0; i < n; i++) {
            a[i] = rng();
            b[i] = rng();
        }
        auto function = mode == 0 ? automatic_add : mode == 1 ? add_avx2 : add_avx512;
        auto start = chrono::steady_clock::now();
        for (int round = 0; round < 100; round++) {
            function(a.data(), b.data(), out.data(), n);
            asm volatile("" : : "g"(out.data()) : "memory");
        }
        double ms = chrono::duration<double, milli>(chrono::steady_clock::now() - start).count();
        for (int i = 0; i < n; i++) {
            assert(out[i] == uint32_t(a[i] + b[i]));
        }
        cout << fixed << setprecision(6) << ms << '\n';
        return 0;
    }
    Guarded a;
    Guarded b;
    Guarded out;
    for (int n = 0; n <= 1024; n++) {
        auto x = a.tail(n);
        auto y = b.tail(n);
        auto z = out.tail(n);
        vector<int32_t> signed_values(n);
        for (int i = 0; i < n; i++) {
            x[i] = rng();
            y[i] = rng();
            signed_values[i] = bit_cast<int32_t>(x[i]);
        }
        for (auto function : {add_avx2, add_avx512}) {
            function(x, y, z, n);
            for (int i = 0; i < n; i++) {
                assert(z[i] == uint32_t(x[i] + y[i]));
            }
        }
        for (int32_t bound : {INT32_MIN, -1, 0, 1, INT32_MAX}) {
            int expected = count_if(signed_values.begin(), signed_values.end(),
                                    [&](int32_t x) { return x < bound; });
            assert(count_less_avx2(signed_values.data(), n, bound) == expected);
        }
    }
    cout << "SIMD lengths 0..1024, guard pages, modular sums and signed bounds PASS\n";
}
