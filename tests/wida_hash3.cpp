#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_hash3/main.cpp"

static int expect(const string &s, int mod, int base)
{
    long long ans = 0;
    for (char c : s) ans = (ans * base + (c - 'a')) % mod;
    if (ans < 0) ans += mod;
    return (int)ans;
}

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "small") {
        cout << Miller_rabin(1) << Miller_rabin(2) << Miller_rabin(9) << Miller_rabin(17) << ' ' << findPrime(14) << '\n';
        String s(100, 10, 2);
        cout << s.get("a0") << '\n';
        return 0;
    }
    if (mode == "overflow") {
        String s(1000000007, 127, 8);
        cout << s.MOD << '\n';
        return 0;
    }
    StringHash h(2);
    string s = "ab", raw = s;
    pii got = h[s];
    pii changed = h.modify(got, raw, 0, 'c');
    int a = expect(s, h.chk1.MOD, h.chk1.BASE);
    int b = expect(s, h.chk2.MOD, h.chk2.BASE);
    int c = expect("cb", h.chk1.MOD, h.chk1.BASE);
    int d = expect("cb", h.chk2.MOD, h.chk2.BASE);
    if (got.first != a || got.second != b || changed.first != c || changed.second != d) return 1;
    cout << h.chk1.MOD << ' ' << h.chk1.BASE << ' ' << h.chk2.MOD << ' ' << h.chk2.BASE << '\n';
}
