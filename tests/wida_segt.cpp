#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_segt/main.cpp"

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "sentinel") {
        int sentinel = 1E18;
        Segt t(4);
        cout << sentinel << ' ' << t.Min(1, 2) << ' ' << t.Min(2, 3) << '\n';
        return 0;
    }
    Segt_<long long> t(vector<int>{0, 1, 2, 3, 4, 5});
    vector<long long> a = {0, 1, 2, 3, 4, 5};
    auto add = [&](int l, int r, long long v) {
        t.modify(l, r, v);
        for (int i = l; i <= r; i++) a[i] += v;
    };
    add(2, 4, 10);
    add(1, 5, -1);
    for (int l = 1; l <= 5; l++) for (int r = l; r <= 5; r++) {
        long long sum = 0, mn = a[l];
        for (int i = l; i <= r; i++) {
            sum += a[i];
            mn = min(mn, a[i]);
        }
        if (t.ask(l, r) != sum || t.Min(l, r) != mn) return 1;
        auto merged = t.Ask(l, r);
        if (merged.w != sum || merged.Min != mn) return 1;
    }
    auto split = t.Ask(2, 4);
    if (split.l != 0 || split.r != 0) return 1;
    cout << "ok\n";
}
