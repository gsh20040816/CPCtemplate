#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int l = 1;
    int r = 100;
    while (l < r) {
        int m = (l + r) / 2;
        cout << "? " << m << endl;
        int reply;
        if (!(cin >> reply) || reply == -1) {
            return 1;
        }
        if (reply == 1) {
            r = m;
        } else {
            l = m + 1;
        }
    }
    cout << "! " << l << endl;
}
