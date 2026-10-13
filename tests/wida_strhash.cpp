#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_strhash/main.cpp"

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
        String h(1000000007, 127, 8);
        string s = "abcdefg";
        int x = h.get(s);
        cout << h.modify(x, s, 0, 'z') << '\n';
        return 0;
    }
    String h(1000, 10, 4);
    if (h[0] != 1 || h[1] != 10 || h[2] != 100 || h[3] != 0) return 1;
    string s = "ab";
    int got = h[s];
    if (got != expect(s, 1000, 10)) return 1;
    string t = s;
    t[0] = 'c';
    if (h.modify(got, s, 0, 'c') != expect(t, 1000, 10)) return 1;
    t = s;
    t[1] = 'a';
    if (h.modify(got, s, 1, 'a') != expect(t, 1000, 10)) return 1;
    cout << got << ' ' << h.get("") << ' ' << mod << ' ' << base << '\n';
}
