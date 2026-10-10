#include <bits/stdc++.h>
using namespace std;

// Deliberately incorrect: run only to demonstrate the named checker.
int main(int argc, char** argv) {
    if (argc != 2) {
        return 2;
    }
    int mode = stoi(argv[1]);
    if (mode == 1) {
        volatile int x = INT_MAX;
        cout << x + 1 << '\n';
    } else if (mode == 2) {
        auto p = make_unique<int[]>(1);
        volatile int index = 1;
        cout << p[index] << '\n';
    } else if (mode == 3) {
        vector<int> a(1);
        a.reserve(8);
        cout << a[3] << '\n';
    } else if (mode == 4) {
        vector<int> a{1, 2};
        auto it = a.begin();
        a.erase(it);
        cout << *it << '\n';
    }
}
