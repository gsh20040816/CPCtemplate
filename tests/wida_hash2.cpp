#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_hash2/main.cpp"

static int expect(const string &s, int mod, int base)
{
    long long ans = 0;
    for (unsigned char c : s) ans = (ans * base + c) % mod;
    return (int)ans;
}

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "overflow") {
        StringHash big(8);
        string s = "abcdefg";
        pii x = big[s];
        cout << big.modify(x, s, 0, 'z').first << '\n';
        return 0;
    }
    StringHash h(2);
    string s = "ab";
    pii got = h[s];
    if (got.first != expect(s, 1000000007, 127) || got.second != expect(s, 1000000009, 131)) return 1;
    string t = "cb";
    pii changed = h.modify(got, s, 0, 'c');
    if (changed.first != expect(t, 1000000007, 127) || changed.second != expect(t, 1000000009, 131)) return 1;
    pii empty = h[string()];
    cout << got.first << ' ' << got.second << ' ' << empty.first << ' ' << empty.second << '\n';
}
