#include <bits/stdc++.h>
#include <cassert>
using namespace std;

int square(int x) {
    assert(0 <= x && x <= 10000);
#ifdef LOCAL
    cerr << "x=" << x << '\n';
#endif
    int result = x * x;
    return result;
}

int main() {
    int x;
    if (!(cin >> x)) {
        return 1;
    }
    int answer = square(x);
    cout << answer << '\n';
}
