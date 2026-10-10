#include <bits/stdc++.h>
using namespace std;
using Clock = chrono::steady_clock;

__attribute__((noinline))
uint64_t consume(vector<int> a) {
    return accumulate(a.begin(), a.end(), uint64_t(0));
}

__attribute__((noinline))
uint64_t read_values(const vector<int>& a) {
    return accumulate(a.begin(), a.end(), uint64_t(0));
}

int main(int argc, char** argv) {
    if (argc != 3) {
        return 2;
    }
    string mode = argv[1];
    int n = stoi(argv[2]);
    uint64_t sum = 0;
    vector<int> a;
    if (mode != "grow" && mode != "reserve") {
        a.resize(n);
        for (int i = 0; i < n; i++) {
            a[i] = i % 1009;
        }
    }
    auto start = Clock::now();
    if (mode == "grow" || mode == "reserve") {
        if (mode == "reserve") {
            a.reserve(n);
        }
        for (int i = 0; i < n; i++) {
            a.push_back(i % 1009);
        }
        sum = accumulate(a.begin(), a.end(), uint64_t(0));
    } else if (mode == "copy") {
        sum = consume(a);
    } else if (mode == "reference") {
        sum = read_values(a);
    } else if (mode == "move") {
        sum = consume(std::move(a));
    } else if (mode == "row" || mode == "column") {
        int side = sqrt(n);
        if (side * side != n) {
            return 2;
        }
        if (mode == "row") {
            for (int i = 0; i < side; i++) {
                for (int j = 0; j < side; j++) {
                    sum += a[i * side + j];
                }
            }
        } else {
            for (int j = 0; j < side; j++) {
                for (int i = 0; i < side; i++) {
                    sum += a[i * side + j];
                }
            }
        }
    } else {
        return 2;
    }
    double ms = chrono::duration<double, milli>(Clock::now() - start).count();
    cout << sum << ' ' << fixed << setprecision(6) << ms << '\n';
}
