#include <bits/stdc++.h>
#include <cassert>
using namespace std;

vector<int> positions(uint64_t x) {
    vector<int> p;
    while (x) {
        p.push_back(__builtin_ctzll(x));
        x &= x - 1;
    }
    return p;
}

int main() {
    uint64_t x = (1ULL << 63) | 5;
    assert(__builtin_popcountll(x) == 3);
    assert(63 - __builtin_clzll(x) == 63);
    assert(positions(x) == vector<int>({0, 2, 63}));
    assert(positions(0).empty());
    bitset<130> b;
    b.set(0);
    b.set(64);
    b.set(129);
    for (size_t i = b._Find_first(); i < b.size(); i = b._Find_next(i)) {
        cout << i << '\n';
    }
    b.reset();
    assert(b._Find_first() == b.size());
    return 0;
}
