#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_fenwick2/main.cpp"

static int inversions(const vector<int> &a)
{
    int n = (int)a.size() - 1, ans = 0;
    for (int i = 1; i <= n; i++)
        for (int j = i + 1; j <= n; j++)
            if (a[i] > a[j]) ans++;
    return ans;
}

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "inv") {
        BIT t;
        vector<int> a = {0, 3, 1, 2, 2, 0};
        cout << t.get(a) << ' ' << inversions(a) << '\n';
        return 0;
    }
    BIT t(4);
    vector<int> f = {0, 1, 0, 2, 1};
    for (int i = 1; i <= 4; i++) t.add(i, f[i]);
    for (int k = 1; k <= 4; k++) {
        int seen = 0, expect = -1;
        for (int i = 1; i <= 4; i++) {
            seen += f[i];
            if (seen >= k) {
                expect = i;
                break;
            }
        }
        if (t.kth(k) != expect) return 1;
    }
    BIT d(5);
    d.add(2, 5, 3);
    cout << t.kth(4) << ' ' << t.kth(5) << ' ' << d.ask(4) << ' ' << d.ask(5) << '\n';
}
