#include <bits/stdc++.h>
using namespace std;

int main(int argc, char** argv) {
    bool fast = argc > 1 && string(argv[1]) == "fast";
    if (fast) {
        ios::sync_with_stdio(false);
        cin.tie(nullptr);
    }
    auto start = chrono::steady_clock::now();
    uint64_t sum = 0;
    int x;
    while (cin >> x) {
        sum += x;
    }
    double ms = chrono::duration<double, milli>(chrono::steady_clock::now() - start).count();
    cout << sum << ' ' << fixed << setprecision(6) << ms << '\n';
}
