#include <bits/stdc++.h>
using namespace std;

#pragma GCC push_options
#pragma GCC optimize("O3", "unroll-loops")
uint64_t sum_values(const vector<unsigned>& a) {
    uint64_t sum = 0;
    for (unsigned x : a) {
        sum += x;
    }
    return sum;
}
#pragma GCC pop_options

int main() {
    vector<unsigned> a{1, 2, 3};
    cout << sum_values(a) << '\n';
}
