#include <bits/stdc++.h>
#include <cassert>
#include <ext/pb_ds/assoc_container.hpp>
using namespace std;

struct Hash {
    static uint64_t mix(uint64_t x) {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }

    size_t operator()(uint64_t x) const {
        static const uint64_t seed =
            chrono::steady_clock::now().time_since_epoch().count();
        return mix(x + seed);
    }
};

int main() {
    unordered_map<long long, int, Hash> a;
    __gnu_pbds::gp_hash_table<long long, int, Hash> b;
    a.reserve(1000);
    for (long long x : {-1LL, 0LL, LLONG_MIN, LLONG_MAX}) {
        a[x]++;
        b[x]++;
        assert(a.at(x) == b.find(x)->second);
    }
    cout << a.size() << ' ' << b.size() << '\n';
}
