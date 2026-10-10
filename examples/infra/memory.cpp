#include <bits/stdc++.h>
using namespace std;

int main() {
    clock_t start = clock();
    vector<int> a(1000000);
    iota(a.begin(), a.end(), 0);
    cout << accumulate(a.begin(), a.end(), 0LL) << '\n';
    ifstream status("/proc/self/status");
    for (string line; getline(status, line); ) {
        if (line.starts_with("VmPeak:") || line.starts_with("VmHWM:")) {
            cerr << line << '\n';
        }
    }
    clock_t finish = clock();
    if (start != clock_t(-1) && finish != clock_t(-1)) {
        cerr << "CPU seconds " << double(finish - start) / CLOCKS_PER_SEC << '\n';
    }
}
