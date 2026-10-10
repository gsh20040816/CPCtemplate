#include <bits/stdc++.h>
using namespace std;

int main() {
    using Clock = chrono::steady_clock;
    auto start = Clock::now();
    auto deadline = start + chrono::milliseconds(20);
    mt19937_64 rng(start.time_since_epoch().count());
    uint64_t checksum = 0;
    do {
        for (int i = 0; i < 1024; i++) {
            checksum ^= rng();
        }
    } while (Clock::now() < deadline);
    auto elapsed = Clock::now() - start;
    auto ms = chrono::duration_cast<chrono::milliseconds>(elapsed).count();
    double seconds = chrono::duration<double>(elapsed).count();
    cout << checksum << '\n';
    cerr << ms << " ms, " << seconds << " s\n";
}
