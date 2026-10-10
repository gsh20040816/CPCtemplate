#include <bits/stdc++.h>
using namespace std;

int main(int argc, char** argv) {
    bool fresh = argc > 1 && string(argv[1]) == "fresh";
    vector<int> a;
    uint64_t sum = 0;
    auto start = chrono::steady_clock::now();
    for (int round = 0; round < 2048; round++) {
        if (fresh) {
            vector<int>().swap(a);
        } else {
            a.clear();
        }
        for (int i = 0; i < 4096; i++) {
            a.push_back(i ^ round);
        }
        sum += accumulate(a.begin(), a.end(), uint64_t(0));
    }
    double ms = chrono::duration<double, milli>(chrono::steady_clock::now() - start).count();
    cout << sum << ' ' << fixed << setprecision(6) << ms << '\n';
}
