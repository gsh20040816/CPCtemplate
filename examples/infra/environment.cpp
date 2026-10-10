#include <bits/stdc++.h>
#include <sys/resource.h>
#include <ext/pb_ds/assoc_container.hpp>
using namespace std;

int main() {
    cout << "compiler " << __VERSION__ << '\n';
    cout << "standard " << __cplusplus << '\n';
    cout << "int128 " << sizeof(__int128) << '\n';
    __gnu_pbds::gp_hash_table<int, int> table;
    table[7] = 9;
    cout << "pbds " << table[7] << '\n';
    rlimit limit;
    if (getrlimit(RLIMIT_STACK, &limit) != 0) {
        return 1;
    }
    cout << "stack soft/hard " << limit.rlim_cur << ' ';
    cout << limit.rlim_max << " bytes; infinity=" << RLIM_INFINITY << '\n';
    cout << "avx2 " << bool(__builtin_cpu_supports("avx2")) << '\n';
    cout << "avx512f " << bool(__builtin_cpu_supports("avx512f")) << '\n';
    uint64_t x = 1;
    auto start = chrono::steady_clock::now();
    for (int i = 0; i < 10000000; i++) {
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
    }
    double seconds = chrono::duration<double>(chrono::steady_clock::now() - start).count();
    cout << "checksum " << x << " seconds " << seconds << '\n';
}
