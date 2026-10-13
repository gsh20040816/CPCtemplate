#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_fenwick/main.cpp"

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "overflow") {
        BIT t(2);
        t.add(1, 2000000000);
        t.add(1, 2000000000);
        cout << t.ask(1) << '\n';
        return 0;
    }
    BIT t(6);
    vector<int> a(7);
    auto add = [&](int x, int k) {
        t.add(x, k);
        a[x] += k;
    };
    add(1, 4);
    add(3, 5);
    add(6, -2);
    for (int r = 1; r <= 6; r++) {
        int sum = 0;
        for (int i = 1; i <= r; i++) sum += a[i];
        if (t.ask(r) != sum) return 1;
        for (int l = 1; l <= r; l++) {
            int part = 0;
            for (int i = l; i <= r; i++) part += a[i];
            if (t.ask(l, r) != part) return 1;
        }
    }
    BIT d(6);
    d.add(2, 5, 3);
    cout << d.ask(1) << ' ' << d.ask(2) << ' ' << d.ask(4) << ' ' << d.ask(5) << ' ' << d.ask(6) << '\n';
}
