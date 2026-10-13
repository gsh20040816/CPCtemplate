#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_segt2/main.cpp"

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "overflow") {
        Segt_<int> t(3);
        t.modify(1, 3, 1000000000);
        cout << t.ask(1, 3) << '\n';
        return 0;
    }
    Segt_<long long> t(vector<int>{0, 1, 2, 3, 4});
    vector<long long> a = {0, 1, 2, 3, 4};
    auto add = [&](int l, int r, long long v) {
        t.modify(l, r, v);
        for (int i = l; i <= r; i++) a[i] += v;
    };
    auto mul = [&](int l, int r, long long v) {
        t.modify2(l, r, v);
        for (int i = l; i <= r; i++) a[i] *= v;
    };
    add(1, 4, 1);
    mul(1, 2, 4);
    add(2, 4, 5);
    mul(3, 4, -1);
    for (int l = 1; l <= 4; l++) for (int r = l; r <= 4; r++) {
        long long sum = 0;
        for (int i = l; i <= r; i++) sum += a[i];
        if (t.ask(l, r) != sum) return 1;
    }
    cout << "ok\n";
}
